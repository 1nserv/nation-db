from utils.functions import entities as ef

ef.delete_organization('101')
ef.delete_organization('102')
ef.delete_organization('103')
ef.delete_organization('104')
ef.delete_organization('105')
ef.delete_organization('106')


group = {
	"id": "101",
	"name": "Département des Maintenances",
	"position": "department",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "102",
	"name": "Département de l'Audiovisuel",
	"position": "department",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "103",
	"name": "Commission Électorale",
	"position": "commission",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "104",
	"name": "Département des Finances",
	"position": "department",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "105",
	"name": "Département de l'Égalité",
	"position": "department",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "106",
	"name": "Département de la Répression des Fraudes",
	"position": "department",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {
		"officiel": 0
	},
	"additional": {},
	"invites": []
}

res = ef.save_organization(group)