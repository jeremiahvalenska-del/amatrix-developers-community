from argon2 import PasswordHasher
import sqlite3, json, os, secrets
ph=PasswordHasher()
conn=sqlite3.connect('amatrix.db')
cur=conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, nom TEXT, telephone TEXT UNIQUE, password_hash TEXT, role TEXT, active INTEGER, derniere_connexion TEXT, perms TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS membres (id INTEGER PRIMARY KEY, nom TEXT, pays TEXT, ville TEXT, gmail TEXT, telephone TEXT, statut TEXT, date_inscription TEXT DEFAULT CURRENT_TIMESTAMP, visibilite TEXT, photo TEXT, poste TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS historique (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER, action TEXT, date TEXT DEFAULT CURRENT_TIMESTAMP, resultat TEXT)")
# Codes provisoires sécurisés - JAMAIS en clair dans code source final
# Matrix333 doit être changé avant prod
codes={
1: os.environ.get('FONDATEUR_CODE','Matrix333_TEMP_CHANGE_ME'),
2: secrets.token_urlsafe(10),
3: secrets.token_urlsafe(10),
4: secrets.token_urlsafe(10),
5: secrets.token_urlsafe(10),
}
admins=[
(1,"Akaza Valenska","+243833576117",ph.hash(codes[1]),"Fondateur principal — Super administrateur",1,None,json.dumps({f"perm_{i}":True for i in range(1,21)})),
(2,"Mr Reddington","+243992083817",ph.hash(codes[2]),"Administrateur secondaire",1,None,json.dumps({"dashboard":True})),
(3,"Rowan","+243851395271",ph.hash(codes[3]),"Administrateur secondaire",1,None,json.dumps({})),
(4,"KIYOTΔKΔ✞SUPREME AP¹","+243900771226",ph.hash(codes[4]),"Administrateur secondaire",1,None,json.dumps({})),
(5,"KRÜGER J A P","+243816482446",ph.hash(codes[5]),"Administrateur secondaire",1,None,json.dumps({})),
]
for a in admins: cur.execute("INSERT OR REPLACE INTO admins VALUES (?,?,?,?,?,?,?,?)",a)
conn.commit(); conn.close()
print("✅ DB 5 admins créée - Argon2id")
print("⚠️ CODES CONFIDENTIELS - Transmettre en privé puis supprimer ce fichier:")
for k,v in codes.items(): print(f"Admin {k}: {v}")
print("\n🔴 FONDATEUR: Matrix333 TEMPORAIRE - change via /api/change-password avant prod!")
