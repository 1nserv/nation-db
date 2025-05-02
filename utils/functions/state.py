import json
import os
import typing

from utils.db import dbpath

from ..common.database import fetch
from ..common import database as db

dbpath = os.path.join(dbpath, "republic.db")


"""
VOTES
"""

def get_vote(id: str) -> dict:
	res = fetch("republic.Votes", id = id)

	if len(res) == 0:
		return None
	else:
		vote = res[0]

	vote["allowed_roles"] = json.loads(vote["allowed_roles"])

	return vote

def save_vote(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_vote(data["id"])

	if existing_data and not overwrite:
		return False, "Vote Already Exists"

	data["allowed_roles"] = json.dumps(data["allowed_roles"])

	db.put_item(dbpath, "Votes", data, overwrite)

	return True, "OK"

def delete_vote(id: str) -> tuple[bool, str]:
	existing_data = get_vote(id)

	if not existing_data:
		return False, "Vote Not Found"

	db.delete_item(dbpath, "Votes", id)
	return True, "Deleted Successfully"


def fetch_votes(**query: typing.Any) -> list[dict]:
	res = fetch("republic.Votes", **query)
	res = [ get_vote(vote["id"]) for vote in res if vote ]
	return [ vote for vote in res if vote ]


"""
ELECTIONS
"""

def get_election(id: str) -> dict:
	res = fetch("republic.Elections", id = id)

	if len(res) == 0:
		return None
	else:
		election = res[0]

	return election

def save_election(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_election(data["id"])

	if existing_data and not overwrite:
		return False, "Election Already Exists"

	db.put_item(dbpath, "Elections", data, overwrite)

	return True, "OK"

def delete_election(id: str) -> tuple[bool, str]:
	existing_data = get_election(id)

	if not existing_data:
		return False, "Election Not Found"

	db.delete_item(dbpath, "Elections", id)
	return True, "Deleted Successfully"


def fetch_elections(**query: typing.Any) -> list[dict]:
	res = fetch("republic.Elections", **query)
	res = [ get_election(election["id"]) for election in res if election ]
	return [ election for election in res if election ]


"""
PARTIS
"""

def get_party(id: str) -> dict:
	res = fetch("republic.Parties", id = id)

	if len(res) == 0:
		return None
	else:
		party = res[0]

	party["politiscales"] = json.loads(party["politiscales"])

	return party

def save_party(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_party(data["id"])

	if existing_data and not overwrite:
		return False, "Party Already Exists"

	data["politiscales"] = json.dumps(data["politiscales"])

	db.put_item(dbpath, "Parties", data, overwrite)

	return True, "OK"

def delete_party(id: str) -> tuple[bool, str]:
	existing_data = get_party(id)

	if not existing_data:
		return False, "Party Not Found"

	db.delete_item(dbpath, "Parties", id)
	return True, "Deleted Successfully"


def fetch_parties(**query: typing.Any) -> list[dict]:
	res = fetch("republic.Parties", **query)
	res = [ get_party(party["id"]) for party in res if party ]
	return [ party for party in res if party ]