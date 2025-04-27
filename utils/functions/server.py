from datetime import datetime
import json
import os
import requests

from utils.db import logpath

webhooks: dict = {}

try:
	with open('.local/webhooks.json', 'r') as file:
		webhooks = json.load(file)
except FileNotFoundError:
	pass


def error(ip: str, method: str, path: str, code: int = 500, message: str = "Unknown Error"):
	date = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

	output = f"\033[1;34m{ip}" + (15 - len(ip)) * "-" + f" \033[0m{date} | \033[31;1m{code}\033[0m {method} {path}"
	print(output, flush = True)

	with open(os.path.join(logpath, "requests.log"), "a") as file:
		file.write(f"\n{ip}" + (15 - len(ip)) * "-" + f" {date} | {method} {path} - {code} {message}")

def log(ip: str, method: str, path: str, code: int = 200, message: str = "Success"):
	date = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

	output = f"\033[1;34m{ip}" + (15 - len(ip)) * "-" + f"\033[0m {date} | \033[32;1m{code}\033[0m {method} {path}"
	print(output, flush = True)

	with open(os.path.join(logpath, "requests.log"), "a") as file:
		file.write(f"\n{ip}" + (15 - len(ip)) * "-" + f" {date} | {method} {path} - {code} {message}")


def create_archive(domain: str, archive: dict):
	name = datetime.now().strftime("%H_%M_%S")
	date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
	dir = os.path.join(logpath, domain, str(datetime.now().year), str(datetime.now().month), str(datetime.now().day))

	if not os.path.exists(dir):
		os.makedirs(dir)

	details = archive.pop("details", None)

	archive["date"] = date
	content = '\n'.join([ f"{key.upper()} :: {val}" for key, val in archive.items() ])

	if details:
		content += f'\n\n{details}'

	with open(os.path.join(dir, "{}_{}.log".format(name, archive.get("action", "ARCHIVE"))), 'w') as file:
		file.write(content)

	# Envoi de l'arhcive sur Discord via un webhook
	data = {
		"content": '',
		"embeds": [
			{
				"title": "Archive",
				"color": int(webhooks[domain]['color'], 16),
				"timestamp": datetime.now().isoformat(),
				"footer": {
					"text": domain
				},
				"fields": [
					{
						"name": k.upper(),
						"value": v,
						"inline": False
					}

					for k, v in archive.items()
				]
			}
		]
	}

	response = requests.post(webhooks[domain]['url'], json = data)