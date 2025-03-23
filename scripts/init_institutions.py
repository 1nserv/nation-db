from utils.functions import entities as ef

ef.delete_organization('1')
ef.delete_organization('2')
ef.delete_organization('3')
ef.delete_organization('4')
ef.delete_organization('5')
ef.delete_organization('6')
ef.delete_organization('7')


group = {
	"id": "1",
	"name": "Conseil Constitutionnel",
	"position": "conseil_constitutionnel",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [
		{
			"id": "BDF22789F400050",
			"level": {
				"general": 0
			}
		},
		{
			"id": "F7DB60DD1C4300A",
			"level": {
				"general": 0
			}
		},
		{
			"id": "A5FBDCE1D000078",
			"level": {
				"general": 0
			}
		},
		{
			"id": "BC5905AE5D0001E",
			"level": {
				"general": 0
			}
		}
	],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "2",
	"name": "Gouvernement",
	"position": "gouvernement",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "3",
	"name": "Tribunal",
	"position": "tribunal",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "4",
	"name": "Assemblée Nationale",
	"position": "assemblee",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "5",
	"name": "Commissariat",
	"position": "commissariat",
	"register_date": 0,
	"owner_id": "11625D9061021010",
	"members": [],
	"certifications": {},
	"additional": {},
	"invites": []
}

ef.save_organization(group)

group = {
	"id": "6",
	"name": "Hexabank",
	"position": "hexabank",
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

group = {
	"id": "7",
	"name": "Archives",
	"position": "archives",
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