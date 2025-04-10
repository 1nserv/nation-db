import time
import urllib

from flask import Request

from utils.common.commons import *

from utils.functions import auth
from utils.functions import server
from utils.functions import economy


def register_item(req: Request):
	def check_params(checklist: list[str], params: dict, ignore_tn: bool = True, ignore_sql: bool = True):
		for name in checklist:
			if name not in params.keys(): return False
			if not (tn_safe(params[name]) or ignore_tn): return False
			if not (sql_safe(params[name]) or ignore_sql): return False

		return True

	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/marketplace/register_item', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args
	payload = req.json

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "items": "a---" }):
			server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if not check_params(['name'], params, ignore_sql = False):
		server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if 'emoji' in params.keys() and not check_params(['emoji'], params, ignore_sql = False):
		server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if 'categories' in payload.keys():
		for category in payload['categories']:
			if not (isinstance(category, str) and tn_safe(category)):
				server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 400, "Bad Request")
				return {"message": "Bad Request"}, 400

	if 'craft' in payload.keys():
		for item in payload['craft'].keys():
			if not tn_safe(item):
				server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 400, "Bad Request")
				return {"message": "Bad Request"}, 400

			res = economy.get_item(item)

			if not res[0]:
				server.error(req.remote_addr, 'PUT', f'/marketplace/register_item', 404, "Unknown Item In Craft")
				return {"message": "Unknown Item In Craft"}, 404

	# =============================

	session = auth.get_session(token)

	item = {
		"id": hex(round(time.time()))[2:].upper(), # ID de l'item
		"name": params.get("tag", "inconnu"), # Nom de l'item
		"emoji": payload.get("emoji", ":lightbulb:"), # Emoji de l'item
		"categories": payload.get('categories'), # Catégories de l'item
		"craft": payload.get('craft'), # Craft de l'item
	}

	economy.save_item(item, overwrite = False)

	server.log(req.remote_addr, 'PUT', f'/marketplace/register_item', 200)
	server.create_archive("marketplace", {
		"action": "REGISTER_ITEM",
		"author": session["author"],
		"item_id": item["id"],
		"categories": item["categories"],
		"craft": item["craft"]
	})

	return item, 200

def get_item(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'GET', f'/marketplace/get_item/{id}', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/marketplace/get_item/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	item = economy.get_item(id)

	if not item:
		server.error(req.remote_addr, 'GET', f'/marketplace/get_item/{id}', 404, "Item Not Found")
		return {"message": "Item Not Found"}, 404

	return item, 200

def search_items(req: Request):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "POST", f"/fetch/items/", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f"/fetch/items/", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f"/fetch/items/", 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "items": "---r" }):
			server.error(req.remote_addr, 'PUT', f"/fetch/items/", 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f"/fetch/items/", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ---- FOUILLE DANS LA DB ----

	data = economy.fetch_items(**params)

	res = []

	for item in data:
		if not item: continue

		_item = get_item(req, item['id'])

		if item[1] == 200:
			res.append(_item[0])

	server.log(req.remote_addr, 'GET', f'/fetch/items')
	return res, 200

def update_item(req: Request, id: str, action: str):
	def check_params(checklist: list[str], params: dict, ignore_tn: bool = True, ignore_sql: bool = True):
		for name in checklist:
			if name not in params.keys(): return False
			if not (tn_safe(params[name]) or ignore_tn): return False
			if not (sql_safe(params[name]) or ignore_sql): return False

		return True

	res = get_item(req, id) # On récupère l'entité et on en profite pour une nouvelle requête en cas d'accès non autorisé

	if res[1] != 200: # Si on n'a pas d'entité aucun intérêt à poursuivre
		return res
	else:
		item = res[0]

	params = req.args

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	attr = ""

	# =========== PERMISSIONS ============

	session = auth.get_session(token)
	if not session:
		server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if not auth.check_session(token, { "database": "ame-", "items": "-m--" }, True):
		server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 403, "Missing Permissions")
		return {"message": "Missing Permissions"}, 403

	old_value = ""

	if action == 'delete':
		# =========== TRAITEMENT ============

		res = economy.delete_item(id)

		if res[0]:
			return {"message": "Success"}, 200

	elif action == 'rename':
		# ============ PARAMS ============

		if not check_params(['name'], params, ignore_sql = False):
			server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# =========== TRAITEMENT ============

		attr = "name"
		old_value = item[attr]

		item[attr] = params[attr]

	elif action == 'change_emoji':
		# ============ PARAMS ============

		if not check_params(['emoji'], params, ignore_sql = False):
			server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "emoji"
		old_value = item[attr]

		item[attr] = params[attr]

	elif action == 'add_category':
		# ============ PARAMS ============

		if not check_params(['category'], params, ignore_tn = False):
			server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "categories"
		old_value = item[attr]

		if params['category'] not in item[attr]:
			item[attr].append()

	elif action == 'remove_category':
		# ============ PARAMS ============

		if not check_params(['category'], params):
			server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "categories"
		old_value = item[attr]

		if params['category'] in item[attr]:
			item[attr].remove(params['category'])

	elif action == 'edit_craft':
		# ============ PARAMS ============

		for k, v in params['craft'].keys():
			if k == item['id']:
				server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			if not v.isnumeric():
				server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			res = get_item(k)

			if not res[0]:
				server.error(req.remote_addr, "POST", f"/marketplace/items/{id}/{action}", 404, "Unknown Item In Craft")
				return {"message": "Unknown Item In Craft"}, 404

		# ============ TRAITEMENT ============

		attr = "craft"
		old_value = item[attr]

		item[attr] = {}

		for k, v in params['craft'].keys():
			item[attr][k] = int(round(v))

	# ============ SAUVEGARDE ============

	economy.save_item(item)

	# ============ RÉPONSE ============

	server.log(req.remote_addr, 'POST', f"/marketplace/items/{id}/{action}", 200)

	session = auth.get_session(token)

	server.create_archive("economy", {
		"action": "UPDATE_ITEM",
		"author": session["author"],
		"attribute": attr,
		"old_value": old_value,
		"new_value": item.get(attr, "N/A")
	})

	return {"message": "Item Updated"}, 200