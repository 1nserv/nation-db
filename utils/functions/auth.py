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

def delete_session(id: str) -> tuple[bool, str]:
	existing_data = get_session(id, True)

	if not existing_data:
		return False, "Session Not Found"

	db.delete_item(dbpath, "Sessions", id)
	return True, "Deleted Successfully"


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

def delete_account(id: str) -> tuple[bool, str]:
	existing_data = get_account(id)

	if not existing_data:
		return False, "Account Not Found"

	db.delete_item(dbpath, "Accounts", id)
	return True, "Deleted Successfully"


def get_oauth(code: str) -> dict:
	res = fetch("auth.Providers", auth_code = code)

	if len(res) == 0:
		return None
	else:
		acc = res[0]

	return acc

def save_oauth(data: dict) -> tuple[bool, str]:
	existing_data = get_oauth(data["auth_code"])

	if existing_data:
		return False, "OAuth Token Already Exists"

	db.put_item(dbpath, "Providers", data)

	return True, "OK"

def delete_oauth(code: str) -> tuple[bool, str]:
	existing_data = get_oauth(code)

	if not existing_data:
		return False, "OAuth Token Not Found"

	db.delete_item(dbpath, "Providers", code)
	return True, "Deleted Successfully"



def check_permissions(permissions: dict[str, str], required: dict[str, str] = {}) -> bool:
	permissions = merge_permissions(permissions, { "database": "-m--" })

	for key, value in required.items():
		if key not in permissions:
			continue

		match = True
		for idx, char in enumerate(value):
			if char != "-" and char != permissions[key][idx]:
				match = False
				break

		if match:
			return True

	return False

def check_position(id: str, permissions: dict[str, str] = {}):
	pos = entities.get_position(id)

	return check_permissions(pos["permissions"], permissions)

def check_session(token: str, permissions: dict[str, str] = {}):
	session = get_session(token)

	if not session:
		return False

	individual = entities.get_individual(session['author'])

	if not individual:
		return False

	return check_position(individual["position"], permissions)