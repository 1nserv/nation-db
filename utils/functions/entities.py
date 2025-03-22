import json
import os
import typing

from utils.db import dbpath

from ..common.database import fetch
from ..common import database as db

dbpath = os.path.join(dbpath, "entities.db")

def get_individual(id: str) -> dict:
	res = fetch("entities.Individuals", id = id)

	if len(res) == 0:
		return None
	else:
		entity = res[0]

	entity["register_date"] = int(entity["register_date"])
	entity["xp"] = int(entity["xp"])
	entity["boosts"] = json.loads(entity["boosts"])
	entity["additional"] = json.loads(entity["additional"])
	entity["votes"] = json.loads(entity["votes"])

	return entity

def save_individual(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_individual(data["id"])

	if existing_data and not overwrite:
		return False, "Entity Already Exists"

	data["register_date"] = str(data["register_date"])
	data["xp"] = str(data["xp"])
	data["boosts"] = json.dumps(data["boosts"])
	data["additional"] = json.dumps(data["additional"])
	data["votes"] = json.dumps(data["votes"])

	db.put_item(dbpath, "Individuals", data, overwrite)

	return True, "OK"

def delete_individual(id: str) -> tuple[bool, str]:
	existing_data = get_individual(id)

	if not existing_data:
		return False, "Entity Not Found"

	db.delete_item(dbpath, "Individuals", id)
	return True, "Deleted Successfully"


def fetch_individuals(**query: typing.Any) -> list[dict]:
	res = fetch("entities.Individuals", **query)
	res = [ get_individual(member["id"]) for member in res if member ]
	return [ member for member in res if member ]


def get_organization(id: str) -> dict:
	res = fetch("entities.Organizations", id = id)

	if len(res) == 0:
		return None
	else:
		entity = res[0]

	entity["register_date"] = int(entity["register_date"])
	entity["members"] = json.loads(entity["members"])
	entity["invites"] = json.loads(entity["invites"])
	entity["certifications"] = json.loads(entity["certifications"])
	entity["additional"] = json.loads(entity["additional"])

	return entity

def save_organization(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_organization(data["id"])

	if existing_data and not overwrite:
		return False, "Entity Already Exists"

	data["register_date"] = str(data["register_date"])
	data["members"] = json.dumps(data["members"])
	data["invites"] = json.dumps(data["invites"])
	data["certifications"] = json.dumps(data["certifications"])
	data["additional"] = json.dumps(data["additional"])

	db.put_item(dbpath, "Organizations", data, overwrite)

	return True, "OK"

def delete_organization(id: str) -> tuple[bool, str]:
	existing_data = get_organization(id)

	if not existing_data:
		return False, "Entity Not Found"

	db.delete_item(dbpath, "Organizations", id)
	return True, "Deleted Successfully"

def fetch_organizations(**query: typing.Any) -> list[dict]:
	res = fetch("entities.Organizations", **query)
	res = [ get_organization(org["id"]) for org in res if org is not None ]
	return [ org for org in res if org ] # Permet d'éviter que des None s'invitent à la fête


def get_entity(id: str) -> dict | None:
	entity = get_individual(id)

	if not entity:
		entity = get_organization(id)

	return entity

def fetch_entities(**query: typing.Any) -> list[dict]:
	res = fetch_individuals(**query)
	res.extend(fetch_organizations(**query))
	return sorted(res, key = lambda i : -int(i["register_date"]))

def get_entity_groups(id: str) -> list[str]:
	groups = fetch_organizations()
	result = []

	for grp in groups:
		if grp["owner_id"] == id:
			result.append(grp)
			continue

		for member in grp["members"]:
			if member["id"] == id:
				result.append(grp)
				break

	return result



def get_position(id: str) -> dict:
	res = fetch("entities.Positions", id = id)

	if len(res) == 0:
		return None
	else:
		position = res[0]

	position["permissions"] = json.loads(position["permissions"])
	position["manager_permissions"] = json.loads(position["manager_permissions"])

	return position

def save_position(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_position(data["id"])

	if existing_data:
		return False, "Position Already Exists"

	data["permissions"] = json.dumps(data["permissions"])
	data["manager_permissions"] = json.dumps(data["manager_permissions"])

	db.put_item(dbpath, "Positions", data, overwrite)

	return True, "OK"

def delete_position(id: str) -> tuple[bool, str]:
	existing_data = get_position(id)

	if not existing_data:
		return False, "Position Not Found"

	db.delete_item(dbpath, "Positions", id)
	return True, "Deleted Successfully"

def fetch_positions(**query: typing.Any) -> list[dict]:
	res = fetch("entities.Positions", **query)
	return [ get_position(position["id"]) for position in res ]