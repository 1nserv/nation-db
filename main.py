import time

from flask import Flask, request

from utils.interface import auth
from utils.interface import drive as drive_interface

from utils.interface import economy
from utils.interface.economy import inventories
from utils.interface.economy import items
from utils.interface.economy import loans
from utils.interface.economy import sales

from utils.interface import entities
from utils.interface.entities import positions

from utils.common import database, commons, drive
from utils.common.commons import *

from utils.functions import server
from utils.functions import entities as ef

app = Flask(__name__)

@app.get('/ping')
def ping():
	status = {
		'auth': None,
		'economy': None, 
		'entities': None,
		'republic': None,
		'server': None, 
		'drive': None
	}

	try:
		start = time.time()

		for _ in range(10):
			database.fetch('auth.Sessions')
			database.fetch('auth.Accounts')

		status['auth'] = int((time.time() - start) * 1000 / 10)
	except:
		pass

	try:
		start = time.time()

		for _ in range(10):
			database.fetch('entities.Positions')
			database.fetch('entities.Individuals')
			database.fetch('entities.Organizations')

		status['entities'] = int((time.time() - start) * 1000 / 10)
	except:
		pass

	try:
		start = time.time()

		for _ in range(10):
			database.fetch('marketplace.Banks')
			database.fetch('marketplace.Accounts')
			database.fetch('marketplace.Loans')
			database.fetch('marketplace.Items')
			database.fetch('marketplace.Sales')
			database.fetch('marketplace.Inventories')

		status['economy'] = int((time.time() - start) * 1000 / 10)
	except:
		pass

	try:
		start = time.time()

		for _ in range(10):
			database.fetch('republic.Elections')
			database.fetch('republic.Votes')

		status['republic'] = int((time.time() - start) * 1000 / 10)
	except:
		pass

	try:
		start = time.time()

		server.log("@", 'PING', '/ping', 200, "Pong !")
		server.error("@", 'PING', '/ping', 500, "Pong !")
		server.create_archive('admin', {
			"REQUEST": "PING"
		})

		status['server'] = int((time.time() - start) * 1000 / 10)
	except:
		pass

	try:
		start = time.time()

		for _ in range(10):
			drive.register_file('files', 'ping', b'', True)
			drive.open_file('/files/ping')

		status['drive'] = int((time.time() - start) * 1000 / 10)
	except:
		pass

	if None in status.values():
		for res_time in status.values():
			if isinstance(res_time, int):
				_global = 'partial_outage'
				code = 206
				break
		else:
			_global = 'service_unavailable'
			code = 503
	else:
		_global = 'ok'
		code = 200

	return {
		'_version': 300,
		'global': _global,
		'status': status
	}, code

@app.post('/auth/login')
def login():
	return auth.ask_token(request)

@app.put('/upload/<string:domain>/<string:bucket>')
def upload(domain: str, bucket: str):
	if not (tn_safe(domain) and tn_safe(bucket)):
		server.error(request.remote_addr, 'PUT', '/upload', 400, "Invalid Identifier")
		return {"message": "Bad Request"}, 400

	# Entités
	if domain == "entities":
		return drive_interface.upload_avatar(request)

	# Si ça correspond à rien
	else:
		server.error(request.remote_addr, 'PUT', '/upload', 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400

@app.get('/drive/<string:domain>/<string:bucket>/<path:path>')
def download(domain: str, bucket:str, path: str):
	if not (tn_safe(domain) and tn_safe(bucket)):
		server.error(request.remote_addr, 'GET', '/drive', 400, "Invalid Identifier")
		return {"message": "Bad Request"}, 400

	# Entités
	if domain == "entities":
		return (request)

	# Si ça correspond à rien
	else:
		return {"message": "Invalid Data Class"}, 400

@app.get('/fetch/<string:_class>')
def fetch(_class: str):
	if not tn_safe(_class):
		server.error(request.remote_addr, 'GET', '/model', 400, "Invalid Identifier")
		return {"message": "Bad Request"}, 400

	# Entités
	elif _class == 'entities':
		return entities.search_entities(request, 'entities')
	elif _class == 'individuals':
		return entities.search_entities(request, 'individuals')
	elif _class == 'organizations':
		return entities.search_entities(request, 'organizations')
	elif _class == 'positions':
		return entities.search_positions(request)

	# Économie
	elif _class == 'accounts':
		return economy.search_accounts(request)
	elif _class == 'inventories':
		return inventories.search_inventories(request), 200
	elif _class == 'loans':
		return loans.search_loans(request), 200
	elif _class == 'sales':
		return [], 503
	elif _class == 'items':
		return items.search_items(request)

	# République
	elif _class == 'votes':
		return [], 503
	elif _class == 'elections':
		return [], 503
	elif _class == 'parties':
		return [], 503

	# Si la classe ne correspond à rien
	else:
		server.error(request.remote_addr, 'GET', '/model', 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400


# ---------- ENTITÉS ----------

@app.get('/model/<string:_class>/<string:id>')
def get_model(_class: str, id: str):
	if not (sql_safe(id) and tn_safe(_class)):
		server.error(request.remote_addr, 'GET', f"/model/organizations/{id}/avatar", 400, "Invalid Identifier")
		return {"message": "Bad Request"}, 400

	# Entités
	elif _class == 'entities':
		return entities.get_entity(request, 'entities', id)
	elif _class == 'individuals':
		return entities.get_entity(request, 'individuals', 'i' + id)
	elif _class == 'organizations':
		return entities.get_entity(request, 'organizations', 'o' + id)
	elif _class == 'positions':
		return entities.get_position(request, id)

	# Si la classe ne correspond à rien
	else:
		server.error(request.remote_addr, 'GET', f"/model/{_class}/{id}", 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400

@app.get('/model/organizations/<string:id>/avatar')
def get_avatar(id: str):
	if not (tn_safe(id)):
		server.error(request.remote_addr, 'GET', f"/model/organizations/{id}/avatar", 400, "Invalid Data Class Or Identifier")
		return {"message": "Bad Request"}, 400

	return drive_interface.download_avatar(request, id)

@app.post('/model/<string:_class>/<string:id>/<string:action>')
def update_model(_class: str, id: str, action: str):
	if not (tn_safe(id) and tn_safe(_class)):
		server.error(request.remote_addr, 'POST', f"/model/{_class}/{id}/{action}", 400, "Invalid Data Class Or Identifier")
		return {"message": "Bad Request"}, 400

	if _class == "individuals":
		return entities.update_entity(request, _class, id, action)
	elif _class == "organizations":
		return entities.update_entity(request, _class, id, action)

	# Si ça correspond à rien
	else:
		server.error(request.remote_addr, 'POST', f"/model/{_class}/{id}/{action}", 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400

@app.get('/model/<string:_class>/<string:id>/<string:attribute>')
def get_model_attribute(_class: str, id: str, attribute: str):
	if not (tn_safe(id) and tn_safe(_class)):
		server.error(request.remote_addr, 'POST', f"/model/{_class}/{id}/{attribute}", 400, "Invalid Data Class Or Identifier")
		return {"message": "Bad Request"}, 400

	if _class == "individuals":
		if attribute == "groups":
			res = []
			groups = ef.get_entity_groups(id)

			for grp in groups:
				query = entities.get_entity(request, "organizations", grp["id"]) # La réponse est déjà au complet mais on prévient toute sorte de bypass

				if query[1] == 200:
					res.append(query[0])
				else:
					return query

			return res, 200

	# Si ça correspond à rien
	else:
		server.error(request.remote_addr, 'POST', f"/model/{_class}/{id}/{attribute}", 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400

@app.put('/new_model/<string:_class>')
def create_model(_class: str):
	# Entités
	if _class == 'individuals':
		return entities.create_entity(request, 'individuals')
	elif _class == 'organizations':
		return entities.create_entity(request, 'organizations')

	# Si ça correspond à rien
	else:
		server.error(request.remote_addr, 'PUT', '/new_model', 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400


# ---------- BANQUE ----------

@app.put("/bank/register_account")
def open_bank_account():
	return economy.register_account(request)

@app.get("/bank/accounts/<string:id>")
def get_bank_account(id: str):
	return economy.get_account(request, id)

@app.post("/bank/accounts/<string:id>/<string:action>")
def edit_bank_account(id: str, action: str):
	if action == 'freeze':
		return economy.freeze_account(request, id)
	elif action == 'flag':
		return economy.flag_account(request, id)
	elif action == 'debit':
		return economy.debit(request, id)
	elif action == 'deposit':
		return economy.deposit(request, id)

	else:
		server.error(request.remote_addr, 'POST', f'/bank/accounts/{id}/{action}', 400, "Invalid Action")
		return {"message": "Invalid Action"}, 400

# BANQUE => Inventaires

@app.put("/bank/register_inventory")
def register_inventory():
	return inventories.register_inventory(request)

@app.get("/bank/inventories/<string:id>")
def get_inventory(id: str):
	return inventories.get_inventory(request, id)

@app.post("/bank/inventories/<string:id>/<string:action>")
def edit_inventory(id: str, action: str):
	if action == 'deposit':
		return inventories.deposit_item(request, id)
	if action == 'sell_item':
		return inventories.sell_item(request, id)

	else:
		server.error(request.remote_addr, 'POST', f'/bank/inventories/{id}/{action}', 400, "Invalid Action")
		return {"message": "Invalid Action"}, 400

# ---------- MARCHÉ ----------
# MARCHÉ => Items

@app.put("/marketplace/register_item")
def register_marketplace_item():
	return items.register_item(request)

@app.get("/marketplace/items/<string:id>")
def get_marketplace_item(id: str):
	return items.get_item(request, id)

@app.post("/marketplace/items/<string:id>/<string:action>")
def edit_item(id: str, action: str):
	return items.update_item(request, id, action)

# MARCHÉ => Ventes

@app.get("/marketplace/sales/<string:id>")
def get_sale(id: str):
	return sales.get_sale(request, id)

@app.post("/marketplace/sales/<string:id>/cancel")
def cancel_sale(id: str):
	return sales.cancel_sale(request, id)