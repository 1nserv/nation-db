source .venv/Scripts/Activate

if [ ! -d .local ]; then
	echo "Création du dossier .local ..."
	mkdir ".local"
fi

if [ ! -f .env ]; then
	echo "Création du .env ..."
	touch .env
fi

clear

py -m scripts.reset

py -m scripts.reset.init_admins
py -m scripts.reset.init_bots
py -m scripts.reset.init_departments
py -m scripts.reset.init_institutions
py -m scripts.reset.init_positions

py -m scripts.reset.economy.init_accounts
py -m scripts.reset.economy.init_inventories
py -m scripts.reset.economy.init_items

clear