import time

from flask import Request

from utils.common.commons import *

from utils.functions import auth
from utils.functions import state
from utils.functions import entities
from utils.functions import server

def get_vote(req: Request, id: str):
	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/votes/{id}', 400, "Incorrect ID")
		return {"message": "Bad Request"}, 400

	# ---- PERMISSIONS ----

	token = req.authorization.token if req.authorization else None

	if token:
		if not tn_safe(token):
			server.error(req.remote_addr, 'GET', f'/votes/{id}', 400, "Invalid Token")
			return {"message": "Invalid Token"}, 400

	can_read_votes = auth.check_session(token, { 'votes': '---r' })

	# ---- FOUILLE DANS LA DB ----

	data = state.get_vote(id)

	if not data:
		server.error(req.remote_addr, 'GET', f'/votes/{id}', 404, "Vote Not Found")
		return {"message": "Vote does not exist"}, 404

	vote = data.copy()

	if data['end'] > time.time() and not can_read_votes:
		data['results'] = { k: 0 for k in data['results'].keys() } 

	server.log(req.remote_addr, 'GET', f'/votes/{id}')
	return vote, 200


def open_vote(req: Request):
	payload = req.json

	# ---- PERMISSIONS ----

	if req.authorization.token:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 401, "Missing Token")
		return {"message": "Missing Token"}, 401

	if not tn_safe(token):
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 400, "Invalid Token")
		return {"message": "Invalid Token"}, 400

	if not auth.check_session(token, { 'votes': 'a---' }):
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 403, "Permission Denied")
		return {"message": "Permission Denied"}, 403

	# ---- SÉCURITÉ ----

	if not tn_safe(payload.get('title')):
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "parameter": "title"}, 400

	if not tn_safe(payload.get('propositions')):
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "parameter": "propositions"}, 400

	try:
		end = int(payload.get('end', round(time.time()) + 86400))
	except ValueError:
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "parameter": "end"}, 400

	if 'allowed_roles' in payload.keys():
		allowed_roles = []

		try:
			for role in payload.get('allowed_roles', []):
				allowed_roles.append(int(role))
		except ValueError:
			server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter", "parameter": "allowed_roles"}, 400
	else:
		allowed_roles = None

	if 'author' in payload.keys():
		if not auth.check_session(token, {}): # Permission database.manage requise pour ouvrir un vote au nom de qqun d'autre
			server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 401, "Cannot Open Vote As Another User")
			return {"message": "Cannot Open Vote As Another User"}, 401

		author = entities.get_individual(payload['author'])
		if not author:
			server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 404, "Author Not Found")
			return {"message": "Author Not Found"}, 404

		if 'a' not in author['permissions']['votes']:
			server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 403, "Author Cannot Open Vote")
			return {"message": "Author Cannot Open Vote"}, 403
	else:
		author = entities.get_individual(auth.get_session(token)['author'])
		# Permissions déjà vérifiées plus haut


	# ---- TRAITEMENT ----

	vote = state.get_vote(id)

	if vote:
		server.error(req.remote_addr, 'POST', f'/open_vote/{id}', 409, "Vote Already Exists")
		return {"message": "Vote Already Exists"}, 409

	id = hex(round(time.time()))[2:].upper()

	vote = {
		"id": id,
		"title": payload.get('title', f'Vote n°{id}'),
		"author": author['id'],
		"propositions": payload['propositions'],
		"results": { k: 0 for k in payload['propositions'] },
		"start": round(time.time()),
		"end": end,
		"allowed_roles": payload.get('allowed_roles'),
	}

	state.save_vote(vote['id'])

	server.log(req.remote_addr, 'POST', f'/open_vote/{id}')
	server.create_archive("votes", {
		"action": "OPEN_VOTE",
		"vote": vote['id'],
		"author": author['id'],
	})

	return {"message": "Vote Created", "id": vote['id']}, 200


def close_vote(req: Request, id: str):
	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/votes/{id}/close', 400, "Invalid ID")
		return {"message": "Invalid ID"}, 400

	# ---- PERMISSIONS ----

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/close', 401, "Missing Token")
		return {"message": "Missing Token"}, 401

	if not tn_safe(token):
		server.error(req.remote_addr, 'POST', f'/votes/{id}/close', 400, "Invalid Token")
		return {"message": "Invalid Token"}, 400

	can_close_votes = auth.check_session(token, { 'votes': '-m--' })

	# ----- TRAITEMENT ----

	session = auth.get_session(token)

	vote = state.get_vote(id)

	if not vote:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/close', 404, "Vote Not Found")
		return {"message": "Vote Not Found"}, 404

	if can_close_votes:
		vote['end'] = round(time.time())
	else:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/close', 403, "Permission Denied")
		return {"message": "Permission Denied"}, 403

	state.save_vote(vote['id'])

	server.log(req.remote_addr, 'POST', f'/votes/{id}/close')
	server.create_archive("votes", {
		"action": "CLOSE_VOTE",
		"vote": vote['id'],
		"author": session['author_id']
	})

	return {"message": "Vote Closed"}, 200


def vote_proposal(req: Request, id: str):
	params = req.args

	if not tn_safe(id):
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 400, "Invalid ID")
		return {"message": "Invalid ID"}, 400

	# ---- PERMISSIONS ----

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 401, "Missing Token")
		return {"message": "Missing Token"}, 401

	if not tn_safe(token):
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 400, "Invalid Token")
		return {"message": "Invalid Token"}, 400

	can_vote = auth.check_session(token, { 'votes': 'a---' })

	# ---- FOUILLE DANS LA DB ----

	session = auth.get_session(token)
	author = entities.get_individual(params.get('author', session['author_id']))

	if auth.check_session(token) and author['id'] != session['author_id']:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 403, "Permission Denied")
		return {"message": "Permission Denied"}, 403

	vote = state.get_vote(id)
	can_vote = auth.check_position(author['position'], { 'votes': 'a---' })

	if not vote:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 404, "Vote Not Found")
		return {"message": "Vote Not Found"}, 404

	if vote['end'] < round(time.time()):
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 403, "Vote Already Closed")
		return {"message": "Vote Already Closed"}, 403

	if vote['allowed_roles'] and author['position']['id'] not in vote['allowed_roles']:
		can_vote = False

	if can_vote:
		choice = params.get('choice')

		if not tn_safe(choice):
			server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter", "parameter": "vote"}, 400

		if choice not in vote['propositions'].keys():
			server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 400, "Invalid Or Missing Parameter")
			return {"message": "Invalid Or Missing Parameter", "parameter": "vote"}, 400

		if vote['id'] in author['votes']:
			server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 403, "Already Voted")
			return {"message": "Already Voted"}, 403

		vote['results'][choice] += 1
		author['votes'].append(vote['id'])
		# vote['voters'].append(session['author_id'])

		state.save_vote(vote['id'], vote)
		entities.save_individual(author['id'], author)
	else:
		server.error(req.remote_addr, 'POST', f'/votes/{id}/vote', 403, "Permission Denied")
		return {"message": "Permission Denied"}, 403

	server.log(req.remote_addr, 'POST', f'/votes/{id}/vote')
	server.create_archive("votes", {
		"action": "VOTE",
		"vote": vote['id'],
		"author": session['author_id'],
	})

	return {"message": "Vote Registered"}, 200