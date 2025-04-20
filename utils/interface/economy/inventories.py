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


def register_inventory(req: Request):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/register_inventory', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	params = req.args

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)
		author = entities.get_entity(session['author'])

		if params.get('owner') and params['owner'] != author['id']:
			if not tn_safe(params['owner']):
				server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 400, "Bad Request")
				return {"message": "Bad Request"}, 400

			author = entities.get_entity(params['owner'])

			if not author:
				server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 404, "Unexisting Owner")
				return {"message": "Unexisting Owner"}, 404

			if not auth.check_session(token, { "inventories": "am--" }):
				server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 403, "Forbidden")
				return {"message": "Forbidden"}, 403
		else:
			if not auth.check_session(token, { "inventories": "a---" }):
				server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 403, "Forbidden")
				return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if params.get('tag') and not tn_safe(params['tag']):
		server.error(req.remote_addr, 'PUT', f'/bank/register_inventory', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	# =============================


	res = economy.get_inventory(author['id'])

	if res: # On détermine s'il s'agit de son premier compte
		id: str = hex(round(time.time() * 1000) * 16 ** 3)[2:].upper()
	else:
		id: str = author['id']

	digicode = gen_digicode(8)

	inventory = {
		"id": id, # ID de l'inventaire
		"tag": params.get("tag", "inconnu"), # Étiquette de l'inventaire
		"owner_id": author['id'], # Proprio de l'inventaire
		"register_date": round(time.time()), # Date d'enregistrement
		"items": {}, # Items présents dans l'inventaire
		"digicode_hash": bcrypt.hashpw(digicode.encode(), db.salt).decode() # Hash du code d'accès
	}

	economy.save_inventory(inventory, overwrite = False)

	server.log(req.remote_addr, 'PUT', f'/bank/register_inventory', 200)
	server.create_archive("bank", {
		"action": "REGISTER_INVENTORY",
		"author": session["author"],
		"inventory_id": inventory["id"],
		"tag": inventory["tag"]
	})

	return {
		"id": inventory["id"],
		"digicode": digicode
	}, 200

def get_inventory(req: Request, id: str):
	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/bank/inventories/{id}', 400, "Invalid Token")
			return {"message": "Bad Request"}, 400

		session = auth.get_session(token)

		if id != session["author"] and not auth.check_session(token, { "database": "---r", "inventories": "---r" }):
			server.error(req.remote_addr, 'GET', f'/bank/inventories/{id}', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/bank/inventories/{id}', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/bank/inventories/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	inventory = economy.get_inventory(id)

	if not inventory:
		server.error(req.remote_addr, 'GET', f'/bank/inventories/{id}', 404, "Inventory Not Found")
		return {"message": "Inventory Not Found"}, 404
	else:
		inventory = inventory.copy()
		del inventory["digicode_hash"]

	return inventory, 200

def search_inventories(req: Request):
	params = req.args

	for k, v in params.items():
		if not (tn_safe(k) and sql_safe(v)):
			server.error(req.remote_addr, "GET", f"/fetch/inventories", 400, "Invalid Params")
			return {"message": "Invalid Params"}, 400

		v = urllib.parse.unquote(v)

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'GET', f'/fetch/inventories', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'GET', f'/fetch/inventories', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "database": "---r", "inventories": "-m-r" }):
			server.error(req.remote_addr, 'GET', f'/fetch/inventories', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'GET', f'/fetch/inventories', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	# ---- FOUILLE DANS LA DB ----

	data = economy.fetch_inventories(**params)

	res = []

	for inventory in data:
		if not inventory: continue

		_acc = get_inventory(req, inventory['id'])

		if _acc[1] == 200:
			res.append(inventory[0])

	server.log(req.remote_addr, 'GET', f'/fetch/inventories')
	return res, 200



def deposit_item(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args
	payload = req.json

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Bad Request")
			return {"message": "Bad Request"}, 400
	else:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	session = auth.get_session(token)

	# =============================

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	if payload.get("reason"):
		if not sql_safe(payload["reason"]):
			server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

	if params.get("item"):
		if not tn_safe(params["item"]):
			server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

		item = params["item"]

	if payload.get("giver"):
		if not tn_safe(params["giver"]):
			server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter"}, 400

	inventory = economy.get_inventory(id)
	_account = economy.get_account(id) # Pour interdire toute transaction si le compte lié est gelé

	if not _account: _account = { "frozen": False } # Laisser passer la transaction si aucun compte (et donc aucun gel) n'est associé à l'inventaire

	# On détermine le montant

	try:
		amount = abs(int(params["amount"]))
	except:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 400, "Invalid Or Undefined Amount")
		return {"message": "Invalid Or Undefined Amount"}, 400

	# Check inventaire cible

	if not inventory:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 404, "Inventory Not Found")
		return {"message": "Inventory Not Found"}, 404

	if _account["frozen"] and not auth.check_session(token, { "inventories": "-m--" }):
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 401, "Account Frozen")
		return {"message": "Account Frozen"}, 401

	# Check inventaire destinataire

	if payload.get('giver'):
		giver = economy.get_inventory(payload.get('giver', session['author']))
		_giver_account = economy.get_account(payload.get('giver', session['author']))
	else:
		giver = economy.get_inventory(session['author'])
		_giver_account = economy.get_account(session['author'])

	if not _giver_account: _giver_account = { "frozen": False }

	if not giver:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 404, "Giver Not Found")
		return {"message": "Giver Not Found"}, 404

	# Check digicode

	if (not payload.get('digicode')) or bcrypt.hashpw(payload.get("digicode").encode(), db.salt).decode() != giver["digicode_hash"]\
	and not auth.check_session(token, { "inventories": "--e-" }):
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 401, "Wrong Digicode")
		return {"message": "Wrong Digicode"}, 401

	if _giver_account["frozen"] and not auth.check_session(token, { "inventories": "-m--" }):
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 401, "Giver Frozen")
		return {"message": "Giver Frozen"}, 401

	# Transaction

	if item not in giver['items'].keys() or amount > giver['items'][item]:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 401, "Giver Frozen")
		return {"message": "Giver Frozen"}, 401

	giver['items'][item] -= amount
	inventory['items'][item] += amount

	# Sauvegarde des changements

	economy.save_inventory(inventory)
	economy.save_inventory(giver)

	server.log(req.remote_addr, 'POST', f'/bank/inventories/{id}/deposit_item', 200)
	server.create_archive("bank", {
		"action": "deposit_item",
		"author": session["author"],
		"inventory_id": inventory["id"],
		"giver_id": giver['id'],
		"reason": payload.get("reason", "No reason provided.")
	})

	res = inventory.copy()
	del res['digicode_hash']

	return res, 200

def sell_item(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	params = req.args
	payload = req.json

	if token:
		if not sql_safe(token):
			server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not auth.check_session(token, { "marketplace": "a---" }):
			server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 403, "Forbidden")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 401, "Unauthorized")
		return {"message": "Unauthorized"}, 401

	session = auth.get_session(token)

	# ============ TRAITEMENT ============

	# Check params

	if not tn_safe(params['item']):
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	try:
		quantity = int(params['quantity'])
	except:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	try:
		price = int(params['price'])
	except:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	inventory = economy.get_inventory(id)
	account = economy.get_account(id)

	if not inventory:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 401, "No Inventory")
		return {"message": "No Inventory"}, 401

	if not account:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 401, "No Bank Account")
		return {"message": "No Bank Account"}, 401

	# Check du digicode

	if (not payload.get('digicode')) or bcrypt.hashpw(payload.get("digicode").encode(), db.salt).decode() != inventory["digicode_hash"]:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 401, "Wrong Digicode")
		return {"message": "Wrong Digicode"}, 401

	if account["frozen"]:
		server.error(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 401, "Seller Account Is Frozen")
		return {"message": "Seller Account Is Frozen"}, 401

	# Initialisation de la vente

	data = {
		'id': hex(int(time.time() * 1000))[2:].upper(),
		'open': True,
		'seller_id': session['author'],
		'item_id': params['item'],
		'quantity': quantity,
		'price': price
	}

	economy.save_sale(data)

	server.log(req.remote_addr, 'POST', f'/bank/inventories/{id}/sell_item', 200)
	server.create_archive('marketplace', {
		'action': "SELL_ITEM",
		'sale_id': data['id'],
		'author': session['author'],
		'item_id': params['item'],
		'quantity': quantity,
		'price': price
	})

	return { 'sale_id': data['id'] }, 200