import os

from utils.db import drivepath

from .commons import *

def register_file(_dir: str, name: str, data: bytes, overwrite: bool = False):
	_dir = os.path.join(drivepath, _dir)
	path = os.path.join(_dir, name)

	if not os.path.exists(_dir): # La database est bien structurée, aucune création de dossier permise
		raise PermissionError(f"Attempt to create a directory: {path}")

	if os.path.exists(path) and not overwrite:
		raise FileExistsError(f"File {path} already exists.")

	with open(path, "wb") as file:
		file.write(data)

def open_file(path: str) -> bytes:
	path = adjust_path(path)
	if path.startswith('/'): path = path[1:]
	path = os.path.join(drivepath, path)

	with open(path, "rb") as file:
		return file.read()