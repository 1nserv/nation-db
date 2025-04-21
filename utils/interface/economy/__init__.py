import bcrypt
import time
import urllib

from flask import Request

from utils import db

from utils.common.commons import *

from utils.functions import auth
from utils.functions import server
from utils.functions import economy
from utils.functions import entities


def register_account(req: Request):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/register_account', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/bank/register_account', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f'/bank/register_account', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)

		if not session:
			server.error(req.remote_addr, 'PUT', f'/bank/register_account', 401, "Unauthorized")
			return {"message": "Unauthorized"}, 401

		author = entities.get_entity(session['author'])

		if params.get('owner') and params['owner'] != author['id']:
			if not tn_safe(params['owner']):
				server.error(req.remote_addr, 'PUT', f'/bank/register_account', 400, "Bad Request")
				return {"message": "Bad Request"}, 400

			author = entities.get_entity(params['owner'])

			if not author:
				server.error(req.remote_addr, 'PUT', f'/bank/register_account', 404, "Unexisting Owner")
				return {"message": "Unexisting Owner"}, 404

			if not auth.check_session(token, { "inventories": "am--" }):
				server.error(req.remote_addr, 'PUT', f'/bank/register_account', 403, "Forbidden")
				return {"message": "Forbidden"}, 403
		else:
			if not auth.check_session(token, { "inventories": "a---" }):
				server.error(req.remote_addr, 'PUT', f'/bank/register_account', 403, "Forbidden")
				return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f'/bank/register_account', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	res = economy.get_account(author['id'])

	flagged = False

	if res: # On détermine s'il s'agit de son premier compte
		id: str = hex(round(time.time() * 1000) * 16 ** 3)[2:].upper()
		flagged = True
	else:
		id: str = author['id']

	digicode = gen_digicode(8)

	account = {
		"id": id, # ID du compte
		"tag": params.get("tag", "inconnu"), # Étiquette du compte
		"owner_id": author['id'], # Proprio du compte
		"frozen": flagged, # Si double compte => doit passer par une approbation avant d'être dégelé
		"flagged": flagged, # Suivi du compte
		"register_date": round(time.time()), # Date d'enregistrement
		"amount": 0, # Montant sur le compte
		"income": 0, # Montant accumulé depuis le dernier passage de l'URSSAF
		"bank": "HexaBank", # Banque propriétaire du compte
		"digicode_hash": bcrypt.hashpw(digicode.encode(), db.salt).decode() # Hash du code d'accès
	}

	economy.save_account(account, overwrite = False)

	server.log(req.remote_addr, 'PUT', f'/bank/register_account', 200)
	server.create_archive("bank", {
		"action": "REGISTER_ACCOUNT",
		"author": session["author"],
		"owner": author["id"],
		"account_id": account["id"],
		"tag": account["tag"]
	})

	return {
		"id": account["id"],
		"digicode": digicode
	}, 200

def get_account(req: Request, id: str):
	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/bank/accounts/{id}', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)

		if not session:
			server.error(req.remote_addr, 'GET', f'/bank/accounts/{id}', 401, "Unauthorized")
			return {"message": "Unauthorized"}, 401

		if id != session["author"] and not auth.check_session(token, { "database": "---r", "inventories": "---r" }):
			server.error(req.remote_addr, 'GET', f'/bank/accounts/{id}', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/bank/accounts/{id}', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/bank/accounts/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	account = economy.get_account(id)

	if not account:
		server.error(req.remote_addr, 'GET', f'/bank/accounts/{id}', 404, "Account Not Found")
		return {"message": "Account Not Found"}, 404
	else:
		account = account.copy()
		del account["digicode_hash"]

	return account, 200

def search_accounts(req: Request):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "GET", f"/fetch/accounts/", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'GET', f'/fetch/accounts/', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/fetch/accounts/', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "database": "---r", "inventories": "-m-r" }):
			server.error(req.remote_addr, 'GET', f'/fetch/accounts/', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/fetch/accounts/', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ---- FOUILLE DANS LA DB ----

	data = economy.fetch_accounts(**params)

	res = []

	for acc in data:
		if not acc: continue

		_acc = get_account(req, acc['id'])

		if _acc[1] == 200:
			res.append(_acc[0])

	server.log(req.remote_addr, 'GET', f'/fetch/accounts')
	return res, 200



def freeze_account(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	params = req.args
	payload = req.json

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	account = economy.get_account(id)

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)
		author = entities.get_entity(session["author"])

		if author["id"] != account["owner_id"] and not auth.check_session(token, { "inventories": "--e-" }):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if payload.get("reason") and not sql_safe(payload["reason"]):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if params.get("frozen") and params["frozen"] not in ("true", "false"):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if not account:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 404, "Account Not Found")
		return {"message": "Account Not Found"}, 404

	session = auth.get_session(token)
	account["frozen"] = params.get('frozen', "true") == "true"

	economy.save_account(account)

	server.log(req.remote_addr, 'POST', f'/bank/accounts/{id}/freeze', 200)
	server.create_archive("bank", {"action": "FREEZE_ACCOUNT" if account["frozen"] else "UNFREEZE_ACCOUNT", "author": session["author"], "account_id": account["id"], "reason": req.json["reason"]})
	return {"message": "Success"}, 200

def flag_account(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "inventories": "--e-" }):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if id and not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if req.json.get("reason") and not tn_safe(req.json["reason"]):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if params.get("flagged") and params["flagged"] not in ("true", "false"):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	account = economy.get_account(id)

	if not account:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 404, "Account Not Found")
		return {"message": "Account Not Found"}, 404
	else:
		account = account.copy()

	session = auth.get_session(token)
	account["flagged"] = params.get('flagged', "true") == "true"

	economy.save_account(account)

	server.log(req.remote_addr, 'POST', f'/bank/accounts/{id}/flag', 200)
	server.create_archive("bank", {"action": "FLAG_ACCOUNT" if account["flagged"] else "UNFLAG_ACCOUNT", "author": session["author"], "account_id": account["id"], "reason": req.json["reason"]})
	return account, 200

def debit(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args
	payload = req.json

	is_loan = False
	loan = {}

	if params.get('loan_id'):
		if not tn_safe(params['loan_id']):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		loan = economy.get_loan(params['loan_id'])
		if loan: is_loan = True

		if (
			loan["frozen"] or\
			(0 < loan["expires"] >= round(time.time())) or\
			loan["last"] - round(time.time()) < loan["frequency"] or\
			loan["target"] not in (id, "*")
		):
			is_loan = False

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not (is_loan or auth.check_session(token, { "inventories": "--e-" })):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	session = auth.get_session(token)

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if payload.get("reason") and not sql_safe(payload["reason"]):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if params.get("target"):
		if not tn_safe(params["target"]):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

	account = economy.get_account(id)

	# Check digicode

	if payload.get('digicode'):
		given_digicode = bcrypt.hashpw(payload.get("digicode").encode(), db.salt).decode()
	else:
		given_digicode = None

	if given_digicode != account["digicode_hash"] and not auth.check_session(token, { "inventories": "--e-" }):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 401, "Wrong Digicode")
		return {"message": "Wrong Digicode"}, 401

	# Check si crédit

	try:
		if is_loan:
			if loan["is_percentage"]:
				percentage = abs(int(params["amount"])) / 100
				amount = int(round(account["amount"] * percentage))
			else:
				amount = loan["amount"]
		else:
			amount = abs(int(params["amount"]))
	except:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 400, "Invalid Or Undefined Amount")
		return {"message": "Invalid Or Undefined Amount"}, 400

	# Check compte cible

	if not account:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 404, "Account Not Found")
		return {"message": "Account Not Found"}, 404

	if account["frozen"] and not auth.check_session(token, { "inventories": "-m--" }):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 401, "Account Frozen")
		return {"message": "Account Frozen"}, 401

	# Check compte destinataire

	target = economy.get_account(params.get("target", "6"))

	if not target:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 404, "Target Not Found")
		return {"message": "Target Not Found"}, 404

	if target["frozen"] and not auth.check_session(token, { "inventories": "-m--" }):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 401, "Target Frozen")
		return {"message": "Target Frozen"}, 401

	# Transaction

	if amount > account["amount"] and not (is_loan and loan["tag"] in TAXATIONS.keys()):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 401, "Account Frozen")
		return {"message": "Account Frozen"}, 401

	account["amount"] -= amount

	target["amount"] += amount
	target["income"] += amount

	# Actualisation du crédit si c'en est un

	if is_loan:
		loan["last"] = round(time.time())

	# Sauvegarde des changements

	economy.save_account(account)
	economy.save_account(target)

	server.log(req.remote_addr, 'POST', f'/bank/accounts/{id}/debit', 200)
	server.create_archive("bank", {
		"action": "DEBIT",
		"author": session["author"],
		"account_id": account["id"],
		"target_id": target['id'],
		"reason": payload.get("reason", "No reason provided.")
	})

	return account, 200

def deposit(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	params = req.args
	payload = req.json

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	account = economy.get_account(id)

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)

		if not auth.check_session(token, { "database": '--e-', "money": "a---" }):
			server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if payload.get("reason") and not tn_safe(payload["reason"]):
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	try:
		amount = int(params["amount"])
	except:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Undefined Amount"}, 400

	if not account:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 404, "Account Not Found")
		return {"message": "Account Not Found"}, 404

	if account["frozen"]:
		server.error(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 401, "Account Frozen")
		return {"message": "Account Frozen"}, 401

	account["amount"] += amount
	account["income"] += amount

	session = auth.get_session(token)

	economy.save_account(account)

	server.log(req.remote_addr, 'POST', f'/bank/accounts/{id}/deposit', 200)
	server.create_archive("bank", {
		"action": "DEPOSIT",
		"author": session["author"],
		"account_id": account["id"],
		"amount": params["amount"],
		"reason": payload.get("reason", "No reason provided.")
	})

	return account, 200