import json
import os
import typing

from utils.db import dbpath

from ..common.database import fetch
from ..common import database as db

dbpath = os.path.join(dbpath, "marketplace.db")


# ===== ACCOUNTS =====

def get_account(id: str) -> dict:
	res = fetch("marketplace.Accounts", id = id)

	if len(res) == 0:
		return None
	else:
		acc = res[0]

	acc["frozen"] = bool(acc["frozen"])
	acc["flagged"] = bool(acc["frozen"])

	return acc

def save_account(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_account(data["id"])

	if existing_data and not overwrite:
		return False, "Account Already Exists"

	data["frozen"] = int(data["frozen"])
	data["flagged"] = int(data["flagged"])

	db.put_item(dbpath, "Accounts", data, overwrite)

	return True, "OK"

def delete_account(id: str) -> tuple[bool, str]:
	existing_data = get_account(id)

	if not existing_data:
		return False, "Account Not Found"

	db.delete_item(dbpath, "Accounts", id)
	return True, "Deleted Successfully"

def fetch_accounts(**query: typing.Any) -> list[dict]:
	res = fetch("marketplace.Accounts", **query)
	res = [ get_account(acc["id"]) for acc in res ] # La réponse est déjà complète mais certains attributs sont pas convertis (bool, objets, listes...)
	return [ acc for acc in res if acc ]



# ===== LOANS =====

def get_loan(id: str) -> dict:
	res = fetch("marketplace.Loans", id = id)

	if len(res) == 0:
		return None
	else:
		loan = res[0]

	loan["frozen"] = bool(loan["frozen"])
	loan["is_percentage"] = bool(loan["is_percentage"])

	return loan

def save_loan(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_loan(data["id"])

	if existing_data and not overwrite:
		return False, "Loan Already Exists"

	data["frozen"] = int(data["frozen"])
	data["is_percentage"] = int(data["is_percentage"])

	db.put_item(dbpath, "Loans", data, overwrite)

	return True, "OK"

def delete_loan(id: str) -> tuple[bool, str]:
	existing_data = get_loan(id)

	if not existing_data:
		return False, "Loan Not Found"

	db.delete_item(dbpath, "Loans", id)
	return True, "Deleted Successfully"

def fetch_loans(**query: typing.Any) -> list[dict]:
	res = fetch("marketplace.Loans", **query)
	res = [ get_loan(loan["id"]) for loan in res ]
	return [ loan for loan in res if loan ]



# ===== INVENTORIES =====

def get_inventory(id: str) -> dict:
	res = fetch("marketplace.Inventories", id = id)

	if len(res) == 0:
		return None
	else:
		inventory = res[0]

	inventory["items"] = json.loads(inventory["items"])

	return inventory

def save_inventory(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_inventory(data["id"])

	if existing_data and not overwrite:
		return False, "Inventory Already Exists"

	data["items"] = json.dumps(data["items"])

	db.put_item(dbpath, "Inventories", data, overwrite)

	return True, "OK"

def delete_inventory(id: str) -> tuple[bool, str]:
	existing_data = get_inventory(id)

	if not existing_data:
		return False, "Inventory Not Found"

	db.delete_item(dbpath, "Inventories", id)
	return True, "Deleted Successfully"

def fetch_inventories(**query: typing.Any) -> list[dict]:
	res = fetch("marketplace.Inventories", **query)
	res = [ get_inventory(inv["id"]) for inv in res ]
	return [ inv for inv in res if inv ]



# ===== ITEMS =====

def get_item(id: str) -> dict:
	res = fetch("marketplace.Items", id = id)

	if len(res) == 0:
		return None
	else:
		item = res[0]

	item["categories"] = json.loads(item["categories"].lower())
	item["craft"] = json.loads(item["craft"].lower())

	return item

def save_item(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_item(data["id"])

	if existing_data and not overwrite:
		return False, "Item Already Exists"

	data["categories"] = json.dumps(data["categories"])
	data["craft"] = json.dumps(data["craft"])

	db.put_item(dbpath, "Items", data, overwrite)

	return True, "OK"

def delete_item(id: str) -> tuple[bool, str]:
	existing_data = get_item(id)

	if not existing_data:
		return False, "Item Not Found"

	db.delete_item(dbpath, "Items", id)
	return True, "Deleted Successfully"

def fetch_items(**query: typing.Any) -> list[dict]:
	res = fetch("marketplace.Items", **query)
	res = [ get_item(item["id"]) for item in res ]
	return [ item for item in res if item ]



# ===== SALES =====

def get_sale(id: str) -> dict:
	res = fetch("marketplace.Sales", id = id)

	if len(res) == 0:
		return None
	else:
		sale = res[0]

	return sale

def save_sale(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_sale(data["id"])

	if existing_data and not overwrite:
		return False, "Sale Already Exists"

	db.put_item(dbpath, "Sales", data, overwrite)

	return True, "OK"

def delete_sale(id: str) -> tuple[bool, str]:
	existing_data = get_item(id)

	if not existing_data:
		return False, "Sale Not Found"

	db.delete_item(dbpath, "Sales", id)
	return True, "Deleted Successfully"

def fetch_sales(**query: typing.Any) -> list[dict]:
	res = fetch("marketplace.Sales", **query)
	res = [ get_sale(sale["id"]) for sale in res ]
	return [ sale for sale in res if sale ]