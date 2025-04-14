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


def register_loan(req: Request):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/register_loan', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "bank_accounts": "-m--", "loans": "a---" }):
			server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if params.get('tag') and not tn_safe(params['tag']):
		server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if not (params.get('target') and tn_safe(params['target'])):
		server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	# =============================

	session = auth.get_session(token)
	author = economy.get_account(session['author'])
	target = economy.get_account(params['target'])

	id = hex(round(time.time()))[2:].upper()

	try:
		__expires = int(params['__expires'])

		if __expires < time.time():
			__expires = round(time.time()) + 3600
	except:
		__expires = round(time.time()) + 3600

	is_percentage = params.get('type') == "percentage"

	try:
		amount = int(params['amount'])

		if amount < 0:
			amount = 0

		if is_percentage and not 0 <= amount <= 100:
			server.error(req.remote_addr, 'PUT', f'/bank/register_loan', 400, "Invalid Percentage Value")
			return {"message": "Invalid Percentage Value"}, 400
	except:
		amount = 0

	loan = {
		"id": id, # ID de la facturation
		"author_id": author['id'], # NSID du compte de l'auteur
		"target_id": target['id'], # NSID du compte cible
		"tag": params.get("tag", "inconnu"), # Motif de la facturation
		"frozen": False,
		"register_date": round(time.time()), # Date d'enregistrement
		"expires": __expires, # Date d'expiration
		"amount": amount, # Montant prélevé à chaque occurence
		"is_percentage": "percentage" in params.keys(), # Pourcentage à prélever
		"bank": "HexaBank", # Banque propriétaire du compte
	}

	economy.save_loan(loan, overwrite = False)

	server.log(req.remote_addr, 'PUT', f'/bank/register_loan', 200)
	server.create_archive("bank", {
		"action": "REGISTER_LOAN",
		"author": session["author"],
		"loan_id": loan["id"],
		"tag": loan["tag"]
	})

	return loan, 200

def get_loan(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'GET', f'/bank/loans/{id}', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/bank/loans/{id}', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)

		if id != session["author"] and not auth.check_session(token, { "bank_accounts": "---r", "loans": "---r" }):
			server.error(req.remote_addr, 'GET', f'/bank/loans/{id}', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/bank/loans/{id}', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/bank/loans/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	loan = economy.get_loan(id)

	if not loan:
		server.error(req.remote_addr, 'GET', f'/bank/loans/{id}', 404, "Loan Not Found")
		return {"message": "Loan Not Found"}, 404

	return loan, 200

def search_loans(req: Request):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "POST", f"/fetch/loans", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/fetch/loans', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/fetch/loans', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "bank_accounts": "-m-r", "loans": "---r" }):
			server.error(req.remote_addr, 'GET', f'/fetch/loans', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/fetch/loans', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ---- FOUILLE DANS LA DB ----

	data = economy.fetch_loans(**params)

	res = []

	for loan in data:
		if not loan: continue

		_loan = get_loan(req, loan['id'])

		if _loan[1] == 200:
			res.append(_loan[0])

	server.log(req.remote_addr, 'GET', f'/fetch/loans')
	return res, 200



def freeze_loan(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	params = req.args
	payload = req.json

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	loan = economy.get_loan(id)

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)
		author = entities.get_entity(session["author"])

		if author["id"] != loan["owner_id"] and not auth.check_session(token, { "loans": "--e-" }):
			server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	if payload.get("reason") and not sql_safe(payload["reason"]):
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if params.get("frozen") and params["frozen"] not in ("true", "false"):
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if not loan:
		server.error(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 404, "Loan Not Found")
		return {"message": "Loan Not Found"}, 404


	session = auth.get_session(token)
	loan["frozen"] = params.get('frozen', "true") == "true"

	economy.save_loan(loan)

	server.log(req.remote_addr, 'POST', f'/bank/loans/{id}/freeze', 200)
	server.create_archive("bank", {
		"action": "FREEZE_LOAN" if loan["frozen"] else "UNFREEZE_LOAN",
		"author": session["author"],
		"account_id": loan["id"], 
		"reason": req.json["reason"]
	})

	return {"message": "Success"}, 200