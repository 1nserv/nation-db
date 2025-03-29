from flask import Flask, request

from utils.interface.auth import *
from utils.interface.drive import *

from utils.interface.economy import *
from utils.interface.economy.inventories import *
from utils.interface.economy.items import *
from utils.interface.economy.loans import *

from utils.interface.entities import *
from utils.interface.entities.positions import *

from utils.common import database, drive

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
	return ask_token(request)

@app.put('/upload/<string:domain>/<string:bucket>')
def upload(domain: str, bucket: str):
	if not (tn_safe(domain) and tn_safe(bucket)):
		server.error(request.remote_addr, 'PUT', '/upload', 400, "Invalid Identifier")
		return {"message": "Bad Request"}, 400

	# Entités
	if domain == "entities":
		return upload_avatar(request)

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
		return search_entities(request, 'entities')
	elif _class == 'individuals':
		return search_entities(request, 'individuals')
	elif _class == 'organizations':
		return search_entities(request, 'organizations')
	elif _class == 'positions':
		return search_positions(request)

	# Économie
	elif _class == 'accounts':
		return search_accounts(request)
	elif _class == 'inventories':
		return search_inventories(request), 200
	elif _class == 'loans':
		return search_loans(request), 200
	elif _class == 'sales':
		return [], 200
	elif _class == 'items':
		return search_items(request)

	# République
	elif _class == 'votes':
		return [], 200
	elif _class == 'elections':
		return [], 200

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
		return get_entity(request, 'entities', id)
	elif _class == 'individuals':
		return get_entity(request, 'individuals', 'i' + id)
	elif _class == 'organizations':
		return get_entity(request, 'organizations', 'o' + id)
	elif _class == 'positions':
		return get_position(request, id)

	# Si la classe ne correspond à rien
	else:
		server.error(request.remote_addr, 'GET', f"/model/{_class}/{id}", 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400

@app.get('/model/organizations/<string:id>/avatar')
def get_avatar(id: str):
	if not (tn_safe(id)):
		server.error(request.remote_addr, 'GET', f"/model/organizations/{id}/avatar", 400, "Invalid Data Class Or Identifier")
		return {"message": "Bad Request"}, 400

	return download_avatar(request, id)

@app.post('/model/<string:_class>/<string:id>/<string:action>')
def update_model(_class: str, id: str, action: str):
	if not (tn_safe(id) and tn_safe(_class)):
		server.error(request.remote_addr, 'POST', f"/model/{_class}/{id}/{action}", 400, "Invalid Data Class Or Identifier")
		return {"message": "Bad Request"}, 400

	if _class == "individuals":
		return update_entity(request, _class, id, action)
	elif _class == "organizations":
		return update_entity(request, _class, id, action)

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
			groups = entities.get_entity_groups(id)

			for grp in groups:
				query = get_entity(request, "organizations", grp["id"]) # Le groupe est déjà au complet mais on prévient toute sorte de bypass

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
		return create_entity(request, 'individuals')
	elif _class == 'organizations':
		return create_entity(request, 'organizations')

	# Si ça correspond à rien
	else:
		server.error(request.remote_addr, 'PUT', '/new_model', 400, "Invalid Data Class")
		return {"message": "Invalid Data Class"}, 400


# ---------- BANQUE ----------

@app.put("/bank/register_account")
def open_bank_account():
	return register_account(request)

@app.get("/bank/accounts/<string:id>")
def get_bank_account(id: str):
	return get_account(request, id)

@app.post("/bank/accounts/<string:id>/<string:action>")
def edit_bank_account(id: str, action: str):
	if action == 'freeze':
		return freeze_account(request, id)
	elif action == 'flag':
		return flag_account(request, id)
	elif action == 'debit':
		return debit(request, id)
	elif action == 'deposit':
		return deposit(request, id)

	else:
		server.error(request.remote_addr, 'POST', f'/bank/accounts/{id}/{action}', 400, "Invalid Action")
		return {"message": "Invalid Action"}, 400