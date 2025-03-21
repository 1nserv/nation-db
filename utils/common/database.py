import json
import os
import sqlite3
import typing

from utils.db import dbpath

def get_items(dbpath:str, table: str):
	if " " in table:
		raise SyntaxError("Whitespaces are not allowed in <table> parameter")

	with sqlite3.connect(dbpath) as conn:
		cursor = conn.cursor()
		cursor.execute(f"SELECT * FROM {table}")

		columns = [ str(description[0]) for description in cursor.description ]

		return [ dict(zip(columns, row)) for row in cursor.fetchall() ]


def put_item(dbpath: str, table: str, item: dict, overwrite: bool = False):
	with sqlite3.connect(dbpath) as conn:
		cursor = conn.execute(f"PRAGMA table_info({table})")
		table_columns = [ row[1] for row in cursor.fetchall() ]

		if sorted(item.keys()) != sorted(table_columns):
			raise ValueError("Keys don't match with table scheme.")

		placeholders = ", ".join("?" for _ in item)
		columns = ", ".join(item.keys())
		values = tuple(item.values())

		if overwrite:
			query = (
				f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
				f"ON CONFLICT DO UPDATE SET "
				+ ", ".join(f"{col}=excluded.{col}" for col in item.keys())
			)
		else:
			query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

		conn.execute(query, values)

def delete_item(dbpath: str, table: str, id: str) -> tuple[bool, str]:
	if " " in table:
		raise SyntaxError("Whitespaces are not allowed in <table> parameter")

	with sqlite3.connect(dbpath) as conn:
		cursor = conn.cursor()

		cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE id = ?", (id,))
		if cursor.fetchone()[0] == 0:
			return False, "Item Not Found"

		cursor.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
		conn.commit()

	return True, "Deleted Successfully"

def fetch(zone: str, **query: typing.Any) -> list[dict]:
	zone = zone.split('.')
	base = os.path.join(dbpath, f"{zone[0]}.db")
	table = zone[1]

	items = sorted(get_items(base, table), key = lambda item: -int(item.get('register_date', "0")))
	res = []

	for item in items:
		if item is None:
			continue

		for q, value in query.items():
			try:
				parsed_attr = json.loads(item[q])

				if parsed_attr != value:
					break
			except (json.JSONDecodeError, KeyError, TypeError):
				if item.get(q) != value:
					break
		else:
			res.append(item)

	return res