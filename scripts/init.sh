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
clear