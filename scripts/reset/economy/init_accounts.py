import bcrypt

from utils.db import salt
from utils.functions import economy as bf

def save_acc(id: str):
	print(f"\033[1;34m== Initialisation pour {id} ==\033[0m")
	acc = {
		"id": id,
		"owner_id": id,
		"tag": "primary",
		"frozen": False,
		"flagged": False,
		"register_date": 0,
		"amount": int(input("Sommme sur le compte: ")),
		"income": 0,
		"bank": "HexaBank",
		"digicode_hash": bcrypt.hashpw(input("Digicode: ").encode(), salt).decode()
	}

	bf.save_account(acc)
	print()

ids = [
	"1", "2", "3", "4", "5", "6", "7",
	"101", "102", "103", "104", "105", "106",
	"BDF22789F400050", "F7DB60DD1C4300A", "A5FBDCE1D000078", "B40AC2137440001", "BC5905AE5D0001E"
]

for id in ids:
	save_acc(id)