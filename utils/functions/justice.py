import json
import os
import typing

from utils.db import dbpath

from ..common.database import fetch
from ..common import database as db

dbpath = os.path.join(dbpath, "republic.db")


"""
REPORTS
"""

def get_report(id: str) -> dict:
	res = fetch("republic.Reports", id = id)

	if len(res) == 0:
		return None
	else:
		report = res[0]

	return report

def save_report(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_report(data["id"])

	if existing_data and not overwrite:
		return False, "Report Already Exists"

	db.put_item(dbpath, "Reports", data, overwrite)

	return True, "OK"

def delete_report(id: str) -> tuple[bool, str]:
	existing_data = get_report(id)

	if not existing_data:
		return False, "Report Not Found"

	db.delete_item(dbpath, "Reports", id)
	return True, "Deleted Successfully"


def fetch_reports(**query: typing.Any) -> list[dict]:
	res = fetch("republic.Reports", **query)
	res = [ get_report(report["id"]) for report in res if report ]
	return [ vote for vote in res if vote ]


"""
PROCÈS
"""

def get_lawsuit(id: str) -> dict:
	res = fetch("republic.Lawsuits", id = id)

	if len(res) == 0:
		return None
	else:
		lawsuit = res[0]

	lawsuit['private'] = bool(lawsuit['private'])

	return lawsuit

def save_lawsuit(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_lawsuit(data["id"])

	if existing_data and not overwrite:
		return False, "Lawsuit Already Exists"

	db.put_item(dbpath, "Lawsuits", data, overwrite)

	return True, "OK"

def delete_lawsuit(id: str) -> tuple[bool, str]:
	existing_data = get_lawsuit(id)

	if not existing_data:
		return False, "Lawsuit Not Found"

	db.delete_item(dbpath, "Lawsuits", id)
	return True, "Deleted Successfully"


def fetch_lawsuits(**query: typing.Any) -> list[dict]:
	res = fetch("republic.Lawsuits", **query)
	res = [ get_lawsuit(lawsuit["id"]) for lawsuit in res if lawsuit ]
	return [ lawsuit for lawsuit in res if lawsuit ]


"""
SANCTIONS
"""

def get_sanction(id: str) -> dict:
	res = fetch("republic.Sanctions", id = id)

	if len(res) == 0:
		return None
	else:
		sanction = res[0]

	return sanction

def save_sanction(data: dict, overwrite: bool = True) -> tuple[bool, str]:
	existing_data = get_sanction(data["id"])

	if existing_data and not overwrite:
		return False, "Sanction Already Exists"

	db.put_item(dbpath, "Sanctions", data, overwrite)

	return True, "OK"

def delete_sanction(id: str) -> tuple[bool, str]:
	existing_data = get_sanction(id)

	if not existing_data:
		return False, "Sanction Not Found"

	db.delete_item(dbpath, "Sanctions", id)
	return True, "Deleted Successfully"


def fetch_Sanctions(**query: typing.Any) -> list[dict]:
	res = fetch("republic.Sanctions", **query)
	res = [ get_sanction(sanction["id"]) for sanction in res if sanction ]
	return [ sanction for sanction in res if sanction ]