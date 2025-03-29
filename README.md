![Bannière de Nation DB](./assets/banner.png)

# Nation DB

Ce repo est le code source de Nation, c'est là que TOUT repose. C'est ici que les bots viennent piocher leurs infos, c'est ici qu'est votre clone.


## Avantages de Nation DB

Avant Nation DB, on était pliés à la volonté des plateformes qui hébergeaient nos données. Si ils voulaient nous faire payer, on avait pas le choix. Maintenant, on peut contrôler qui accède à nos données et quand, et surtout, les limites font partie du passé !

## Créer sa propre instance

C'est très simple ne vous inquiétez pas ! D'abord assurez-vous d'avoir un fichier `.env` dans votre cwd (dossier courant) avec les champs ci-dessous renseignés:

```sh
BASEPATH=path/to/folder
DRIVEPATH=path/to/drive/folder
BACKUP=path/to/backup/folder

APP_HOST=0.0.0.0
APP_PORT=8000
APP_URL=http://localhost:8000
```

Les trois derniers champs ne sont pas obligatoires, ils servent de référence seulement. Le script de démarrage choisit par défaut de démarrer le serveur sur `http://localhost:8000` (`5000` en mode dev) mais les valeurs peuvent être changées dans le fichier `./scripts/start.sh` ou `./scripts/start.ps1` suivant votre environnement.

### 1. Une fois votre `.env` prêt, initialisez la db

C'est pas une surprise que sans base de données, le serveur ne peut pas fonctionner. Il vous faudra donc l'initialiser. Si vous êtes dans un terminal bash, il vous suffit d'exécuter la commande suivante:

```sh
source scripts/init.sh
```

Si vous êtes dans un environnement PowerShell, il vous faudra directement run le fichier Python qui réinitialisera le dossier de la database:

```py
python -m scripts.reset
```

### 2. Créez un compte superadmin

> Vous pouvez à tout moment laisser la database en l'état en appuyant sur [CTRL + C]. Cela reste très déconseillé car vous perdrez tout droit d'accès à la database via le serveur.

Une fois l'étape 1 terminée, le processus de création d'un compte superadmin sera automatiquement lancé. Vous devrez renseigner 2 champs:

**Nom d'utilisateur:** Une suite de caractères ne pouvant comprendre que des lettres __minuscules__*, des chiffres et le symbole "."
**Mot de passe:** Une série de caractères, la seule condition est d'en mettre au moins 8.

> Il est conseillé d'écrire ces deux valeurs dans le fichier .env __puis__ de les copier dans le terminal afin de ne pas les perdre.

Après ça, la database sera prête à l'emploi. Vous recevrez une réponse qui ressemble à ceci:

```
Nom d'utilisateur: pingouin2008
ID Session: 114213332844544
ID Utilisateur: 11625D9061021010
Token: FD2$gO.nG9rFwzK2sFNaPLyqp2R.6t8WRg8FJDF5UtSlF0CVZ6oUc88l7Rwsc1bRQYnWSXytfDyOcASX0NU
```

Vous n'avez plus qu'à copier le token (osef du reste) dans votre fichier `.env` et le tour est joué !

### 3. Démarrer le serveur

Une fois la base de données prête, il ne vous reste plus qu'à démarrer le serveur. Pour cela, vous avez le choix de le démarrer en mode dev:

**Bash:**
```sh
source scripts/dev.sh
```

**PowerShell:**
```ps1
.\scripts\dev
```

Si vous le démarrez en mode dev, il sera accessible à l'URL http://localhost:5000

Sinon, vous pouvez le démarrer en production-ready:

**Bash:**
```sh
source ./scripts/start.sh
```

**PowerShell:**
```ps1
.\scripts\start
```

Dans ce cas, le serveur sera accessible par défaut à l'URL http://localhost:8000, sauf si vous avez changé la configuration.

### 4. Configurez NSArchive

La configuration de NSArchive peut être présente [ici](https://github.com/1nserv/nsarchive/README.md)