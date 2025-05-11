import time

from flask import Request

from utils.common.commons import *

from utils.functions import auth
from utils.functions import state
from utils.functions import entities
from utils.functions import server

from .. import entities as ei
from . import votes as vi

def get_election(req: Request, id: str):
	if not tn_safe(id):
		server.error(req.remote_addr, 'GET', f'/elections/{id}', 400, "Incorrect ID")
		return {"message": "Bad Request"}, 400

	# ---- FOUILLE DANS LA DB ----

	election = state.get_election(id)

	if not election:
		server.error(req.remote_addr, 'GET', f'/elections/{id}', 404, "Election Not Found")
		return {"message": "Election does not exist"}, 404

	res = vi.get_vote(req, election['vote'])

	if res[1] == 200:
		vote = res[0]
	else:
		return res

	election['vote'] = vote

	server.log(req.remote_addr, 'GET', f'/elections/{id}')
	return election, 200

def submit_candidacy(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 400, "Expected JSON Request")
		return {"message": "Expected JSON Request"}, 400

	if not tn_safe(id):
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "parameter": "id"}, 400


	# ---- PERMISSIONS ----

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 401, "Missing Token")
		return {"message": "Missing Token"}, 401

	if not tn_safe(token):
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 401, "Invalid Token")
		return {"message": "Invalid Token"}, 401

	session = auth.get_session(token)

	if not session:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 401, "Invalid Token")
		return {"message": "Invalid Token"}, 401

	author = entities.get_individual(session['author'])

	if not author:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 401, "Session Does Not Match Any Author")
		return {"message": "Session Does Not Match Any Author"}, 401


	# ---- VÉRIFICATION DU VOTE ----

	election = state.get_election(req, id)

	if not election:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 404, "Election Not Found")
		return {"message": "Election Not Found"}, 404

	vote = state.get_vote(election['vote'])

	if not vote:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 404, "Election Not Linked To Any Vote")
		return {"message": "Election Not Linked To Any Vote"}, 404

	if vote['start'] <= round(time.time()) - 10800: # Les candidats ont jusqu'à 3h avant le début du vote pour se présenter
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 401, "Vote Already Started")
		return {"message": "Vote Already Started"}, 401


	# ---- VÉRIFICATION DU CANDIDAT ----

	group = {}

	res = entities.fetch_organizations(position = 'parti')

	for grp in res:
		if grp['ower_id'] == author['id']:
			group = grp.eopy()
			break

		for member in grp['members']:
			if member['id'] == author['id']:
				group = grp.copy()
				break
	else:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 403, "Not In Any Party")
		return {"message": "Not In Any Party"}, 403

	# TODO: Vérification des sanctions


	# ---- VÉRIFICATION DU PARTI ----

	party = state.get_party(group['id'])

	if not party:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/submit', 403, "Party Not Registered")
		return {"message": "Party Not Registered"}, 403

	# ---- ENREGISTREMENT ----

	vote['propositions'][author['id']] = author['name'] + "({})".format(group['name'])

	state.save_vote(vote)

	server.log(req.remote_addr, 'PUT', f'/elections/{id}/submit')
	server.create_archive('republic', {
		'action': "SUBMIT_CANDIDACY",
		'candidate': author['id'],
		'party': group['id'],
		'election': id
	})

	return {"message": "Success"}, 200

def cancel_candidacy(req: Request, id: str):
	if not req.is_json:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 400, "Expected JSON Request")
		return {"message": "Expected JSON Request"}, 400

	if not tn_safe(id):
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "parameter": "id"}, 400


	# ---- PERMISSIONS ----

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 401, "Missing Token")
		return {"message": "Missing Token"}, 401

	if not tn_safe(token):
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 401, "Invalid Token")
		return {"message": "Invalid Token"}, 401

	session = auth.get_session(token)

	if not session:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 401, "Invalid Token")
		return {"message": "Invalid Token"}, 401

	author = entities.get_individual(session['author'])

	if not author:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 401, "Session Does Not Match Any Author")
		return {"message": "Session Does Not Match Any Author"}, 401


	# ---- VÉRIFICATION DU VOTE ----

	election = state.get_election(req, id)

	if not election:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 404, "Election Not Found")
		return {"message": "Election Not Found"}, 404

	vote = state.get_vote(election['vote'])

	if not vote:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 404, "Election Not Linked To Any Vote")
		return {"message": "Election Not Linked To Any Vote"}, 404

	if vote['start'] <= round(time.time()) - 10800: # Les candidats ont jusqu'à 3h avant le début du vote pour se retirer
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 401, "Vote Already Started")
		return {"message": "Vote Already Started"}, 401

	# ---- TRAITEMENT ----

	if author['id'] in vote['propositions'].keys():
		del vote['propositions'][author['id']]
		del vote['results'][author['id']]
	else:
		server.error(req.remote_addr, 'PUT', f'/elections/{id}/cancel_candidacy', 404, "Candidate Not Found")
		return {"message": "Candidate Not Found"}, 404

	state.save_vote(vote)

	server.log(req.remote_addr, 'POST', f'/elections/{id}/cencel_candidacy')
	server.create_archive('republic', {
		'action': 'CANCEL_CANDIDACY',
		'author': author['id'],
		'election': id
	})

	return {"message": "Success"}

def register_party(req: Request):
	if not req.is_json:
		server.error(req.remote_addr, 'PUT', f'/register_party', 400, "Expected JSON Request")
		return {"message": "Expected JSON Request"}, 400

	if not tn_safe(id):
		server.error(req.remote_addr, 'PUT', f'/register_party', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "parameter": "id"}, 400

	params = req.args
	payload = req.json


	# ---- PERMISSIONS ----

	if req.authorization:
		token = req.authorization.token
	else:
		server.error(req.remote_addr, 'PUT', f'/register_party', 401, "Missing Token")
		return {"message": "Missing Token"}, 401

	if not tn_safe(token):
		server.error(req.remote_addr, 'PUT', f'/register_party', 401, "Invalid Token")
		return {"message": "Invalid Token"}, 401

	session = auth.get_session(token)

	if not session:
		server.error(req.remote_addr, 'PUT', f'/register_party', 401, "Invalid Token")
		return {"message": "Invalid Token"}, 401

	author = entities.get_individual(session['author'])

	if not author:
		server.error(req.remote_addr, 'PUT', f'/register_party', 401, "Session Does Not Match Any Author")
		return {"message": "Session Does Not Match Any Author"}, 401


	# ---- VÉRIFICATION DU PARTI ----

	if not tn_safe(params.get('candidate')):
		server.error(req.remote_addr, 'PUT', f'/register_party', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter", "param": "parti"}, 400

	group = entities.get_organization(params['candidate'])

	if not group:
		server.error(req.remote_addr, 'PUT', f'/register_party', 404, "Does Not Exist")
		return {"message": "Does Not Exist"}, 404

	if group['owner'] != author['id']:
		server.error(req.remote_addr, 'PUT', f'/register_party', 403, "You Are Not The Owner")
		return {"message": "You Are Not The Owner"}, 403

	if group['position'] != 'parti':
		server.error(req.remote_addr, 'PUT', f'/register_party', 422, "Not A Party")
		return {"message": "Not A Party"}, 422

	if len(group['members']) < 2:
		server.error(req.remote_addr, 'PUT', f'/register_party', 422, "Not Enough Members")
		return {"message": "Not Enough Mmbers"}, 422


	# ---- ENREGISTREMENT ----

	res = state.get_party(params['candidate'])

	if res:
		server.error(req.remote_addr, 'PUT', f'/register_party', 409, "Already A Candidate")
		return {"message": "Already A Candidate"}, 409

	motto = payload.get('motto')

	try:
		color = int(payload.get('color', 0))
	except ValueError:
		server.error(req.remote_addr, 'PUT', f'/register_party', 400, "Invalid Or Missing Parameter")
		return {"message": "Invalid Or Missing Parameter"}, 400

	party = {
		'org_id': params['candidate'],
		'color': color,
		'motto': motto,
		'politiscales': "{}",
		'last_election': None
	}

	state.save_party(party)

	server.log(req.remote_addr, 'PUT', f'/register_party')
	server.create_archive('republic', {
		"action": "SUBMIT_CANDIDACY",
		"author": author['id'],
		"party": party['org_id'],
		"election": id
	})

	return {"message": "Success"}, 200