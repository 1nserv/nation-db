import json
import os
import typing

from utils.db import dbpath

from ..common.database import fetch
from ..common import database as db
from ..common.commons import *

from . import entities

dbpath = os.path.join(dbpath, "auth.db")

def get_session(query: str, by_id: bool = False) -> dict:
	if by_id:
		res = fetch("auth.Sessions", id = query)
	else:
		res = fetch("auth.Sessions", token = query)

	if len(res) == 0:
		return None
	else:
		session = res[0]

	return session

def save_session(data: dict) -> tuple[bool, str]:
	existing_data = get_session(data["id"])

	if existing_data:
		return False, "Session Already Exists"

	db.put_item(dbpath, "Sessions", data)

	return True, "OK"


def get_account(id: str) -> dict:
	res = fetch("auth.Accounts", id = id)

	if len(res) == 0:
		return None
	else:
		acc = res[0]

	return acc

def save_account(data: dict) -> tuple[bool, str]:
	existing_data = get_account(data["id"])

	if existing_data:
		return False, "Account Already Exists"

	db.put_item(dbpath, "Accounts", data)

	return True, "OK"



def check_session(token: str, permissions: dict[str, str]):
	session = get_session(token)
	permissions = merge_permissions(permissions, { "database": "-m--" })

	if not session:
		return False

	individual = entities.get_individual(session['author'])

	if not individual:
		return False

	pos = entities.get_position(individual["position"])

	match_found = False

	for key, value in permissions.items():
		if key not in pos["permissions"]:
			continue

		match = True
		for idx, char in enumerate(value):
			if char != "-" and char != pos["permissions"][key][idx]:
				match = False
				break

		if match:
			return True

	return False