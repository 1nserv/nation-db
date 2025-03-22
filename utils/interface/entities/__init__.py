import time
import urllib
import urllib.parse

from flask import Request

from utils.common.commons import *

from utils.functions import auth
from utils.functions import entities
from utils.functions import server

from . import positions

def get_entity(req: Request, type: str, id: str):
	if not sql_safe(id):
		server.error(req.remote_addr, 'GET', f'/model/{type}/{id}', 400, "Incorrect ID")
		return {"message": "Bad Request"}, 400

	# ---- FOUILLE DANS LA DB ----

	if id.startswith('o'):
		data = entities.get_organization(id[1:])
		id = id[1:] # Si on garde la lettre il apparaîtra de façon incorrecte dans la console
	elif id.startswith('i'):
		data = entities.get_individual(id[1:])
		id = id[1:] # Même chose + il fonctionnera pas avec get_entity_groups
	else:
		data = entities.get_entity(id)

	if not data:
		server.error(req.remote_addr, 'GET', f'/model/{type}/{id}', 404, "Entity Not Found")
		return {"message": "Entity does not exist"}, 404

	pos = positions.get_position(req, data['position'])
	if pos[1] == 200:
		data['position'] = pos[0]
	else:
		data['position'] = {
			'id': "-",
			"title": "-", 
			"permissions": {},
			"manager_permissions": {}
		}

	if 'xp' in data.keys():
		data['_class'] = "individuals"
	elif 'members' in data.keys():
		data['_class'] = "organizations"

		owner = get_entity(req, 'entities', data['owner_id'])
		if owner[1] == 200:
			data["owner"] = owner[0]
		else:
			server.error(req.remote_addr, "POST", f"/fetch/{type}/", 403, "Unexisting Owner")
			return {"message": "Unexisting Owner"}, 403

		del data['owner_id']

	server.log(req.remote_addr, 'GET', f'/model/{type}/{id}')
	return data, 200

def search_entities(req: Request, type: str):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "POST", f"/fetch/{type}/", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	# ---- FOUILLE DANS LA DB ----

	if type == "organizations":
		data = entities.fetch_organizations(**params)
	elif type == "individuals":
		data = entities.fetch_individuals(**params)
	else:
		data = entities.fetch_entities(**params)

	res = []

	for entity in data:
		if not entity: continue

		_e = get_entity(req, type, entity['id'])

		if _e[1] == 200:
			res.append(_e[0])

	server.log(req.remote_addr, 'GET', f'/fetch/{type}')
	return res, 200

def update_entity(req: Request, _class: str, id: str, action: str):
	def check_params(checklist: list[str], params: dict, ignore_tn: bool = True, ignore_sql: bool = True):
		for name in checklist:
			if name not in params.keys(): return False
			if not (tn_safe(params[name]) or ignore_tn): return False
			if not (sql_safe(params[name]) or ignore_sql): return False

		return True

	if not _class in ["individuals", "organizations"]:
		server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400

	res = get_entity(req, _class, id) # On récupère l'entité et on en profite pour une nouvelle requête en cas d'accès non autorisé

	if res[1] != 200: # Si on n'a pas d'entité aucun intérêt à poursuivre
		return res
	else:
		entity = res[0]

	params = req.args

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	attr = ""

	# =========== PERMISSIONS ============

	session = auth.get_session(token)
	if not session:
		server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if _class == 'individuals' and not auth.check_session(token, { "database": "ame-", "entities": "--e-" }, True):
		server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 403, "Missing Permissions")
		return {"message": "Missing Permissions"}, 403

	old_value = ""

	if action == 'delete':
		# =========== TRAITEMENT ============

		if _class == "individuals":
			res = entities.delete_individual(id)
		else:
			res = entities.delete_organization(id)

		if res[0]:
			return {"message": "Success"}, 200

	elif action == 'rename':
		# ============ PARAMS ============

		if not check_params(['name'], params, ignore_sql = False):
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# =========== TRAITEMENT ============

		attr = "name"
		old_value = entity[attr]

		entity[attr] = params[attr]

	elif action == 'change_position':
		# ============ PARAMS ============

		if not check_params(['position'], params):
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "position"
		old_value = entity[attr]

		entity[attr] = params[attr]

	elif action == 'add_link':
		# ============ PARAMS ============

		if not check_params(['link'], params):
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "additional"
		old_value = entity[attr]

		try:
			if params.get('type') == 'integer':
				val = int(params.get('value', 0))
			elif params.get('type') == 'boolean':
				val = bool(params.get('value', True))
			else:
				val = str(params.get('value', ""))
		except:
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Parameter")
			return {"message": "Invalid Parameter"}, 400

		entity[attr][params['link']] = val

	elif action == 'remove_link':
		# ============ PARAMS ============

		if not check_params(['link'], params):
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		# ============ TRAITEMENT ============

		attr = "additional"
		old_value = entity[attr]

		if params['link'] in entity[attr]:
			del entity[attr][params['link']]

	# ============ UPDATES SPÉCIFIQUES AUX MEMBRES ============

	elif _class == "individuals":
		if action == "add_xp":
			# ============ PARAMS ============

			if not check_params(['amount'], params, ignore_sql = False):
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			# ============ TRAITEMENT ============

			attr = "xp"
			old_value = entity[attr]

			entity[attr] += int(params["amount"])
		elif action == "edit_boost":
			# ============ PARAMS ============

			if not check_params(['boost'], params, ignore_tn = False) or not params["multiplier"].isnumeric():
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			# ============ TRAITEMENT ============

			attr = "boosts"
			old_value = entity[attr]

			multiplier = int(params["multiplier"])

			if multiplier == -1:
				del entity[attr][params["boost"]]
			else:
				entity[attr][params["boost"]] += multiplier
		elif action == "accept_invite":
			# ============ PARAMS ============

			if not check_params(['id'], params, ignore_sql = False):
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			# ============ TRAITEMENT ============

			user = entity.copy() # On garde l'entity de base de côté
			entity = entities.get_organization(params['id']) # L'entreprise est sujette au traitement
			attr = "members"
			old_value = entity[attr]

			invite = entity['invites'].copy().get(user['id'])

			if not invite:
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 404, "User has never been invited")
				return {"message": "User has never been invited"}, 404

			del entity['invites'][user['id']]

			if invite.get('__expires', time.time() + 608400) > time.time(): # Pas de clé __expires => Pas d'expiration
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 404, "Invite expired")
				return {"message": "Invite expired"}, 404

			level = int(invite['level'])

			for member in entity[attr]:
				if member['id'] == user['id']:
					member['teams'][invite['team']] = level
					break
			else:
				entity[attr].append({
					"id": user['id'],
					"teams": {
						invite["team"]: level
					}
				})

				entities.save_organization(entity)

			entity = user.copy() # On remet l'entity de base pour éviter que le code qui suit sauvegarde une entreprise dans les individuels
		else:
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Action")
			return {"message": "Invalid Action"}, 400

	# ============ UPDATES SPÉCIFIQUES AUX GROUPES ============

	elif _class == "organizations":
		if action == "add_certification":
			# ============ PARAMS ============

			if not check_params(['name'], params, ignore_tn = False) or not params["duration"].isnumeric():
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			# ============ TRAITEMENT ============

			attr = "certifications"
			old_value = entity[attr]

			duration = round(time.time()) + int(params["duration"])
			if duration <= 0:
				server.log(req.remote_addr, 'POST', f"/model/{_class}/{id}/{action}", 200)
				return {"message": "Entity Updated"}, 200

			entity[attr][params["name"]] = duration
		elif action == "remove_certification":
			# ============ PARAMS ============

			if not check_params(['name'], params, ignore_tn = False):
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			# ============ TRAITEMENT ============

			attr = "certifications"
			old_value = entity[attr]

			del entity[attr][params["name"]]
		elif action == "invite_user":
			# ============ PARAMS ============

			if not check_params(['id'], params, ignore_sql = False):
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			if 'team' in params.keys() and not check_params(['team'], params, ignore_tn = False):
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Or Missing Parameter")
				return {"message": "Invalid Or Missing Parameter"}, 400

			# ============ TRAITEMENT ============

			attr = "invites"
			old_value = entity[attr]

			user = entities.get_individual(params['id'])

			if not user:
				server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 403, "Can't invite a ghost user")
				return {"message": "Can't invite a ghost user"}, 403

			level = int(params.get('level', 0))

			entity[attr][params['id']] = {
				"__expires": round(time.time() + 608400),
				"team": params.get('team', "general"),
				"level": level
			}
		else:
			server.error(req.remote_addr, "POST", f"/model/{_class}/{id}/{action}", 400, "Invalid Action")
			return {"message": "Invalid Action"}, 400

	# ============ SAUVEGARDE ============

	if _class == "individuals":
		entities.save_individual(entity)
	elif _class == "organizations":
		entities.save_organization(entity)

	# ============ RÉPONSE ============

	server.log(req.remote_addr, 'POST', f"/model/{_class}/{id}/{action}", 200)

	session = auth.get_session(token)

	server.create_archive("entities", {
		"action": "UPDATE_ENTITY",
		"author": session["author"],
		"base": _class,
		"attribute": attr,
		"old_value": old_value,
		"new_value": entity.get(attr, "N/A")
	})

	return {"message": "Entity Updated"}, 200

def create_entity(req: Request, type: str):
	if not req.is_json:
		server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 400, "Bad Request")
		return {"message": "Payload must be a json value"}, 400

	if req.authorization:
		token = req.authorization.token

		if not sql_safe(token): # Pour prévenir les attaques
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if type == "individuals":
			if not auth.check_session(token, {"members": "a---", "database": "-me-"}, at_least_one = True):
				server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 403, "Missing Permissions")
				return {"message": "Forbidden"}, 403
		elif type == "organizations":
			if not auth.check_session(token, {"organizations": "a---", "database": "-me-"}, at_least_one = True):
				server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 403, "Missing Permissions")
	else:
		server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 401, "Missing Token")
		return {"message": "Unauthorized"}, 401

	session = auth.get_session(req.authorization.token)
	author = entities.get_entity(session["author"])

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

	id = params.get("id", hex(int(time.time() * 1000))[2:].upper())

	data = {}
	res: tuple = (False, "Something went wrong")

	if type == "individuals":
		data = {
			"id": id,
			"name": params["name"],
			"position": "member",
			"register_date": int(round(time.time() / 3600) * 3600),
			"xp": 0,
			"boosts": {},
			"additional": {},
			"votes": []
		}

		res = entities.save_individual(data)
	elif type == "organizations":
		if int(id, 16) < 100 and author["position"] not in ("superadmin", "admincouncil", "admin"): # Seul le Conseil d'Administration peut créer une nouvelle institution
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 403, "Missing Permissions")
			return {"message": "Forbidden"}, 403

		if 100 < int(id, 16) < 1000 and author["position"] not in ("superadmin", "admin", "pre_rep"): # Seul le Président de la République peut créer un nouveau ministère
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 403, "Missing Permissions")
			return {"message": "Forbidden"}, 403

		data = {
			"id": id,
			"name": params["name"],
			"position": params.get("position", "group"),
			"register_date": round(time.time()),
			"owner_id": session["author"],
			"members": [],
			"invites": {},
			"certifications": {},
			"additional": {}
		}

		res = entities.save_organization(data)

	if not res[0]:
		if res[1] == "Entity Already Exists":
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 409, "Entity Already Exists")
			return {"message": "Entity Already Exists"}, 409
		else:
			server.error(req.remote_addr, 'PUT', f'/new_model/{type}', 422, "Error In Data")
			return {"message": "Unprocessable Entity"}, 422

	server.log(req.remote_addr, 'PUT', f'/new_model/{type}', 200)
	server.create_archive("entities", {"action": "CREATE_ENTITY", "author": session["author"], "base": type})
	return data, 200