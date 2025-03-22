import os
import re
import random

from utils.db import drivepath, dbpath

def get_in_drive(path: str) -> bytes:
	with open(os.path.join(drivepath, path), 'rb') as _buffer:
		return _buffer.read()

def merge_permissions(d1: dict[str, str], d2: dict[str, str]) -> dict[str, str]:
	new_dict: dict[str, str] = d1.copy()

	for key, val in d2.items():
		ref = ""
		for state, i in zip(val, range(len(val))):
			if new_dict[key][i] == "-":
				ref += state
			else:
				ref += new_dict[key][i]

		new_dict[key] = ref

	return new_dict


# Sécurité

def adjust_path(path: str) -> str:
	path = os.path.normpath(path)
	path = path.replace('\\', '/')

	newpath = []
	for component in path.split('/'):
		if component not in ('..',):
			newpath.append(component)

	return '/'.join(newpath)

def sql_safe(data: str) -> bool:
	patterns = [
		r"(?:--|\#)",
		r"';\s*(?:DROP|ALTER|CREATE|INSERT|UPDATE|DELETE|REPLACE)",
		r"UNION\s+SELECT",
		r"' OR '1'='1",
		r"SELECT \* FROM",
		r"' OR 1=1 --",
		r";--",
		r";\s*PRAGMA",
	]

	for pattern in patterns:
		if re.search(pattern, data, re.IGNORECASE):
			return False

	return True

def tn_safe(data: str) -> bool: # Safe for table and bucket names
	if not data:
		return False

	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_."

	for char in data:
		if char not in charset:
			return False

	return True

# Banque

def gen_digicode(length: int = 6) -> str:
	return hex(random.randint(0, 16 ** 8))[2:].upper().zfill(length)

# Impôts

TAXATIONS = ('taxe_ega',)

def calculate_amount(tag: str, income: int = 0) -> int:
	if tag not in TAXATIONS:
		return 0

	if tag == "taxe_ega": # Taxe égalitaire
		if income < 2000:
			percentage = 0
		elif 2000 <= income < 5000:
			percentage = .01
		elif 5000 <= income < 20000:
			percentage = .025
		elif 20000 <= income < 50000:
			percentage = .045
		else:
			percentage = .05
			e = income

			while e >= 150000 and percentage < .2:
				percentage += .01
				e -= 100000

	return int(round(income * percentage))
