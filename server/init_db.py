import sqlite3, json, os
from argon2 import PasswordHasher
ph = PasswordHasher()
codes = {
  1: "Matrix333",
  2: "Redmond8274!K",
  3: "Rowan6392!M",
  4: "Kiyota5186!R",
  5: "Kruger7943!V"
}
admins_data = [
 (1, "༺༻DEV 𝑨𝒌𝒂𝒛𝒂 𝑽𝒂𝒍𝒆𝒏𝒔𝒌𝒂 ༺ap1", "+243992083817", codes[1], "👑 Fondateur principal — tous les droits", 1),
 (2, "𝐦𝐫 𝐫𝐞𝐝𝐝𝐢𝐧𝐠𝐭𝐨𝐧", "+243851395271", codes[2], "💼 Responsable Validation & Gestion Membres", 1),
 (3, "ROWAN", "+243900771226", codes[3], "👥 Gestionnaire Communauté & Recrutement", 1),
 (4, "𝐊𝐈𝐘𝐎𝐓Δ𝐊Δ✞𝐒𝐔𝐏𝐑𝐄𝐌𝐄≛⃝ 𝐀𝐏¹", "+243816482446", codes[4], "⚙️ Administrateur Technique & Statistiques", 1),
 (5, "𝐊𝐑𝐔̈𝐆𝐄𝐑༄𝘿᭄⋆𝐉𝐀𝐏", "+243833576117", codes[5], "🎯 Recruteur & Validation Technique", 1),
]
DB = os.path.join(os.path.dirname(__file__), 'amatrix.db')
conn = sqlite3.connect(DB)
cur = conn.cursor()
for t in ["admins","membres","historique","communities","texts"]: cur.execute(f"DROP TABLE IF EXISTS {t}")
cur.execute("CREATE TABLE admins (id INTEGER PRIMARY KEY, nom TEXT UNIQUE, numero TEXT, password_hash TEXT, role TEXT, active INTEGER, permissions TEXT, derniere_connexion TEXT, photo TEXT)")
cur.execute("CREATE TABLE membres (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, age TEXT, villepays TEXT, whatsapp TEXT, gmail TEXT, numero TEXT, niveau TEXT, langages TEXT, acquises TEXT, aapprendre TEXT, outils TEXT, projets TEXT, liens TEXT, techno TEXT, pourquoi TEXT, objectifs TEXT, heures TEXT, signature TEXT, date TEXT, statut TEXT, visibility TEXT, photo TEXT, pays TEXT, ville TEXT)")
cur.execute("CREATE TABLE historique (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT DEFAULT CURRENT_TIMESTAMP, admin_id INTEGER, action TEXT, resultat TEXT)")
cur.execute("CREATE TABLE communities (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, nom TEXT, lien TEXT, photo TEXT, description TEXT, active INTEGER DEFAULT 1, date TEXT DEFAULT CURRENT_TIMESTAMP)")
cur.execute("CREATE TABLE texts (key TEXT PRIMARY KEY, value TEXT)")
perms_founder = json.dumps({"dashboard":True,"viewMembers":True,"viewPrivate":True,"editProfiles":True,"suspend":True,"deleteAccount":True,"manageAdmins":True,"editPerms":True,"security":True,"manageTexts":True,"manageCommunities":True})
perms_others = [
 json.dumps({"dashboard":True,"viewMembers":True,"viewPrivate":True,"editProfiles":True,"suspend":True,"deleteAccount":False,"manageAdmins":False,"editPerms":False,"security":False,"manageTexts":False,"manageCommunities":False}),
 json.dumps({"dashboard":True,"viewMembers":True,"viewPrivate":False,"editProfiles":True,"suspend":True,"deleteAccount":False,"manageAdmins":False,"editPerms":False,"security":False,"manageTexts":False,"manageCommunities":False}),
 json.dumps({"dashboard":True,"viewMembers":True,"viewPrivate":False,"editProfiles":False,"suspend":False,"deleteAccount":False,"manageAdmins":False,"editPerms":False,"security":True,"manageTexts":False,"manageCommunities":True}),
 json.dumps({"dashboard":False,"viewMembers":True,"viewPrivate":True,"editProfiles":True,"suspend":False,"deleteAccount":False,"manageAdmins":False,"editPerms":False,"security":False,"manageTexts":False,"manageCommunities":False}),
]
for i,a in enumerate(admins_data):
  aid,nom,num,code,role,active = a
  perm = perms_founder if i==0 else perms_others[i-1]
  cur.execute("INSERT INTO admins VALUES (?,?,?,?,?,?,?,?)",(aid,nom,num,ph.hash(code),role,active,perm,""))
cur.execute("INSERT INTO texts VALUES (?,?)", ("main_phrase","Le talent se développe par la pratique."))
cur.execute("INSERT INTO texts VALUES (?,?)", ("community_desc","AMATRIX Developers Community - Recrutement ouvert"))
cur.execute("INSERT INTO texts VALUES (?,?)", ("admin_welcome","Bienvenue dans l'espace administration"))
cur.execute("INSERT INTO communities (type,nom,lien,description) VALUES (?,?,?,?)", ("channel","AMATRIX DEVELOPERS HUB","https://whatsapp.com/channel/0029VbDMH24FSAtCHZ5smv20","Chaîne officielle"))
cur.execute("INSERT INTO communities (type,nom,lien,description) VALUES (?,?,?,?)", ("group","Groupe Recrutement","https://chat.whatsapp.com/CYcNxrmW7lH6XrLRU20hxS","Groupe officiel"))
conn.commit(); conn.close()
print("✅ DB V-FINAL créée")
for k,v in codes.items(): print(f"Admin {k}: {v}")
