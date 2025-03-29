import hashlib
import os
import random
import shutil
import sqlite3
import time

import utils.db as db

dbpath = db.dbpath
logpath = db.logpath
drivepath = db.drivepath

if os.path.exists(dbpath):
    shutil.rmtree(dbpath)

os.makedirs(dbpath)

if os.path.exists(drivepath):
    shutil.rmtree(drivepath)

os.makedirs(os.path.join(drivepath, "entities"))
os.makedirs(os.path.join(drivepath, "files"))

if not os.path.exists(logpath):
    os.makedirs(os.path.join(logpath, "auth"))
    os.makedirs(os.path.join(logpath, "admin"))
    os.makedirs(os.path.join(logpath, "entities"))
    os.makedirs(os.path.join(logpath, "economy"))
    os.makedirs(os.path.join(logpath, "republic"))


with sqlite3.connect(os.path.join(dbpath, 'auth.db')) as auth:
    auth.execute("""CREATE TABLE Sessions (
        id TEXT PRIMARY KEY NOT NULL,
        token CHAR(256) UNIQUE NOT NULL,
        author TEXT NOT NULL
    );""")

    auth.execute("""CREATE TABLE Accounts (
        id TEXT PRIMARY KEY NOT NULL,
        pwd TEXT NOT NULL,
        author_id TEXT UNIQUE NOT NULL
    );""")

    auth.commit()


with sqlite3.connect(os.path.join(dbpath, 'entities.db')) as entities:
    entities.execute("""CREATE TABLE Positions (
        id TEXT PRIMARY KEY NOT NULL,
        name VARCHAR(32) UNIQUE NOT NULL,
        category TEXT,
        permissions TEXT NOT NULL,
        manager_permissions TEXT NOT NULL,
        FOREIGN KEY (category) REFERENCES Positions(id)
    );""")

    entities.execute("""CREATE TABLE Individuals (
        id TEXT PRIMARY KEY NOT NULL,
        name VARCHAR(32) UNIQUE NOT NULL,
        position TEXT NOT NULL,
        register_date INTEGER NOT NULL,
        xp INTEGER NOT NULL,
        boosts TEXT NOT NULL,
        additional TEXT NOT NULL,
        votes TEXT NOT NULL,
        FOREIGN KEY (position) REFERENCES Positions(id)
    );""")

    entities.execute("""CREATE TABLE Organizations (
        id TEXT PRIMARY KEY NOT NULL,
        name VARCHAR(32) UNIQUE NOT NULL,
        position TEXT NOT NULL,
        register_date INTEGER NOT NULL,
        owner_id TEXT NOT NULL,
        members TEXT NOT NULL,
        invites TEXT NOT NULL,
        certifications TEXT NOT NULL,
        additional TEXT NOT NULL,
        FOREIGN KEY (position) REFERENCES Positions(id)
        FOREIGN KEY (owner_id) REFERENCES Individuals(id)
    );""")

    entities.commit()


with sqlite3.connect(os.path.join(dbpath, 'marketplace.db')) as economy:
    economy.execute("""CREATE TABLE Banks (
        org_id TEXT PRIMARY KEY NOT NULL,
        name TEXT UNIQUE NOT NULL,
        url TEXT UNIQUE NOT NULL,
        hash TEXT UNIQUE NOT NULL
    );""")

    economy.execute("""CREATE TABLE Accounts (
        id TEXT PRIMARY KEY NOT NULL,
        owner_id TEXT NOT NULL,
        tag TEXT NOT NULL,
        frozen INTEGER NOT NULL,
        flagged INTEGER NOT NULL,
        register_date INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        income INTEGER NOT NULL,
        bank TEXT NOT NULL,
        digicode_hash TEXT NOT NULL,
        FOREIGN KEY (bank) REFERENCES Banks(name)
    );""")

    economy.execute("""CREATE TABLE Loans (
        id TEXT PRIMARY KEY NOT NULL,
        author_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        tag TEXT NOT NULL,
        frozen INTEGER NOT NULL,
        register_date INTEGER NOT NULL,
        expires INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        is_percentage INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
        last INTEGER NOT NULL
    );""")

    economy.execute("""CREATE TABLE Items (
        id TEXT PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        emoji TEXT NOT NULL,
        category TEXT NOT NULL,
        craft TEXT NOT NULL
    );""")

    economy.execute("""CREATE TABLE Sales (
        id TEXT PRIMARY KEY NOT NULL,
        item_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price INTEGER NOT NULL, 
        seller_id TEXT NOT NULL,
        FOREIGN KEY (item_id) REFERENCES Items(id),
        FOREIGN KEY (seller_id) REFERENCES Accounts(id)
    );""")

    economy.execute("""CREATE TABLE Inventories (
        id TEXT PRIMARY KEY NOT NULL,
        owner_id TEXT NOT NULL,
        tag TEXT NOT NULL,
        register_date INTEGER NOT NULL,
        items TEXT NOT NULL,
        digicode_hash TEXT NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES Accounts(id)
    );""")

    economy.commit()


with sqlite3.connect(os.path.join(dbpath, 'republic.db')) as republic:
    republic.execute("""CREATE TABLE Votes (
        id TEXT PRIMARY KEY NOT NULL,
        title TEXT NOT NULL,
        choices TEXT NOT NULL,
        author TEXT NOT NULL
    );""")

    republic.execute("""CREATE TABLE Elections (
        id TEXT PRIMARY KEY NOT NULL,
        candidates TEXT NOT NULL,
        vote TEXT NOT NULL,
        FOREIGN KEY (vote) REFERENCES Votes(id)
    );""")

    republic.commit()

with open(
        os.path.join(os.curdir, "assets/default_avatar.png"), 
        'rb'
    ) as _buffer, open(
        os.path.join(db.drivepath, "entities/0"),
        'wb'
    ) as _target:

    _target.write(_buffer.read())

from utils.functions import entities
from utils.functions import auth

from scripts.reset import init_admins, init_positions, init_departments, init_institutions

entities.save_position({
    "id": "superadmin",
    "name": "SuperAdmin",
    "category": "admin",
    "permissions": { "database": "amer" },
    "manager_permissions": {}
})

entities.save_position({
    "id": "admin",
    "name": "Administrateur",
    "category": "officier",
    "permissions": {
        "bots": "amer",
        "constitution": "ame-",
        "inventories": "amer",
        "items": "amer",
        "laws": "----",
        "loans": "amer",
        "members": "amer",
        "mines": "amer",
        "money": "amer",
        "national_channel": "ame-",
        "organizations": "amer",
        "reports": "amer",
        "sales": "amer",
        "state_budgets": "---r",
        "votes": "am-r"
    },
    "manager_permissions": {
        "database": "ame-"
    }
})


entities.save_individual({
    "id": hex(1252666521046618128)[2:].upper(),
    "name": "Père Fondateur",
    "position": "superadmin",
    "register_date": 0,
    "xp": 0,
    "boosts": {},
    "additional": {},
    "votes": []
})

# =============== Génération de la session superadmin ================

from utils.functions import entities
from utils.functions import auth

def create_account(id: int):
    id = hex(id)[2:].upper()
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$."
    token = ''.join([ charset[random.randint(0, 63)] for _ in range(256) ])

    session = {
        "id": round(time.time()) * 16 ** 4,
        "token": token,
        "author": id
    }

    auth.save_session(session)

    def is_safe(login: str) -> bool:
        for char in login:
            if char.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789.":
                return False

        return True

    usn = input("Nom d'utilisateur: ")
    while not is_safe(usn):
        os.system('clear')
        print("Le nom d'utilisateur ne peut contenir que des lettres (A-Z a-z), des chiffres (0-9) ou des points (.)")
        usn = input("Nom d'utilisateur: ")

    os.system('clear')
    print("\033[1;31mLe mot de passe sera visible à l'écran: Veillez à le taper à l'abri des regards !\033[0m")

    pwd = input("Mot de passe: ")
    while len(pwd) < 8:
        os.system('clear')
        print("Le mot de passe doit faire au moins 8 caractères.")
        pwd = input("Mot de passe: ")

    pwd = hashlib.sha256(pwd.encode()).hexdigest()

    auth.save_account({
        "id": usn,
        "pwd": pwd,
        "author_id": id
    })

    print("Nom d'utilisateur:\033[1;34m", usn, "\033[0m")
    print("ID Session:\033[1;34m", session["id"], "\033[0m")
    print("ID d'enregistrement:\033[1;34m", id, "\033[0m")
    print()
    print("Token:\033[1;34m\n", token, "\033[0m", sep = "")
    print()

create_account(1252666521046618128)
input("Pressez [ENTRÉE] pour continuer.")