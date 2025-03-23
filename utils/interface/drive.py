import io

from flask import Request, send_file

from utils.common.commons import *
from utils.common import drive

from utils.functions import auth
from utils.functions import server

def upload_avatar(req: Request):
	if not req.is_json:
		server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 400, "Bad Request")
		return {"message": "Payload must be a json value"}, 400

	if req.authorization:
		token = req.authorization.token

		if not sql_safe(token): # Pour prévenir les attaques
			server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 400, "Bad Request")
			return {"message": "Bad Request"}, 400

		if not (auth.check_session(token, { "entities": "--e-", "database": "-m--" }, at_least_one = True)):
			server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 403, "Missing Permissions")
			return {"message": "Forbidden"}, 403
	else:
		server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 401, "Missing Token")
		return {"message": "Unauthorized"}, 401

	payload = req.json()

	if "avatar" in req.files.keys():
		file = req.files["avatar"]
	else:
		server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 400, "Missing File")
		return {"message": "Missing File", "missing_file": "avatar"}, 400

	session = auth.get_session(token)

	try:
		drive.register_file("entities", payload["name"], file.stream.read(), payload["overwrite"])
		server.create_archive("entities", {"action": "UPLOAD_AVATAR", "author": session["author_id"], "avatar_name": payload["name"]})

		server.log(req.remote_addr, 'PUT', '/upload/organizations/avatars')
		return {"message": "Success"}, 200
	except PermissionError:
		server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 404, "Invalid Bucket Name")
		return {"message": "Invalid Bucket Name"}, 404
	except FileExistsError:
		server.error(req.remote_addr, 'PUT', f'/upload/organizations/avatars', 409, "File Already Exists")
		return {"message": "Avatar Already Exists"}, 409

def download_avatar(req: Request, id: str):
	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/model/organizations/{id}/avatar', 400, "Bad Request")
		return {"message": "Bad Request"}, 400

	try:
		data = drive.open_file(f'/entities/{id}')
		server.log(req.remote_addr, 'GET', f'/model/organizations/{id}/avatar')
		return send_file(io.BytesIO(data), 'image/png'), 200
	except FileNotFoundError:
		server.error(req.remote_addr, 'GET', f'/model/organizations/{id}/avatar', 404, "Avatar Does Not Exist")
		return {"message": "Avatar Does Not Exist"}, 404