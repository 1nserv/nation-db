import urllib

from flask import Request

from utils.common.commons import *

from utils.functions import auth
from utils.functions import server
from utils.functions import economy

def get_sale(req: Request, id: str):
	if not tn_safe(id):
		server.error(req.remote_addr, "POST", f"/marketplace/sales/{id}", 400, "Invalid Params")
		return {"message": "Invalid Params"}, 400


	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}", 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "marketplace": "---r" }):
			server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}", 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ============ FOUILLE DANS LA DB ============

	data = economy.get_sale(id)

	if not data:
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}", 404, "Not Found")
		return {"message": "Sale Not Found"}, 404

	return data, 200


def cancel_sale(req: Request, id: str):
	payload = req.json

	if not tn_safe(id):
		server.error(req.remote_addr, "POST", f"/marketplace/sales/{id}/cancel", 400, "Invalid Params")
		return {"message": "Invalid Params"}, 400

	if payload.get('reason') and not tn_safe(payload['reason']):
		server.error(req.remote_addr, "POST", f"/marketplace/sales/{id}/cancel", 400, "Invalid Params")
		return {"message": "Invalid Params"}, 400


	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}/cancel", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}/cancel", 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)
	else:
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}/cancel", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ============ FOUILLE DANS LA DB ============

	data = economy.get_sale(id)

	if not data:
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}/cancel", 404, "Not Found")
		return {"message": "Sale Not Found"}, 404

	# ============ TRAITEMENT ============

	if not (auth.check_session(token, { "marketplace": "-m--" }) or data["seller_id"] == session["author"]):
		server.error(req.remote_addr, 'PUT', f"/marketplace/sales/{id}/cancel", 403, "Forbidden")
		return {"message": "Forbidden"}, 403

	economy.delete_sale(id)

	server.log(req.remote_addr, 'PUT', f"/marketplace/sales/{id}/cancel", 200, "Sale Cancelled")
	server.create_archive('marketplace', {
		"action": "CANCEL_SALE",
		"author": session["author"],
		"reason": payload.get('reason', "No reason provided.")
	})

	return {"message": "Sale Successfully Cancelled"}, 200


def search_sales(req: Request):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "POST", f"/fetch/sales", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/fetch/sales', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/fetch/sales', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "marketplace": "---r" }):
			server.error(req.remote_addr, 'GET', f'/fetch/sales', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/fetch/sales', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ---- FOUILLE DANS LA DB ----

	data = economy.fetch_sales(**params)

	res = []

	for sale in data:
		if not sale: continue

		_sale = get_sale(req, sale['id'])

		if _sale[1] == 200:
			res.append(_sale[0])

	server.log(req.remote_addr, 'GET', f'/fetch/sales')
	return res, 200