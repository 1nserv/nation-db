from utils.functions import entities as ef

ef.delete_position('member')
ef.delete_position('citoyen')
ef.delete_position('bot')
ef.delete_position('officier')
ef.delete_position('officier_etat')
ef.delete_position('gd_officier_etat')
ef.delete_position('garant')

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


# ========== BASE ==========

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

ef.save_position(position)

position = {
	"id": "bot",
	"name": "Bot Officiel",
	"category": None,
	"permissions": {
		"database": "amer"
	},
	"manager_permissions": {}
}

ef.save_position(position)


# ========== OFFICIERS ==========

position = {
	"id": "officier",
	"name": "Officier",
	"category": "citoyen",
	"permissions": {
		"reports": "---r",
		"sanctions": "---r"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "avocat",
	"name": "Avocat",
	"category": "officier",
	"permissions": {
		"reports": "-m--"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "moderateur",
	"name": "Modérateur",
	"category": "officier",
	"permissions": {
		"reports": "-m--",
		"sanctions": "a---"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

# ========== OFFICIERS D'ÉTAT ==========

position = {
	"id": "officier_etat",
	"name": "Officier d'État",
	"category": "officier",
	"permissions": {
		"database": "---r"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "repr",
	"name": "Député",
	"category": "officier_etat",
	"permissions": {
		"laws": "-m--"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "judge",
	"name": "Juge",
	"category": "officier_etat",
	"permissions": {
		"reports": "-m--",
		"sanctions": "-me-"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

# ========== GRANDS OFFICIERS D'ÉTAT ==========

position = {
	"id": "gd_officier_etat",
	"name": "Grand Officier d'État",
	"category": "officier_etat",
	"permissions": {
		"state_budgets": "---r"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "pre_an",
	"name": "Président de l'Assemblée Nationale",
	"category": "gd_officier_etat",
	"permissions": {
		"votes": "a---"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "ministre",
	"name": "Ministre",
	"category": "gd_officier_etat",
	"permissions": {
		"bots": "-me-",
		"laws": "ame-"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

# ========== GARANTS DE LA CONSTITUTION ==========

position = {
	"id": "garant",
	"name": "Garant de la Constitution",
	"category": "gd_officier_etat",
	"permissions": {
		"constitution": "--e-",
		"laws": "ame-",
		"national_channel": "ame-",
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "pre_rep",
	"name": "Président de la République",
	"category": "garant",
	"permissions": {
		"state_budgets": "ame-"
	},
	"manager_permissions": {
		"constitution": "--e-"
	}
}

ef.save_position(position)

position = {
	"id": "sage",
	"name": "Sage",
	"category": "garant",
	"permissions": {
		"database": "amer",
		"money": "a---"
	},
	"manager_permissions": {}
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
	"id": "department",
	"name": "Ministère",
	"category": "group",
	"permissions": {
		"inventories": "a---",
		"items": "a--r",
		"laws": "a---",
		"members": "---r",
		"organizations": "---r"
	},
	"manager_permissions": {
		"state_budgets": "--e-"
	}
}

ef.save_position(position)

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
		"money": "a---"
	},
	"manager_permissions": {}
}

ef.save_position(position)