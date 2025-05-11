import hashlib
import random
import time

from flask import Request

from utils.common.commons import *
from utils.functions import auth
from utils.functions import server

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
			"id": hex(round(time.time()) * random.randint(0, 256))[2:].upper(),
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