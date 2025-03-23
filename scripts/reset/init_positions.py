from utils.functions import entities as ef

ef.delete_position('member')
ef.delete_position('citoyen')
ef.delete_position('officiel')

ef.delete_position('group')
ef.delete_position('parti')
ef.delete_position('commerce')

ef.delete_position('institution')
ef.delete_position('conseil_constitutionnel')
ef.delete_position('gouvernement')
ef.delete_position('tribunal')
ef.delete_position('assemblee')
ef.delete_position('commissariat')
ef.delete_position('hexabank')
ef.delete_position('archives')

position = {
	"id": "member",
	"name": "Membre",
	"category": None,
	"permissions": {
		"bots": "----",
		"constitution": "----",
		"database": "----",
		"inventories": "----",
		"items": "----",
		"laws": "----",
		"loans": "----",
		"members": "----",
		"mines": "----",
		"money": "----",
		"national_channel": "----",
		"organizations": "----",
		"reports": "a---",
		"sales": "----",
		"state_budgets": "----",
		"votes": "----"
	},
	"manager_permissions": {
		"members": "-m--"
	}
}

ef.save_position(position)

position = {
	"id": "citoyen",
	"name": "Citoyen",
	"category": "member",
	"permissions": {
		"bots": "----",
		"constitution": "----",
		"database": "----",
		"inventories": "a---",
		"items": "---r",
		"laws": "----",
		"loans": "----",
		"members": "---r",
		"mines": "---r",
		"money": "----",
		"national_channel": "----",
		"organizations": "a--r",
		"reports": "a---",
		"sales": "a--r",
		"state_budgets": "----",
		"votes": "----"
	},
	"manager_permissions": {}
}

position = {
	"id": "officier",
	"name": "Officier",
	"category": "citoyen",
	"permissions": {
		"members": "-me-"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)



# ========== GROUPES ==========

position = {
	"id": "group",
	"name": "Groupe",
	"category": None,
	"permissions": {
		"bots": "----",
		"constitution": "----",
		"database": "----",
		"inventories": "----",
		"items": "---r",
		"laws": "----",
		"loans": "----",
		"members": "----",
		"mines": "----",
		"money": "----",
		"national_channel": "----",
		"organizations": "a---",
		"reports": "a---",
		"sales": "---r",
		"state_budgets": "----",
		"votes": "----"
	},
	"manager_permissions": {
		"organizations": "-m--"
	}
}

ef.save_position(position)

position = {
	"id": "parti",
	"name": "Parti",
	"category": "group",
	"permissions": {
		"inventories": "a---",
		"items": "a--r",
		"organizations": "a---",
		"sales": "a--r"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "commerce",
	"name": "Commerce",
	"category": "group",
	"permissions": {
		"inventories": "a---",
		"items": "a--r",
		"sales": "a--r"
	},
	"manager_permissions": {}
}

ef.save_position(position)



# ========== INSTITUTIONS ==========

position = {
	"id": "institution",
	"name": "Institution",
	"category": "group",
	"permissions": {
		"inventories": "a---",
		"items": "a--r",
		"laws": "a---",
		"members": "---r",
		"organizations": "---r"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "conseil_constitutionnel",
	"name": "Conseil Constitutionnel",
	"category": "institution",
	"permissions": {
		"bots": "ame-",
		"constitution": "ame-",
		"items": "---r",
		"laws": "ame-",
		"state_budgets": "ame-",
		"votes": "amer"
	},
	"manager_permissions": {}
}

ef.save_position(position)

position = {
	"id": "gouvernement",
	"name": "Gouvernement",
	"category": "institution",
	"permissions": {
		"bots": "ame-",
		"constitution": "a---",
		"inventories": "a---",
		"laws": "a---",
		"loans": "amer",
		"national_channel": "ame-",
		"state_budgets": "a---"
	},
	"manager_permissions": {}
}

ef.save_position(position)

position = {
	"id": "tribunal",
	"name": "Tribunal",
	"category": "institution",
	"permissions": {
		"database": "---r",
		"inventories": "--er",
		"items": "-mer",
		"loans": "amer",
		"members": "-me-",
		"organizations": "ame-",
		"reports": "---r",
		"state_budgets": "-me-",
		"votes": "---r"
	},
	"manager_permissions": {}
}

ef.save_position(position)

position = {
	"id": "commissariat",
	"name": "Commissariat",
	"category": "institution",
	"permissions": {
		"inventories": "--er",
		"items": "-me-",
		"loans": "amer",
		"members": "-me-",
		"organizations": "ame-",
		"reports": "-mer"
	},
	"manager_permissions": {}
}

ef.save_position(position)

position = {
	"id": "hexabank",
	"name": "Hexabank",
	"category": "institution",
	"permissions": {
		"inventories": "amer",
		"items": "amer",
		"loans": "amer",
		"mines": "ame-",
		"money": "ame-"
	},
	"manager_permissions": {}
}

ef.save_position(position)

position = {
	"id": "archives",
	"name": "Archives",
	"category": "institution",
	"permissions": {
		"database": "---r"
	},
	"manager_permissions": {}
}

ef.save_position(position)