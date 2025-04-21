from utils.functions import economy as bf

def save_item(id: str):
	print(f"\033[1;34m== Initialisation pour {id} ==\033[0m")
	item = {
		"id": id,
		"name": input("Name: "),
		"emoji": input("Emoji: "),
		"category": input("Category: "),
		"craft": {},
	}

	bf.save_item(item)
	print()

ids = [
	"1", "2", "3", "4"
]

for id in ids:
	save_item(id)