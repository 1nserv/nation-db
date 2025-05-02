import hashlib
import random
import requests
import time

from flask import Request, redirect

from utils.common.commons import *
from utils.functions import auth
from utils.functions import server
from utils.functions import entities

def ask_token(req: Request):
	payload = req.json

	if 'username' not in payload.keys() or 'password' not in payload.keys():
		server.error(req.remote_addr, 'POST', '/auth/login', 401, "Missing Credentials")
		return {"message": "Missing Credentials"}, 401

	if not(sql_safe(payload["username"]) and sql_safe(payload["password"])): # On détecte les menaces dans l'entrée utilisateur
		return {"message": "Incorrect Credentials"}, 401

	acc = auth.get_account(payload['username'])

	if not acc:
		server.error(req.remote_addr, 'POST', '/auth/login', 401, "Account Does Not Exist")
		return {"message": "Incorrect Credentials"}, 401

	if acc['pwd'] == hashlib.sha256(payload['password'].encode()).hexdigest():
		charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$."
		token = ''.join([ charset[random.randint(0, 63)] for _ in range(256) ])

		auth.save_session({
			"id": round(time.time()) * random.randint(0, 256),
			"token": token,
			"author": acc["author_id"],
			"provider": "password"
		})

		server.log(req.remote_addr,  'POST','/auth/login')
		server.create_archive("auth", {"action": "GENERATE_TOKEN", "ip_addr": req.remote_addr, "author": acc["author_id"]})
		return {"token": token}, 200
	else:
		server.error(req.remote_addr, 'POST', '/auth/login', 401, "Incorrect Password")
		return {"message": "Incorrect Credentials"}, 401


def oauth_login(req: Request):
	params = req.args

	if 'authCode' not in params.keys():
		server.error(req.remote_addr, 'POST', '/auth/login/', 401, "Missing Credentials")
		return {"message": "Missing Credentials"}, 401

	if tn_safe(params["authCode"]): # On détecte les menaces dans l'entrée utilisateur
		return {"message": "Incorrect Credentials"}, 401

	acc = auth.get_oauth(params['authCode'])

	if not acc:
		server.error(req.remote_addr, 'POST', '/auth/login', 401, "OAuth Token Does Not Exist")
		return {"message": "Incorrect Credentials"}, 401

	charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$."
	token = ''.join([ charset[random.randint(0, 63)] for _ in range(256) ])

	auth.save_session({
		"id": round(time.time()) * random.randint(0, 256),
		"token": token,
		"author": acc["author_id"],
		"provider": "discord"
	})

	server.log(req.remote_addr,  'POST','/auth/login')
	server.create_archive("auth", {
		"action": "GENERATE_TOKEN",
		"ip_addr": req.remote_addr,
		"author": acc["author_id"]
	})

	return {"token": token}, 200


def discord_callback(req: Request):
	params = req.args

	code = params.get('code')
	authCode = params.get('state')

	if not sql_safe(code) or not tn_safe(authCode):
		server.error(req.remote_addr, 'POST', '/auth/login/', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	data = {
		'client_id': os.getenv('DISCORD_CLIENT_ID'),
		'client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': os.getenv('DISCORD_REDIRECT_URI'),
	}

	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	token_res = requests.post('https://discord.com/api/oauth2/token', data = data, headers = headers)
	token = token_res.json().get('access_token')

	res = requests.get(
		'https://discord.com/api/users/@me',
		headers = {'Authorization': f'Bearer {token}'}
	)

	discord_user = res.json()

	# ---- RETOUR VERS NATION

	discord_id = int(discord_user['id'])
	id = hex(discord_id)[2:].upper()

	user = entities.get_individual(id)

	if not user:
		user = {
			'id': id,
			'name': discord_user['username'],
			'position': 'member',
			'register_date': round(time.time()),
			'xp': 0,
			'boosts': {},
			'additional': {},
			'votes': []
		}

		entities.save_individual(user)

	# ---- ENREGISTREMENT DE LA SESSION ----

	OAuth_acc = auth.get_oauth(authCode)

	if not OAuth_acc:
		auth.save_oauth({
			"auth_code": hashlib.sha256(authCode.encode()).hexdigest(),
			"provider": "discord",
			"profile_id": discord_user["id"],
			"author_id": id,
		})

	profile = entities.get_individual(id)

	server.log(req.remote_addr,  'POST','/auth/login')
	server.create_archive("auth", {
		"action": "GENERATE_TOKEN",
		"ip_addr": req.remote_addr,
		"author": discord_user["id"],
		"medium": "discord"
	})

	with open('./utils/pages/loggedin.html', 'r', encoding = 'UTF-8') as f:
		page = f.read()
		page = page.replace('{{name}}', profile["name"])
		page = page.replace('{{id}}', profile["id"])
		page = page.replace('{{authCode}}', authCode)

	return page, 200