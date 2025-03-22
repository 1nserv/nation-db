import urllib
import urllib.parse

from flask import Request

from utils.common.commons import *

from utils.functions import auth
from utils.functions import entities
from utils.functions import server

def get_position(req: Request, id: str, tree: tuple = ()):
	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/model/positions/{id}', 400, "Incorrect ID")
		return {"message": "Bad Request"}, 400

	# ---- SÉCURITÉ ----

	for elem in tree:
		if not tn_safe(elem):
			server.error(req.remote_addr, 'GET', f'/model/positions/{id}', 400, "Invalid Param")
			return {"message": "Invalid Param"}, 400

		if id == elem:
			server.error(req.remote_addr, 'GET', f'/model/positions/{id}', 508, "Loop Detected")
			return {"message": "Loop Detected"}, 508

	# ---- FOUILLE DANS LA DB ----

	data = entities.get_position(id)

	if not data:
		server.error(req.remote_addr, 'GET', f'/model/positions/{id}', 404, "Position Not Found")
		return {"message": "Position does not exist"}, 404

	pos = data.copy()

	if pos['category']:
		res = get_position(req, pos['category'], tree + (id,))

		if res[1] == 200:
			parent = res[0]

			pos["permissions"] = merge_permissions(pos["permissions"], parent["permissions"])
			pos["manager_permissions"] = merge_permissions(pos["manager_permissions"], parent["manager_permissions"])

	server.log(req.remote_addr, 'GET', f'/model/positions/{id}')
	return pos, 200

def search_positions(req: Request):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "POST", f"/fetch/positions/", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	# ---- FOUILLE DANS LA DB ----

	data = entities.fetch_positions(**params)

	if data is None:
		raise ValueError("Fetch returned None instead of an empty list")

	res = []

	for e in data:
		res.append(e)

	server.log(req.remote_addr, 'GET', f'/fetch/positions')
	return res, 200

def update_position(req: Request, id: str, action: str):
	def check_params(checklist: list[str], params: dict, ignore_tn: bool = True, ignore_sql: bool = True):
		for name in checklist:
			if name not in params.keys(): return False
			if not (tn_safe(params[name]) or ignore_tn): return False
			if not (sql_safe(params[name]) or ignore_sql): return False

		return True

	def perm_safe(perm: str) -> bool:
		for i in range(len(perm)):
			if perm[i] not in ("amer"[i], '-'):
				return False

		return len(perm) == 4

	res = get_position(req, id) # On récupère l'entité et on en profite pour une nouvelle requête en cas d'accès non autorisé

	if res[1] != 200: # Si on n'a pas d'entité aucun intérêt à poursuivre
		return res
	else:
		pos = res[0]

	params = req.args

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, "POST", f"/model/positions/{id}/{action}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	attr = ""

	# =========== PERMISSIONS ============

	session = auth.get_session(token)
	if not session:
		server.error(req.remote_addr, "POST", f"/model/positions/{id}/{action}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	required_perms = merge_permissions(pos["manager_permissions"], {"database", "ame-"})

	if not auth.check_session(token, required_perms, at_least_one = True):
		server.error(req.remote_addr, "POST", f"/model/positions/{id}/{action}", 403, "Missing Permissions")
		return {"message": "Missing Permissions"}, 403

	if action == 'rename':
		# ============ PARAMS ============

		if not check_params(['name'], params, ignore_sql = False):
			server.error(req.remote_addr, "POST", f"/model/positions/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# =========== TRAITEMENT ============

		attr = "name"
		old_value = pos[attr]

		pos[attr] = params[attr]

	elif action == 'update_permissions':
		# ============ PARAMS ============

		attr = "permissions"
		old_value = pos[attr]

		for k, v in params.items():
			if k in pos[attr].keys() and perm_safe(v):
				pos[attr][k] = v

	elif action == 'update_manager_permissions':
		# ============ PARAMS ============

		if not check_params(['permissions'], params, ignore_tn = False):
			server.error(req.remote_addr, "POST", f"/model/positions/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "manager_permissions"
		old_value = pos[attr]

		for k, v in params.items():
			if k in pos[attr].keys() and perm_safe(v):
				pos[attr][k] = v

	# ============ SAUVEGARDE ============

	entities.save_position(pos)

	# ============ RÉPONSE ============

	server.log(req.remote_addr, 'POST', f"/model/position/{id}/{action}", 200)

	session = auth.get_session(token)

	server.create_archive("entities", {
		"action": "UPDATE_POSITION",
		"author": session["author"],
		"attribute": attr,
		"old_value": old_value,
		"new_value": pos.get(attr, "N/A")
	})

	return {"message": "Position Updated"}, 200

def register_position(req: Request):
	if not req.is_json:
		server.error(req.remote_addr, 'PUT', f'/new_model/positions', 400, "Bad Request")
		return {"message": "Payload must be a json value"}, 400

	if req.authorization:
		token = req.authorization.token

		if not sql_safe(token): # Pour prévenir les attaques
			server.error(req.remote_addr, 'PUT', f'/new_model/positions', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, {"database": "-me-"}, at_least_one = True):
			server.error(req.remote_addr, 'PUT', f'/new_model/positions', 403, "Missing Permissions")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f'/new_model/positions', 401, "Missing Token")
		return {"message": "Unauthorized"}, 401

	session = auth.get_session(req.authorization.token)

	params = req.args

	if 'name' not in params.keys():
		server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 400, "Missing Name Or ID")
		return {"message": "A name must be defined"}, 400

	if "id" in params.keys() and not sql_safe(params["id"]): # On détecte les menaces dans l'entrée utilisateur
		server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 401, "Bad Request")
		return {"message": "Bad Request"}, 400

	if not sql_safe(params["name"]): # Pareil
		server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 401, "Bad Request")
		return {"message": "Bad Request"}, 400

	id = params.get("id", params["name"].split(" ")[0].lower())

	# reference = get_position(req, "member")
	# data = reference.copy()

	data = {}

	res: tuple = (False, "Something went wrong")

	data["id"] = id
	data["name"] = params["name"]

	res = entities.save_position(data, False)

	if not res[0]:
		if res[1] == "Position Already Exists":
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 409, "Entity Already Exists")
			return {"message": "Position Already Exists"}, 409
		else:
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 422, "Error In Data")
			return {"message": "Unprocessable Entity"}, 422

	server.log(req.remote_addr, 'PUT', f'/new_model/{type}', 200)
	server.create_archive("entities", {"action": "REGISTER_POSITION", "author": session["author"], "base": "positions"})
	return data, 200