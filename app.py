import os, sqlite3, datetime, uuid, urllib.parse, base64
from flask import Flask, request, render_template_string, redirect, session, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'amatrix-final-vocal-fix'
DATABASE='amatrix.db'
CODE_ADMIN_MODIF = "AMATRIX999PRO"

def get_logo_uri_default():
    for p in ["static/logo.png", "/mnt/data/wa_image_7133823538203423842"]:
        if os.path.exists(p):
            try:
                with open(p,"rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                return f"data:image/jpeg;base64,{b64}"
            except:
                pass
    return "/static/logo.png"
LOGO_DEFAULT = get_logo_uri_default()

DEFAULT_SETTINGS = {
    "general_logo": "", "cercle1_logo": "", "cercle2_logo": "", "cercle3_logo": "",
    "feature_accueil": "active", "feature_inscription": "active", "feature_membres": "active", "feature_annonces": "active", "feature_apropos": "active", "feature_assistance": "active", "feature_cercles": "active",
    "hero_badge": "Bienvenue dans AMATRIX community",
    "hero_title": "Construis ton<br><b>avenir avec nous</b>",
    "hero_desc": "Communaute dynamique pour creer applications, sites web, plateformes et Marketplace.",
    "hero_btn": "S'inscrire maintenant →",
    "hero_image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
    "hero_blur1": "💻 CODE • HTML • CSS", "hero_blur2": "⚡ AMATRIX DEV", "hero_blur3": "🛒 Marketplace • SaaS", "hero_blur4": "📱 Apps • Python • Firebase",
    "hero_hand": "Ensemble<br><b>plus loin !</b>",
    "cercle1_titre": "Chaine", "cercle1_icone": "A", "cercle1_btn": "S'ABONNER →", "cercle1_color": "linear-gradient(135deg,#00ff88,#00aaff)",
    "cercle2_titre": "Recrutement", "cercle2_icone": "NOUS<br>RECRUTONS", "cercle2_btn": "REJOINDRE →", "cercle2_color": "linear-gradient(135deg,#2a7bff,#00d4ff)",
    "cercle3_titre": "Communaute", "cercle3_icone": "COMMUNAUTE<br>DEV", "cercle3_btn": "REJOINDRE →", "cercle3_color": "linear-gradient(135deg,#00ff88,#00ff88)",
    "link_chaine": "https://whatsapp.com/channel/0029VbDMH24FSAtCHZ5smv20",
    "link_recrutement": "https://chat.whatsapp.com/CYcNxrmW7lH6XrLRU20hxS?s=cl&p=a&mlu=4&ilr=4",
    "link_communaute": "https://chat.whatsapp.com/K2fYZpLSk1a81qFKy3yNZN",
    "showcase_small": "NOS REALISATIONS", "showcase_title": "On code des <b>sites web</b>, des <b>apps</b> et des <b>Marketplace</b>",
    "showcase_desc": "Sites vitrines, SaaS, e-commerce, Marketplace avec Mobile Money RDC.",
    "showcase_image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
    "showcase_blur1": "🌐 Site Vitrine 50$", "showcase_blur2": "✅ Live", "showcase_blur3": "🛒 Marketplace + Mobile Money"
}

def get_db():
    db=getattr(g,'_database',None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
        db.row_factory=sqlite3.Row
    return db

def init_db():
    now=datetime.datetime.now().isoformat()
    db=sqlite3.connect(DATABASE)
    c=db.cursor()
    c.executescript("""
    DROP TABLE IF EXISTS candidatures;
    CREATE TABLE candidatures(
        id TEXT PRIMARY KEY, nom TEXT, age INTEGER, ville TEXT, pays TEXT, whatsapp TEXT,
        niveau TEXT, langages TEXT, competences TEXT, competences_ameliorer TEXT,
        outils TEXT, projets TEXT, liens_projets TEXT, techno_projets TEXT,
        motivation TEXT, objectifs TEXT, disponibilite TEXT,
        statut TEXT, created_at TEXT, pays_lower TEXT, ville_lower TEXT, photo TEXT
    );
    CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT);
    CREATE TABLE IF NOT EXISTS annonces(id TEXT PRIMARY KEY, titre TEXT, description TEXT, image TEXT, categorie TEXT, statut TEXT, date TEXT, prix TEXT, contact TEXT);
    CREATE TABLE IF NOT EXISTS assistance(id TEXT PRIMARY KEY, nom TEXT, whatsapp TEXT, message TEXT, date TEXT, type TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    """)
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users VALUES (?,?,?,?)",(str(uuid.uuid4()),'amatrix',generate_password_hash("AMATRIX999PRO"),'admin_principal'))
    for k,v in DEFAULT_SETTINGS.items():
        if not c.execute("SELECT * FROM settings WHERE key=?",(k,)).fetchone():
            c.execute("INSERT INTO settings VALUES (?,?)",(k,v))
    c.execute("DELETE FROM annonces")
    offres=[
        ("Site Vitrine Pro 50$", "Site vitrine complet 5 pages + domaine .com + hebergement 1 an + responsive + SEO. Livraison 7 jours. Paiement Mobile Money.", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80", "Promotion", "50$ - Promo", "+243 992083817"),
        ("Formation HTML CSS Python Debutant", "Formation 1 mois : HTML5, CSS3, Python bases, Firebase, Git. Projets reels : portfolio + site vitrine.", "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80", "Formation", "Gratuit pour membres", "+243 992083817"),
        ("App Marketplace Mobile Money RDC", "On developpe votre app marketplace comme Jumia avec paiement Airtel Money, Orange Money, M-Pesa.", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=800&q=80", "Marketplace", "Sur devis - 300$", "+243 992083817"),
        ("SaaS Gestion Stock Boutique", "Logiciel gestion stock, ventes, factures, clients. Mode offline.", "https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=800&q=80", "Information", "100$ / an", "+243 992083817"),
        ("Rejoins AMATRIX Dev Team", "Tu sais coder ? Rejoins notre equipe. Projets payes, formations avancees, clients reels.", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80", "Information", "Recrutement ouvert", "+243 992083817"),
    ]
    for t,d,img,cat,prix,cont in offres:
        c.execute("INSERT INTO annonces VALUES (?,?,?,?,?,?,?,?,?)",(str(uuid.uuid4()),t,d,img,cat,"publiee",now,prix,cont))
    db.commit(); db.close()

def get_settings():
    db=get_db()
    rows=db.execute("SELECT * FROM settings").fetchall()
    s={r['key']: r['value'] for r in rows}
    for k,v in DEFAULT_SETTINGS.items():
        if k not in s: s[k]=v
    return s

def get_stats():
    db=get_db()
    try:
        total=db.execute("SELECT COUNT(*) as c FROM candidatures").fetchone()['c']
        pays=db.execute("SELECT COUNT(DISTINCT pays_lower) as c FROM candidatures WHERE pays_lower!=''").fetchone()['c'] or 0
        villes=db.execute("SELECT COUNT(DISTINCT ville_lower) as c FROM candidatures WHERE ville_lower!=''").fetchone()['c'] or 0
        week=db.execute("SELECT COUNT(*) as c FROM candidatures WHERE created_at>=?",((datetime.datetime.now()-datetime.timedelta(days=7)).isoformat(),)).fetchone()['c'] or 0
    except: total=pays=villes=week=0
    return dict(total=total,pays=pays,villes=villes,week=week)

def get_logo_general(settings):
    gl = settings.get("general_logo","")
    if gl and gl.startswith("data:image"): return gl
    if gl and os.path.exists(gl.replace("/static/","static/")): return gl
    if os.path.exists("static/logo.png"): return "/static/logo.png"
    return LOGO_DEFAULT

def build_formulaire_complet(d):
    return f"""╔════════════════════════════╗
　💻 FORMULAIRE DE RECRUTEMENT
　👨‍💻 ÉQUIPE DE DÉVELOPPEMENT WEB
╚════════════════════════════╝
📌 INSTRUCTIONS
Merci de remplir ce formulaire avec des réponses précises et honnêtes.
━━━━━━━━━━━━━━━━━━
👤 01. INFORMATIONS PERSONNELLES
━━━━━━━━━━━━━━━━━━
🔹 Nom complet : {d.get('nom','')}
🔹 Âge : {d.get('age','')}
🔹 Ville / Pays : {d.get('ville','')} / {d.get('pays','')}
🔹 Contact WhatsApp : {d.get('whatsapp','')}
━━━━━━━━━━━━━━━━━━
⚙️ 02. PROFIL TECHNIQUE
━━━━━━━━━━━━━━━━━━
💻 Niveau : {d.get('niveau','')}
🛠️ Langages : {d.get('langages','')}
📚 Compétences acquises : {d.get('competences','')}
🎯 À améliorer : {d.get('competences_ameliorer','')}
🤖 Outils : {d.get('outils','')}
━━━━━━━━━━━━━━━━━━
🚀 03. PROJETS RÉALISÉS
━━━━━━━━━━━━━━━━━━
💻 Projets : {d.get('projets','')}
🔗 Liens : {d.get('liens_projets','')}
🛠️ Technos : {d.get('techno_projets','')}
━━━━━━━━━━━━━━━━━━
🎯 04. MOTIVATION & DISPONIBILITÉ
━━━━━━━━━━━━━━━━━━
🔥 Pourquoi : {d.get('motivation','')}
🎯 Objectifs : {d.get('objectifs','')}
⏳ Heures : {d.get('disponibilite','')}
━━━━━━━━━━━━━━━━━━
✅ 05. VALIDATION
━━━━━━━━━━━━━━━━━━
📝 Je confirme informations exactes.
👤 Nom : {d.get('nom_confirm','')}
╔════════════════════════════╗
　🚀 APPRENONS • CRÉONS • INNOVONS
╚════════════════════════════╝
ID: {d.get('id','')}
"""

BASE_CSS = """
<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
*{margin:0;padding:0;box-sizing:border-box}html,body{max-width:100%;overflow-x:hidden}body{font-family:system-ui,sans-serif;background:#f6f8ff}
header{background:#091a35;display:flex;align-items:center;justify-content:space-between;padding:10px 14px;position:sticky;top:0;z-index:200}
.logo{display:flex;align-items:center;gap:10px;color:#fff;font-weight:800}
.hamburger{font-size:20px;color:#fff;background:#0f2a52;padding:8px 12px;border-radius:10px;border:none}
.menu-drawer{position:fixed;top:0;right:-100%;width:85vw;max-width:340px;height:100vh;background:#0a1930;z-index:999;transition:0.3s;display:flex;flex-direction:column}
.menu-drawer.open{right:0}.drawer-top{background:#091a35;padding:16px;display:flex;justify-content:space-between;border-bottom:1px solid #112a52}
.close{font-size:22px;color:#8aa0c8;background:none;border:none}.drawer-body{padding:10px;overflow-y:auto;flex:1}
.menu-item{display:flex;align-items:center;gap:12px;padding:12px;border-radius:12px;color:#c2d3f0;text-decoration:none;font-size:13px;margin:4px 0}
.menu-item .ic{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-size:16px;flex-shrink:0}
.ic.green{background:linear-gradient(135deg,#00a36a,#00ff88);color:#002a1a}.ic.dark{background:#0f2a52;color:#8aa0c8}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:998;display:none}.overlay.show{display:block}
.hero{display:grid;grid-template-columns:1.05fr 0.95fr;min-height:520px;background:#081a3d;position:relative;overflow:hidden}
.hero-left{padding:36px 22px;z-index:2}.badge2{background:#112f5a;border:1px solid #1a4a7a;color:#b8d4f0;padding:6px 12px;border-radius:20px;font-size:11px;display:inline-block}
.hero h1{font-size:44px;line-height:1.05;color:#fff;font-weight:800;margin-top:14px} .hero h1 b{color:#00f0a0}.hero p{color:#b8c9e6;font-size:14px;margin-top:14px;max-width:440px;line-height:1.6}
.btn-green{background:#00c897;color:#002a1a;padding:13px 20px;border-radius:24px;font-weight:800;font-size:12px;text-decoration:none;display:inline-flex;margin-top:18px}
.hero-right{position:relative;background:#081a3d;min-height:520px;overflow:hidden;display:flex;align-items:center;justify-content:center}
.hero-right img{width:100%;height:100%;object-fit:cover;animation:floatComputer 3.5s ease-in-out infinite}
@keyframes floatComputer{0%,100%{transform:translateY(0)}50%{transform:translateY(-18px)}}
.hand{position:absolute;right:18px;bottom:28px;color:#fff;font-style:italic;transform:rotate(-8deg);font-size:20px;text-shadow:0 2px 12px rgba(0,0,0,0.8);z-index:3;background:rgba(0,0,0,0.25);padding:8px 14px;border-radius:14px;backdrop-filter:blur(6px)}
.blur-badge{position:absolute;z-index:4;background:rgba(0,0,0,0.35);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.18);color:#fff;padding:8px 12px;border-radius:12px;font-size:11px;font-weight:700;box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.cercles{background:#06142b;padding:30px 12px} .c-grid{max-width:1150px;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.c-item{text-align:center} .c-circle{width:210px;height:210px;border-radius:50%;display:grid;place-items:center;margin:0 auto 12px;padding:3px;overflow:hidden}
.c-inner{width:100%;height:100%;border-radius:50%;background:radial-gradient(circle at 50% 30%,#0f2a5a,#06142b);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;overflow:hidden}
.c-inner .bigA{font-size:42px;font-weight:900;text-align:center;line-height:1.1}
.btn-c{padding:8px 14px;border-radius:20px;font-size:11px;font-weight:700;color:#fff;text-decoration:none;display:inline-flex}.btn-c.g{background:#00a36a} .btn-c.b{background:#2a5bd7} .btn-c.p{background:#6a4ad9}
.showcase{background:#0a1930;padding:32px 14px}.showcase-inner{max-width:1150px;margin:0 auto;display:grid;grid-template-columns:1.1fr 0.9fr;gap:24px;align-items:center}
.showcase-text h2{font-size:28px;color:#fff;line-height:1.2} .showcase-text h2 b{color:#00f0a0}.showcase-text p{color:#8da1c7;font-size:13px;margin-top:10px;line-height:1.6}
.showcase-img{position:relative;border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);border:1px solid #1d3a6b}.showcase-img img{width:100%;height:340px;object-fit:cover;display:block;animation:floatComputer 4s ease-in-out infinite}
.impact{background:linear-gradient(180deg,#eaf1ff,#d9e8ff);padding:24px 14px;display:grid;grid-template-columns:1.2fr 1.8fr;gap:14px;max-width:1150px;margin:0 auto}
.stat{background:#fff;border-radius:12px;padding:14px;text-align:center;border:1px solid #d8e4ff} .stat b{font-size:22px;color:#0a1930;display:block}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.page{max-width:1100px;margin:0 auto;background:#fff;min-height:80vh;overflow-x:hidden}
.hero-photo{position:relative;height:340px;background-size:cover;background-position:center;display:flex;align-items:flex-end;overflow:hidden}
.hero-photo::after{content:'';position:absolute;inset:0;background:linear-gradient(0deg,rgba(6,20,43,0.92) 0%,rgba(6,20,43,0.4) 50%,rgba(6,20,43,0.1) 100%)}
.hero-photo-content{position:relative;z-index:2;padding:22px;color:#fff;width:100%}
.card{border:1px solid #d8e4ff;border-radius:14px;padding:14px;background:#fff;margin:8px 0;box-shadow:0 2px 10px rgba(42,91,215,0.06)}
.form-wrap{max-width:850px;margin:20px auto;background:#fff;border-radius:18px;padding:24px;border:1px solid #d8e4ff;box-shadow:0 8px 30px rgba(0,0,0,0.06);overflow:hidden}
.form-wrap label{font-size:12px;font-weight:800;display:block;margin:14px 0 5px;color:#0a1930}
.form-wrap input,.form-wrap select,.form-wrap textarea{width:100%;padding:12px;border-radius:12px;border:1px solid #c2d3f0;font-size:13px;max-width:100%;background:#fff;color:#0a1930}
.admin-card{background:#fff;border:1px solid #d8e4ff;border-radius:16px;padding:20px;margin:16px 0;box-shadow:0 4px 16px rgba(0,0,0,0.04)}
.member-card{background:#fff;border:1px solid #d8e4ff;border-radius:20px;overflow:hidden;box-shadow:0 8px 24px rgba(42,91,215,0.08)}
.member-top{height:90px;background:linear-gradient(135deg,#0a1930,#1a3a6a);position:relative}
.member-avatar{width:84px;height:84px;border-radius:50%;border:4px solid #fff;object-fit:cover;position:absolute;left:50%;bottom:-42px;transform:translateX(-50%)}
.member-body{padding:52px 16px 16px;text-align:center}.badge-level{padding:4px 10px;border-radius:20px;font-size:10px;font-weight:800;color:#fff;display:inline-block;margin-top:6px}
.badge-level.debutant{background:#2a5bd7}.member-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin-top:16px}
.glass-card{background:rgba(255,255,255,0.85);backdrop-filter:blur(12px);border:1px solid rgba(42,91,215,0.18);box-shadow:0 8px 24px rgba(42,91,215,0.12);border-radius:16px;padding:16px}
.vertical-stack{display:flex;flex-direction:column;gap:16px}
.admin-title{font-size:18px;font-weight:900;color:#0a1930;margin-bottom:4px}
.admin-desc{font-size:12px;color:#6b7aa0;line-height:1.5;margin-bottom:12px}
@media(max-width:900px){.hero{grid-template-columns:1fr}.c-grid{grid-template-columns:1fr}.impact{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.showcase-inner{grid-template-columns:1fr}.member-grid{grid-template-columns:1fr}}
</style>
"""

@app.before_request
def before(): g.db=get_db()
@app.teardown_appcontext
def close(e):
    db=getattr(g,'_database',None)
    if db: db.close()

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

def render_header(settings):
    logo = get_logo_general(settings)
    return f'''
<header>
  <div class="logo"><img src="{logo}" style="width:42px;height:42px;border-radius:10px;object-fit:cover;border:1.5px solid #00e5ff"><div>AMATRIX<br><small>community</small></div></div>
  <button class="hamburger" onclick="openMenu()">☰</button>
</header>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<div class="menu-drawer" id="drawer">
  <div class="drawer-top"><h3 style="color:#fff;display:flex;align-items:center;gap:10px"><img src="{logo}" style="width:32px;height:32px;border-radius:8px"> MENU</h3><button class="close" onclick="closeMenu()">✕</button></div>
  <div class="drawer-body">
    <a class="menu-item" href="/"><div class="ic dark">🏠</div><b>Accueil</b></a>
    <a class="menu-item" href="/form"><div class="ic green">📝</div><b>S'inscrire</b></a>
    <a class="menu-item" href="/membres"><div class="ic dark">👥</div><b>Membres</b></a>
    <a class="menu-item" href="/annonces"><div class="ic dark">📢</div><b>Annonces</b></a>
    <a class="menu-item" href="/apropos"><div class="ic dark">ℹ️</div><b>À propos</b></a>
    <a class="menu-item" href="/assistance"><div class="ic dark">🆘</div><b>Assistance</b></a>
    <a class="menu-item" href="/admin"><div class="ic dark">⚙️</div><b>Admin</b></a>
  </div>
</div>
<script>
function openMenu(){{document.getElementById("drawer").classList.add("open");document.getElementById("overlay").classList.add("show")}}
function closeMenu(){{document.getElementById("drawer").classList.remove("open");document.getElementById("overlay").classList.remove("show")}}
</script>
'''

@app.route('/')
def index():
    init_db(); st=get_settings(); s=get_stats(); logo=get_logo_general(st); header=render_header(st)
    c1_logo = st.get("cercle1_logo") or logo
    c2_logo = st.get("cercle2_logo") or logo
    c3_logo = st.get("cercle3_logo") or logo
    def circle_inner(l, fallback):
        return f'<img src="{l}" style="width:160px;height:160px;border-radius:50%;object-fit:cover;border:2px solid #00e5ff">' if l else f'<div class="bigA">{fallback}</div>'
    return render_template_string(BASE_CSS + header + f'''
<section class="hero"><div class="hero-left"><div class="badge2" style="display:flex;align-items:center;gap:8px"><img src="{logo}" style="width:22px;height:22px;border-radius:6px"> {st["hero_badge"]}</div><h1>{st["hero_title"]}</h1><p>{st["hero_desc"]}</p><a class="btn-green" href="/form">{st["hero_btn"]}</a></div><div class="hero-right"><img src="{st["hero_image"]}"><div class="blur-badge" style="top:20px;left:16px">{st["hero_blur1"]}</div><div class="blur-badge" style="top:56px;left:16px;background:rgba(0,200,151,0.25)">{st["hero_blur2"]}</div><div class="blur-badge" style="bottom:90px;left:16px">{st["hero_blur3"]}</div><div class="blur-badge" style="bottom:50px;left:16px;background:rgba(42,91,215,0.3)">{st["hero_blur4"]}</div><div class="hand">{st["hero_hand"]}</div></div></section>
<section class="cercles"><div class="c-grid">
<div class="c-item"><div class="c-circle" style="background:{st["cercle1_color"]}"><div class="c-inner">{circle_inner(c1_logo, st["cercle1_icone"])}</div></div><h3 style="color:#fff">{st["cercle1_titre"]}</h3><a class="btn-c g" href="{st["link_chaine"]}" target="_blank">{st["cercle1_btn"]}</a></div>
<div class="c-item"><div class="c-circle" style="background:{st["cercle2_color"]}"><div class="c-inner">{circle_inner(c2_logo, st["cercle2_icone"])}</div></div><h3 style="color:#fff">{st["cercle2_titre"]}</h3><a class="btn-c b" href="{st["link_recrutement"]}" target="_blank">{st["cercle2_btn"]}</a></div>
<div class="c-item"><div class="c-circle" style="background:{st["cercle3_color"]}"><div class="c-inner">{circle_inner(c3_logo, st["cercle3_icone"])}</div></div><h3 style="color:#fff">{st["cercle3_titre"]}</h3><a class="btn-c p" href="{st["link_communaute"]}" target="_blank">{st["cercle3_btn"]}</a></div>
</div></section>
<section class="showcase"><div class="showcase-inner"><div class="showcase-text"><small style="color:#00ff88;font-weight:700;display:flex;align-items:center;gap:8px"><img src="{logo}" style="width:20px;height:20px;border-radius:6px"> {st["showcase_small"]}</small><h2>{st["showcase_title"]}</h2><p>{st["showcase_desc"]}</p></div><div class="showcase-img"><img src="{st["showcase_image"]}"><div class="blur-badge" style="top:16px;left:12px">{st["showcase_blur1"]}</div><div class="blur-badge" style="top:16px;right:12px;background:rgba(0,200,151,0.25)">{st["showcase_blur2"]}</div><div class="blur-badge" style="bottom:16px;left:12px;right:12px;text-align:center;background:rgba(0,0,0,0.45)">{st["showcase_blur3"]}</div></div></div></section>
<section class="impact"><div><small style="color:#2a5bd7;font-weight:700">NOTRE IMPACT</small><h2 style="font-size:20px;color:#0a1930">Communaute</h2></div><div class="stats"><div class="stat"><b>{s["total"]}</b><small>Inscrits</small></div><div class="stat"><b>{s["pays"]}</b><small>Pays</small></div><div class="stat"><b>{s["villes"]}</b><small>Villes</small></div><div class="stat"><b>{s["week"]}</b><small>Semaine</small></div></div></section>
<footer style="background:#07142e;color:#7e90b2;padding:20px;text-align:center"><img src="{logo}" style="width:56px;height:56px;border-radius:50%;border:2px solid #00e5ff;margin-bottom:8px"><br><b style="color:#fff">AMATRIX DEVELOPERS COMMUNITY</b><br><small>© 2026</small></footer>
''')

@app.route('/form')
def form_page():
    init_db(); st=get_settings(); s=get_stats(); logo=get_logo_general(st); header=render_header(st)
    return render_template_string(BASE_CSS + header + f'''
<div class="page" style="max-width:850px">
  <div class="hero-photo" style="background-image:url('https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1200&q=80');height:320px"><div class="hero-photo-content"><div style="display:flex;align-items:center;gap:14px"><img src="{logo}" style="width:56px;height:56px;border-radius:12px"><div><h1>💻 Formulaire de Recrutement</h1><p>Rejoins {s["total"]} membres</p></div></div></div></div>
  <div class="form-wrap" style="margin-top:0;border-top-left-radius:0;border-top-right-radius:0">
    <div style="background:#0a1930;color:#e6fffa;padding:18px;border-radius:14px;text-align:center;font-family:monospace;font-size:12px;white-space:pre-wrap;line-height:1.5;margin-bottom:20px;display:flex;flex-direction:column;align-items:center;gap:10px"><img src="{logo}" style="width:72px;height:72px;border-radius:50%;border:2px solid #00e5ff">╔════════════════════════════╗
　💻 FORMULAIRE DE RECRUTEMENT
　👨‍💻 ÉQUIPE DE DÉVELOPPEMENT WEB
╚════════════════════════════╝
📌 INSTRUCTIONS
Merci de remplir ce formulaire avec des réponses précises et honnêtes.</div>
    <form method="POST" action="/form/preview" enctype="multipart/form-data">
      <div class="photo-wrap"><div style="font-weight:800;color:#0a1930">📸 Ta vraie photo (obligatoire)</div><img id="previewPhoto" class="photo-preview" src=""><input type="file" name="photo" id="photoInput" accept="image/*" required style="margin-top:8px"></div>
      <div class="card" style="border:1px solid #d8e4ff"><div style="background:#0a1930;color:#fff;padding:10px;border-radius:10px;font-weight:800">━━━━━━━━━━ 👤 01. INFORMATIONS PERSONNELLES ━━━━━━━━━━</div>
        <label>🔹 Nom complet :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="nom" required placeholder="Ex: Jeremiah">
        <label>🔹 Âge :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="age" type="number" required placeholder="Ex: 22">
        <label>🔹 Ville / Pays :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><input name="ville" required placeholder="Ex: Lubumbashi"><input name="pays" required placeholder="Ex: RDC"></div>
        <label>🔹 Contact WhatsApp :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="whatsapp" required placeholder="Ex: +243 992083817"></div>
      <div class="card"><div style="background:#0a1930;color:#fff;padding:10px;border-radius:10px;font-weight:800">━━━━━━━━━━ ⚙️ 02. PROFIL TECHNIQUE ━━━━━━━━━━</div>
        <label>💻 Niveau en développement web :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><select name="niveau" required><option>Debutant</option><option>Intermediaire</option><option>Professionnel</option></select>
        <label>🛠️ Langages et technologies maîtrisés :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="langages" required placeholder="Ex: HTML, CSS">
        <label>📚 Compétences déjà acquises :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="competences" required placeholder="Ex: Sites vitrines">
        <label>🎯 Compétences à améliorer ou à apprendre :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="competences_ameliorer" required placeholder="Ex: JavaScript">
        <label>🤖 Outils de développement utilisés :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="outils" required placeholder="Ex: VS Code"></div>
      <div class="card"><div style="background:#0a1930;color:#fff;padding:10px;border-radius:10px;font-weight:800">━━━━━━━━━━ 🚀 03. PROJETS RÉALISÉS ━━━━━━━━━━</div>
        <label>💻 Quels projets as-tu déjà réalisés ?</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><textarea name="projets" required rows="2" placeholder="Ex: Portfolio"></textarea>
        <label>🔗 Liens vers tes projets ou ton portfolio :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="liens_projets" placeholder="Ex: github.com/tonnom">
        <label>🛠️ Quelles technologies as-tu utilisées pour les réaliser ?</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="techno_projets" required placeholder="Ex: HTML CSS JS"></div>
      <div class="card"><div style="background:#0a1930;color:#fff;padding:10px;border-radius:10px;font-weight:800">━━━━━━━━━━ 🎯 04. MOTIVATION & DISPONIBILITÉ ━━━━━━━━━━</div>
        <label>🔥 Pourquoi souhaites-tu intégrer notre équipe ?</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><textarea name="motivation" required rows="2" placeholder="Ex: Apprendre en equipe"></textarea>
        <label>🎯 Quels sont tes objectifs au sein de l'équipe ?</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="objectifs" required placeholder="Ex: Devenir freelance">
        <label>⏳ Combien d'heures peux-tu consacrer par semaine ?</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><select name="disponibilite" required><option>De 5 a 10 heures</option><option>De 10 a 20 heures</option><option>Plus de 20 heures</option></select></div>
      <div class="card"><div style="background:#0a1930;color:#fff;padding:10px;border-radius:10px;font-weight:800">━━━━━━━━━━ ✅ 05. VALIDATION DE LA CANDIDATURE ━━━━━━━━━━</div>
        <div style="background:#f0f5ff;border:1px solid #d8e4ff;padding:12px;border-radius:10px;font-size:12px;line-height:1.6;margin-top:10px">📝 Je confirme que les informations fournies sont exactes et que je suis prêt(e) à apprendre, à collaborer et à participer sérieusement aux projets de l'équipe.</div>
        <label>👤 Nom du candidat :</label><div style="font-size:11px;color:#2a5bd7;font-weight:800">✍️ Réponse :</div><input name="nom_confirm" required placeholder="Ex: Jeremiah">
        <div style="margin-top:12px;display:flex;gap:8px;align-items:flex-start;background:#fff;border:1px solid #d8e4ff;padding:10px;border-radius:10px"><input type="checkbox" required style="width:18px;height:18px"><span style="font-size:12px">Je confirme que les informations sont exactes</span></div></div>
      <div style="background:#0a1930;color:#e6fffa;padding:14px;border-radius:12px;text-align:center;font-family:monospace;font-size:11px;white-space:pre-wrap;margin-top:16px;display:flex;flex-direction:column;align-items:center;gap:8px"><img src="{logo}" style="width:48px;height:48px;border-radius:50%">╔════════════════════════════╗
　🚀 APPRENONS • CRÉONS • INNOVONS
　💻 Le talent se développe par la pratique.
╚════════════════════════════╝</div>
      <button style="width:100%;background:linear-gradient(135deg,#25D366,#00a36a);color:#fff;padding:16px;border-radius:24px;border:none;font-weight:800;margin-top:20px;font-size:15px" type="submit">APERCU FORMULAIRE COMPLET →</button>
    </form>
  </div>
</div>
<script>document.getElementById('photoInput').addEventListener('change', function(e){{const f=e.target.files[0]; if(!f) return; const u=URL.createObjectURL(f); const i=document.getElementById('previewPhoto'); i.src=u; i.style.display='block';}});</script>
''')

@app.route('/form/preview', methods=['POST'])
def preview():
    init_db(); st=get_settings(); logo=get_logo_general(st); header=render_header(st)
    photo_file=request.files.get('photo'); photo_path=""
    if photo_file and photo_file.filename:
        fname=secure_filename(f"{uuid.uuid4().hex}_{photo_file.filename}")
        path=os.path.join('static/uploads', fname); photo_file.save(path); photo_path=f"/static/uploads/{fname}"; session['photo_path']=photo_path
    data={k: request.form.get(k,'').strip() for k in ['nom','age','ville','pays','whatsapp','niveau','langages','competences','competences_ameliorer','outils','projets','liens_projets','techno_projets','motivation','objectifs','disponibilite','nom_confirm']}
    session['form_data']=data
    img_html=f"<img src='{photo_path}' style='width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid #2a5bd7;display:block;margin:0 auto 12px'>" if photo_path else ""
    full_msg=build_formulaire_complet(data)
    return render_template_string(BASE_CSS + header + f'<div class="form-wrap" style="padding:24px;text-align:center"><img src="{logo}" style="width:60px;height:60px;border-radius:50%;margin-bottom:10px">{img_html}<h2>Apercu - Format exact</h2><div style="background:#0a1930;color:#c2f0d0;padding:20px;border-radius:14px;text-align:left;margin-top:12px;font-size:11px;white-space:pre-wrap;font-family:monospace;line-height:1.6">{full_msg}</div><form method="POST" action="/form/confirm" style="margin-top:18px"><button style="width:100%;background:#25D366;color:#fff;padding:14px;border-radius:24px;border:none;font-weight:800" type="submit">CONFIRMER → GROUPE RECRUTEMENT</button></form></div>')

@app.route('/form/confirm', methods=['POST'])
def confirm():
    init_db(); db=get_db(); st=get_settings(); logo=get_logo_general(st); header=render_header(st)
    d=session.get('form_data'); photo=session.get('photo_path','')
    if not d: return redirect('/form')
    cid=str(uuid.uuid4())
    try: age=int(d.get('age',0) or 0)
    except: age=0
    d['id']=cid
    db.execute("INSERT INTO candidatures VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cid,d.get('nom'),age,d.get('ville'),d.get('pays'),d.get('whatsapp'),d.get('niveau'),d.get('langages'),d.get('competences'),d.get('competences_ameliorer'),d.get('outils'),d.get('projets'),d.get('liens_projets'),d.get('techno_projets'),d.get('motivation'),d.get('objectifs'),d.get('disponibilite'),'En attente',datetime.datetime.now().isoformat(),d.get('pays','').lower(),d.get('ville','').lower(),photo))
    db.commit()
    full_msg=build_formulaire_complet(d)
    return render_template_string(BASE_CSS + header + f'''
<div class="form-wrap" style="padding:24px;text-align:center"><img src="{logo}" style="width:60px;height:60px;border-radius:50%;margin-bottom:8px"><img src="{photo}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid #2a5bd7;display:block;margin:0 auto 12px"><h2 style="color:#25D366">✅ Pret pour GROUPE RECRUTEMENT</h2><div style="background:#0a1930;color:#c2f0d0;padding:16px;border-radius:12px;margin:16px 0;text-align:left;font-size:11px;white-space:pre-wrap;font-family:monospace;max-height:500px;overflow-y:auto">{full_msg}</div><a href="{photo}" download style="display:block;background:#0a1930;color:#fff;padding:14px;border-radius:24px;text-decoration:none;font-weight:800">📥 TELECHARGER VRAIE PHOTO</a><a href="{st["link_recrutement"]}" target="_blank" style="display:block;background:#25D366;color:#fff;padding:16px;border-radius:24px;text-decoration:none;font-weight:800;margin-top:12px">👥 ENVOYER DANS GROUPE RECRUTEMENT →</a></div>
''')

@app.route('/annonces')
def annonces_page():
    init_db(); db=get_db(); st=get_settings(); logo=get_logo_general(st); header=render_header(st)
    rows=db.execute("SELECT * FROM annonces WHERE statut='publiee' ORDER BY date DESC").fetchall()
    html_cards="".join([f"<div class='card'><img src='{r['image']}' style='width:100%;height:200px;object-fit:cover;border-radius:12px'><div style='padding:14px'><div style='display:flex;justify-content:space-between'><span style='background:#0a1930;color:#fff;padding:4px 10px;border-radius:20px;font-size:10px'>{r['categorie']}</span><span style='background:#25D366;color:#fff;padding:4px 10px;border-radius:20px;font-size:10px'>{r['prix']}</span></div><h3 style='margin:10px 0 6px 0'>{r['titre']}</h3><p style='font-size:12px;color:#4a5a7a'>{r['description']}</p></div></div>" for r in rows])
    return render_template_string(BASE_CSS + header + f'<div class="page"><div class="hero-photo" style="background-image:url(\'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200\')"><div class="hero-photo-content"><div style="display:flex;align-items:center;gap:14px"><img src="{logo}" style="width:56px;height:56px;border-radius:14px"><div><h1>🔥 Vraies Offres AMATRIX</h1><p>Site 50$ • Formations • Marketplace • SaaS</p></div></div></div></div><div style="padding:20px;display:grid;gap:16px">{html_cards}</div></div>')

@app.route('/apropos')
def apropos():
    init_db(); st=get_settings(); logo=get_logo_general(st); header=render_header(st); s=get_stats()
    return render_template_string(BASE_CSS + header + f'''
<div class="page">
  <div class="hero-photo" style="background-image:url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80')"><div class="hero-photo-content"><div style="display:flex;align-items:center;gap:14px"><img src="{logo}" style="width:64px;height:64px;border-radius:14px;border:2px solid #00e5ff"><div><h1>À propos AMATRIX</h1><p>De Lubumbashi au monde - Histoire complete</p></div></div></div></div>
  <div style="padding:20px">
    <div style="text-align:center"><img src="{logo}" style="width:120px;height:120px;border-radius:50%;border:3px solid #00e5ff;box-shadow:0 0 20px rgba(0,229,255,0.3)"><h2 style="margin-top:12px">AMATRIX Community</h2><small style="color:#2a5bd7;font-weight:800">APPRENONS • CREONS • INNOVONS • GAGNONS</small></div>
    <div class="card" style="margin-top:20px;background:linear-gradient(135deg,#0a1930,#1a3a6a);color:#fff;border:none">
      <h3 style="color:#00e5ff">💡 Pourquoi on a créé AMATRIX ? Notre Histoire</h3>
      <p style="font-size:13px;color:#b8d4f0;line-height:1.8;margin-top:10px">
        <b style="color:#fff">Constat à Lubumbashi :</b> 90% des commerces, écoles et églises sans site web. Pas par manque de besoin, mais solutions à 300-500$ trop chères.<br><br>
        <b style="color:#fff">Notre déclic :</b> Former des jeunes de L'shi à créer des sites à 50$ avec Mobile Money. Commerçant a son site, jeune gagne ses premiers dollars.<br><br>
        <b style="color:#fff">Nom AMATRIX :</b> A comme Apprendre, Matrix comme monde digital depuis Lubumbashi.
      </p>
    </div>
    <div class="card" style="background:linear-gradient(135deg,#f0f5ff,#e6edff);border:1px solid #d8e4ff">
      <h3>🎯 Notre Objectif Réel</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px">
        <div style="background:#fff;padding:12px;border-radius:12px;border:1px solid #d8e4ff"><b>1. Former autrement</b><br><small>Pas de cours ennuyeux. Projet réel pour vrai client de Lubumbashi dès la 2e semaine.</small></div>
        <div style="background:#fff;padding:12px;border-radius:12px;border:1px solid #d8e4ff"><b>2. Créer emplois locaux</b><br><small>Objectif : gagner 100$/mois en freelance en 3 mois, sans quitter L'shi.</small></div>
        <div style="background:#fff;padding:12px;border-radius:12px;border:1px solid #d8e4ff"><b>3. Digitaliser le Katanga</b><br><small>Chaque commerce de L'shi, Kolwezi, Likasi mérite site vitrine 50$ + Mobile Money.</small></div>
        <div style="background:#fff;padding:12px;border-radius:12px;border:1px solid #d8e4ff"><b>4. Prouver possible depuis RDC</b><br><small>Montrer que talent code aussi à Lubumbashi, solutions offline-first, Mobile Money.</small></div>
      </div>
    </div>
    <h3 style="margin-top:20px">⚙️ Nos 6 fonctionnalités expliquées en détail</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px">
      <div class="card" style="margin:0;border-left:4px solid #25D366"><b>🌐 Sites Web Vitrine 50$</b><br><small>On crée site 5 pages + domaine + hébergement + SEO. Pour commerce, école, église. Livraison 7 jours. Paiement Airtel Money. Exemple réel sur annonces. Tu apprends à le faire et à le vendre.</small></div>
      <div class="card" style="margin:0;border-left:4px solid #2a5bd7"><b>📱 Apps Android + Firebase</b><br><small>Application mobile avec base de données Firebase, mode offline. Exemple : app de livraison, app école. Tu apprends à la coder et à la vendre à des clients locaux.</small></div>
      <div class="card" style="margin:0;border-left:4px solid #6a4ad9"><b>🛒 Marketplace avec Mobile Money</b><br><small>Jumia local avec Airtel Money, Orange Money, M-Pesa. Commission automatique. On te montre comment coder système complet + déployer. Projet SaaS qui rapporte.</small></div>
      <div class="card" style="margin:0;border-left:4px solid #ff3b30"><b>🎓 Formations Débutant → Pro</b><br><small>1 mois HTML CSS Python. Projets réels, pas exercices. Tu sors avec portfolio + 1 client réel. Cours à Lubumbashi + online. Support groupe recrutement.</small></div>
      <div class="card" style="margin:0;border-left:4px solid #f59e0b"><b>🚀 SaaS Gestion Stock</b><br><small>Logiciel pour boutiques : stock, ventes, factures. Mode offline, rapports. Vendu 100$/an. Tu apprends à le coder et le commercialiser aux boutiques de L'shi.</small></div>
      <div class="card" style="margin:0;border-left:4px solid #00a36a"><b>💼 Freelance Revenus Réels</b><br><small>Après formation, tu rejoins équipe AMATRIX. Projets payés, clients réels. Objectif : gagner tes premiers 100$ en freelance en 3 mois. On t'aide à trouver clients.</small></div>
    </div>
    <div class="card" style="background:linear-gradient(135deg,#eaf1ff,#d9e8ff);border:1px solid #d8e4ff;margin-top:16px"><h3>🎯 Fonctionnalités techniques</h3><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"><div style="background:#fff;padding:10px;border-radius:10px;border:1px solid #d8e4ff"><b>Frontend</b><br><small>HTML5, CSS3, JS, Responsive</small></div><div style="background:#fff;padding:10px;border-radius:10px;border:1px solid #d8e4ff"><b>Backend</b><br><small>Python Flask, APIs</small></div><div style="background:#fff;padding:10px;border-radius:10px;border:1px solid #d8e4ff"><b>Database</b><br><small>Firebase, SQLite</small></div><div style="background:#fff;padding:10px;border-radius:10px;border:1px solid #d8e4ff"><b>Paiement</b><br><small>Mobile Money, Stripe</small></div></div></div>
    <div class="card" style="background:linear-gradient(135deg,#0a1930,#081a3d);color:#fff;border:none;margin-top:16px"><h3 style="color:#25D366">🌍 Pourquoi on existe ? Impact</h3><ul style="margin:10px 0 0 18px;font-size:13px;color:#b8c9e6;line-height:1.9"><li><b style="color:#fff">RDC - Lubumbashi :</b> 90% commerces sans site. On digitalise avec solution 50$ + Mobile Money.</li><li><b style="color:#fff">Afrique :</b> Solutions adaptées : offline-first, langues locales, paiement mobile.</li><li><b style="color:#fff">Monde :</b> Prouver que talent vient aussi de Lubumbashi.</li><li><b style="color:#fff">Jeunes :</b> Alternative au chômage. Crées ton emploi en codant.</li></ul></div>
    <div class="card" style="margin-top:16px"><h3>🚀 Vision 2026</h3><p style="font-size:13px;color:#4a5a7a;line-height:1.7;margin-top:6px">Actuel : {s["total"]} membres, {s["pays"]} pays, {s["villes"]} villes. Objectif déc 2026 : 200 membres actifs, 10 projets SaaS, 100 devs freelance 100$/mois.</p></div>
    <div style="text-align:center;margin-top:20px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap"><a href="/form" style="background:#25D366;color:#fff;padding:12px 24px;border-radius:24px;text-decoration:none;font-weight:800">Rejoindre AMATRIX →</a><a href="/annonces" style="background:#0a1930;color:#fff;padding:12px 24px;border-radius:24px;text-decoration:none">Voir Vraies Offres</a></div>
  </div>
</div>
<footer style="background:#07142e;color:#7e90b2;padding:16px;text-align:center;font-size:11px">© 2026 AMATRIX • Histoire + Fonctionnalités restaurées</footer>
''')

@app.route('/assistance', methods=['GET','POST'])
def assistance():
    init_db(); db=get_db(); st=get_settings(); logo=get_logo_general(st); header=render_header(st)
    c1_logo = st.get("cercle1_logo") or logo
    c2_logo = st.get("cercle2_logo") or logo
    c3_logo = st.get("cercle3_logo") or logo
    if request.method=='POST':
        nom=request.form.get('nom',''); wa=request.form.get('whatsapp',''); msg=request.form.get('message',''); typ=request.form.get('type','Support')
        db.execute("INSERT INTO assistance VALUES (?,?,?,?,?,?)",(str(uuid.uuid4()),nom,wa,msg,datetime.datetime.now().isoformat(),typ)); db.commit()
        wa_link=f"https://wa.me/243992083817?text={urllib.parse.quote(f'Assistance {typ} - {nom}: {msg}')}"
        return render_template_string(BASE_CSS + header + f'<div style="padding:40px;text-align:center"><h2>✅ Envoyé !</h2><a href="{wa_link}" target="_blank" style="display:block;background:#25D366;color:#fff;padding:14px;border-radius:24px;text-decoration:none;font-weight:800;max-width:400px;margin:20px auto">WhatsApp</a><a href="{st["link_recrutement"]}" target="_blank" style="display:block;background:#0a1930;color:#fff;padding:14px;border-radius:24px;text-decoration:none;font-weight:800;max-width:400px;margin:10px auto">Groupe recrutement</a></div><script>window.open("{wa_link}", "_blank")</script>')
    return render_template_string(BASE_CSS + header + f'''
<div class="page">
  <div class="hero-photo" style="background-image:url('https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80')"><div class="hero-photo-content"><div style="display:flex;align-items:center;gap:12px"><img src="{logo}" style="width:56px;height:56px;border-radius:14px;border:1px solid #00e5ff"><div><h1>🆘 Assistance AMATRIX</h1><p>Aide rapide • Réponse dans groupe recrutement</p></div></div></div></div>
  <div style="padding:20px">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div class="glass-card"><h3>⚡ Assistance Rapide</h3><p style="font-size:12px;color:#4a5a7a;margin-top:6px">Choisis ton problème</p><div style="display:grid;gap:8px;margin-top:12px"><div class="glass-card" style="padding:10px"><b>🔧 Technique</b><br><small>Bug, code</small></div><div class="glass-card" style="padding:10px"><b>💰 Paiement</b><br><small>Site 50$</small></div><div class="glass-card" style="padding:10px"><b>📚 Formation</b><br><small>Cours</small></div></div></div>
      <div class="glass-card" style="background:linear-gradient(135deg,rgba(238,243,255,0.9),rgba(230,237,255,0.9))"><h3>📞 Contacts Directs - Effet verre + logos circulaires</h3>
        <div style="display:grid;gap:12px;margin-top:12px">
          <a href="{st["link_chaine"]}" target="_blank" style="display:flex;gap:12px;align-items:center;text-decoration:none;color:#0a1930;background:rgba(255,255,255,0.8);backdrop-filter:blur(10px);padding:12px;border-radius:14px;border:1px solid rgba(42,91,215,0.15);box-shadow:0 4px 16px rgba(42,91,215,0.1)">
            <img src="{c1_logo}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid #00e5ff;box-shadow:0 2px 10px rgba(0,229,255,0.3)">
            <div><b>Chaîne WhatsApp</b><br><small>Actus, annonces</small></div><span style="margin-left:auto;background:rgba(42,91,215,0.1);padding:6px 10px;border-radius:20px;font-size:11px">→</span>
          </a>
          <a href="{st["link_recrutement"]}" target="_blank" style="display:flex;gap:12px;align-items:center;text-decoration:none;color:#0a1930;background:rgba(255,255,255,0.8);backdrop-filter:blur(10px);padding:12px;border-radius:14px;border:1px solid rgba(37,211,102,0.2);box-shadow:0 4px 16px rgba(37,211,102,0.1)">
            <img src="{c2_logo}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid #25D366;box-shadow:0 2px 10px rgba(37,211,102,0.3)">
            <div><b>Groupe Recrutement</b><br><small>Assistance ici - Réponse rapide</small></div><span style="margin-left:auto;background:rgba(37,211,102,0.15);padding:6px 10px;border-radius:20px;font-size:11px">→</span>
          </a>
          <a href="{st["link_communaute"]}" target="_blank" style="display:flex;gap:12px;align-items:center;text-decoration:none;color:#0a1930;background:rgba(255,255,255,0.8);backdrop-filter:blur(10px);padding:12px;border-radius:14px;border:1px solid rgba(106,74,217,0.2);box-shadow:0 4px 16px rgba(106,74,217,0.1)">
            <img src="{c3_logo}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid #6a4ad9;box-shadow:0 2px 10px rgba(106,74,217,0.3)">
            <div><b>Communauté Devs</b><br><small>Entraide quotidienne</small></div><span style="margin-left:auto;background:rgba(106,74,217,0.1);padding:6px 10px;border-radius:20px;font-size:11px">→</span>
          </a>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px"><div class="glass-card" style="padding:8px;text-align:center"><b style="font-size:11px">HTML/CSS</b><br><small style="font-size:10px">Frontend</small></div><div class="glass-card" style="padding:8px;text-align:center"><b style="font-size:11px">Python</b><br><small style="font-size:10px">Backend</small></div><div class="glass-card" style="padding:8px;text-align:center"><b style="font-size:11px">Firebase</b><br><small style="font-size:10px">Database</small></div></div>
      </div>
    </div>
    <div class="card" style="margin-top:16px"><h3>✍️ Écrire ta demande (envoi groupe recrutement)</h3><form method="POST" style="margin-top:12px"><label>Type *</label><select name="type" required style="width:100%;padding:12px;border-radius:12px;border:1px solid #c2d3f0"><option>Support Technique</option><option>Paiement / Commande</option><option>Formation</option><option>Bug Site</option><option>Autre</option></select><label>Nom *</label><input name="nom" required placeholder="Ex: Jeremiah" style="width:100%;padding:12px;border-radius:12px;border:1px solid #c2d3f0;margin-top:6px"><label>WhatsApp *</label><input name="whatsapp" required placeholder="Ex: +243 992083817" style="width:100%;padding:12px;border-radius:12px;border:1px solid #c2d3f0;margin-top:6px"><label>Message *</label><textarea name="message" required rows="5" placeholder="Ex: Bonjour, j'ai un bug..." style="width:100%;padding:12px;border-radius:12px;border:1px solid #c2d3f0;margin-top:6px"></textarea><button style="width:100%;background:linear-gradient(135deg,#25D366,#00a36a);color:#fff;padding:14px;border-radius:24px;border:none;font-weight:800;margin-top:16px" type="submit">ENVOYER VERS GROUPE RECRUTEMENT →</button></form></div>
  </div>
</div>
<footer style="background:#07142e;color:#7e90b2;padding:16px;text-align:center;font-size:11px">© 2026 AMATRIX • Assistance 3 logos circulaires verre corrigés</footer>
''')

@app.route('/membres')
def membres():
    init_db(); db=get_db(); st=get_settings(); logo=get_logo_general(st); header=render_header(st); s=get_stats(); rows=db.execute("SELECT * FROM candidatures ORDER BY created_at DESC").fetchall()
    if not rows:
        html = f"""<div style="text-align:center;padding:40px 20px"><img src="{logo}" style="width:80px;height:80px;border-radius:50%;border:2px solid #00e5ff"><h2 style="margin-top:12px">Communauté en démarrage</h2><p>Sois le premier membre</p><a href="/form" style="display:inline-block;background:#25D366;color:#fff;padding:12px 28px;border-radius:24px;text-decoration:none;font-weight:800;margin-top:20px">S'inscrire →</a></div>"""
    else:
        cards=""
        for r in rows:
            photo = r['photo'] or 'https://images.unsplash.com/photo-1535713875008-d1d0cf377fde?auto=format&fit=crop&w=200&q=80'
            cards+=f"""<div class="member-card"><div class="member-top"><img src="{photo}" class="member-avatar"></div><div class="member-body"><h3>{r['nom']}</h3><small>📍 {r['ville']} • {r['pays']}</small><br><span class="badge-level debutant">{r['niveau']}</span><div style="margin-top:10px;text-align:left;background:#f8faff;border-radius:12px;padding:10px;border:1px solid #eef2ff"><div style="font-size:11px"><b>💻</b> {(r['langages'] or '')[:50]}</div></div></div></div>"""
        html = f"""<div class="member-grid">{cards}</div>"""
    return render_template_string(BASE_CSS + header + f'<div class="page" style="background:#f6f8ff"><div class="hero-photo" style="background-image:url(\'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80\');height:340px"><div class="hero-photo-content"><div style="display:flex;align-items:center;gap:14px"><img src="{logo}" style="width:56px;height:56px;border-radius:14px"><div><h1>👥 Membres AMATRIX</h1><p>{s["total"]} développeurs • {s["pays"]} pays • {s["villes"]} villes</p></div></div></div></div><div style="padding:20px;max-width:1150px;margin:0 auto">{html}</div></div>')

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    init_db(); st=get_settings(); logo=get_logo_general(st)
    if request.method=='POST':
        u=request.form.get('username','').strip().lower()
        p=request.form.get('password','').strip()
        db=get_db()
        r=db.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone()
        if r and check_password_hash(r['password_hash'],p):
            session['admin']=r['username']
            return redirect('/admin/dashboard')
        return render_template_string(BASE_CSS + f'<div class="page" style="max-width:480px"><div style="background:#0a1930;padding:14px;display:flex;align-items:center;gap:12px"><a href="/" style="color:#fff;text-decoration:none;font-size:20px;background:#0f2a52;padding:8px 14px;border-radius:10px">←</a><img src="{logo}" style="width:32px;height:32px;border-radius:8px"><div style="color:#fff"><b>Erreur</b></div></div><div style="padding:40px;text-align:center"><p>❌ Identifiant / Codes incorrects</p><a href="/admin" style="display:inline-block;background:#0a1930;color:#fff;padding:10px 18px;border-radius:20px;text-decoration:none;margin-top:12px">Réessayer</a></div></div>')
    if 'admin' in session: return redirect('/admin/dashboard')
    return render_template_string(BASE_CSS + f'''
<div class="page" style="max-width:480px">
  <div style="background:#0a1930;padding:14px;display:flex;align-items:center;gap:12px"><a href="/" style="color:#fff;text-decoration:none;font-size:20px;background:#0f2a52;padding:8px 14px;border-radius:10px">←</a><img src="{logo}" style="width:36px;height:36px;border-radius:8px"><div style="color:#fff"><b>Administration</b><br><small style="color:#8da1c7">Accès sécurisé</small></div></div>
  <div class="hero-photo" style="background-image:url('https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1200&q=80');height:260px"><div class="hero-photo-content"><div style="display:flex;align-items:center;gap:14px"><img src="{logo}" style="width:52px;height:52px;border-radius:12px"><div><h1>⚙️ Administration</h1><p>Espace réservé aux administrateurs</p></div></div></div></div>
  <div style="padding:24px;background:#fff">
    <form method="POST" autocomplete="off">
      <label style="font-size:12px;font-weight:800;color:#0a1930;display:block;margin-bottom:6px">Identifiant</label>
      <input name="username" type="text" required autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" style="width:100%;padding:14px;border-radius:12px;border:1px solid #c2d3f0">
      <label style="font-size:12px;font-weight:800;color:#0a1930;display:block;margin:14px 0 6px 0">Codes</label>
      <input name="password" type="password" required autocomplete="new-password" style="width:100%;padding:14px;border-radius:12px;border:1px solid #c2d3f0">
      <button style="width:100%;background:linear-gradient(135deg,#0a1930,#1a3a5a);color:#fff;padding:14px;border-radius:12px;border:none;margin-top:20px;font-weight:800" type="submit">Entrer →</button>
    </form>
  </div>
</div>
''')

@app.route('/admin/dashboard', methods=['GET','POST'])
def dash():
    init_db()
    if 'admin' not in session: return redirect('/admin')
    db=get_db(); s=get_stats(); st=get_settings(); logo=get_logo_general(st)
    msg=""
    if request.method=='POST':
        code=request.form.get('code_admin','')
        action=request.form.get('action')
        if code != CODE_ADMIN_MODIF and action in ['save_hero','save_hero_image','save_cercles','save_links','save_general_logo','save_cercle_logos','toggle_feature']:
            msg="<div style='background:#fee;border:1px solid #f99;padding:10px;border-radius:10px;color:#900'>❌ Codes incorrects</div>"
        else:
            if action=='save_general_logo':
                f=request.files.get('general_logo')
                if f and f.filename:
                    fname=secure_filename(f"general_logo_{uuid.uuid4().hex}_{f.filename}")
                    path=os.path.join('static/uploads',fname); f.save(path)
                    db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",("general_logo",f"/{path}"))
                    db.commit()
                    msg="<div style='background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:10px'>✅ Logo général AMATRIX mis à jour - s'affiche partout</div>"
                    st=get_settings()
            elif action=='save_cercle_logos':
                for key in ['cercle1_logo','cercle2_logo','cercle3_logo']:
                    f=request.files.get(key)
                    if f and f.filename:
                        fname=secure_filename(f"{key}_{uuid.uuid4().hex}_{f.filename}")
                        path=os.path.join('static/uploads',fname); f.save(path)
                        db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(key,f"/{path}"))
                db.commit()
                msg="<div style='background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:10px'>✅ Logos des 3 cercles mis à jour - Chaîne, Recrutement, Communauté</div>"
                st=get_settings()
            elif action=='save_hero':
                for k in ['hero_badge','hero_title','hero_desc','hero_btn','hero_blur1','hero_blur2','hero_blur3','hero_blur4','hero_hand']:
                    v=request.form.get(k,'')
                    if v: db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(k,v))
                db.commit(); msg="<div style='background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:10px'>✅ Hero textes mis à jour</div>"
            elif action=='save_hero_image':
                f=request.files.get('hero_image_file')
                if f and f.filename:
                    fname=secure_filename(f"hero_{uuid.uuid4().hex}_{f.filename}")
                    path=os.path.join('static/uploads',fname); f.save(path)
                    db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",("hero_image",f"/{path}"))
                    db.commit()
                    msg="<div style='background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:10px'>✅ Image Hero principale qui flotte changée !</div>"
                    st=get_settings()
                else:
                    v=request.form.get('hero_image','')
                    if v:
                        db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",("hero_image",v))
                        db.commit()
                        msg="<div style='background:#e6fffa;padding:12px;border-radius:10px'>✅ URL Hero mise à jour</div>"
                        st=get_settings()
            elif action=='save_cercles':
                for k in ['cercle1_titre','cercle1_icone','cercle1_btn','cercle1_color','cercle2_titre','cercle2_icone','cercle2_btn','cercle2_color','cercle3_titre','cercle3_icone','cercle3_btn','cercle3_color']:
                    v=request.form.get(k,'')
                    if v: db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(k,v))
                db.commit(); msg="<div style='background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:10px'>✅ Textes 3 Cercles mis à jour</div>"
            elif action=='save_links':
                for k in ['link_chaine','link_recrutement','link_communaute']:
                    v=request.form.get(k,'')
                    if v: db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(k,v))
                db.commit(); msg="<div style='background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:10px'>✅ Liens WhatsApp mis à jour - Chaîne, Recrutement, Communauté</div>"
            elif action=='toggle_feature':
                feat=request.form.get('feature')
                curr=st.get(feat,'active')
                new_val='inactive' if curr=='active' else 'active'
                db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)",(feat,new_val))
                db.commit()
                msg=f"<div style='background:#eef3ff;border:1px solid #b5c9ff;padding:10px;border-radius:10px'>✅ {feat} -> {new_val}</div>"
                st=get_settings()
            elif action=='delete_candidature':
                cid=request.form.get('cid')
                db.execute("DELETE FROM candidatures WHERE id=?",(cid,)); db.commit()
                msg="<div style='background:#e6fffa;padding:10px;border-radius:10px'>✅ Candidature supprimée</div>"

    rows=db.execute("SELECT * FROM candidatures ORDER BY created_at DESC LIMIT 100").fetchall()
    html_members=""
    for r in rows:
        html_members+=f"<div class='admin-card' style='display:flex;gap:10px;align-items:center'><img src='{r['photo']}' style='width:44px;height:44px;border-radius:50%;border:1px solid #d8e4ff;object-fit:cover'><div style='flex:1'><b>{r['nom']}</b> - {r['ville']} / {r['pays']}<br><small>{r['niveau']} • {r['langages'][:30]} • {r['whatsapp']}</small></div><form method='POST' style='margin-left:auto'><input type='hidden' name='action' value='delete_candidature'><input type='hidden' name='code_admin' value='{CODE_ADMIN_MODIF}'><input type='hidden' name='cid' value='{r['id']}'><button style='background:#fee;color:#900;border:1px solid #f99;padding:6px 10px;border-radius:8px;font-size:11px'>Suppr</button></form></div>"
    if not html_members:
        html_members="<div class=card>Aucune candidature</div>"

    general_logo_preview = st.get("general_logo") or logo
    c1_prev = st.get("cercle1_logo") or logo
    c2_prev = st.get("cercle2_logo") or logo
    c3_prev = st.get("cercle3_logo") or logo

    # VERTICAL LAYOUT
    return render_template_string(BASE_CSS + f'''
<div style="padding:0;max-width:800px;margin:0 auto;background:#f6f8ff;min-height:100vh">
  <div class="hero-photo" style="background-image:url('https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1200&q=80');height:320px">
    <div class="hero-photo-content">
      <div style="display:flex;align-items:center;gap:14px">
        <img src="{logo}" style="width:64px;height:64px;border-radius:14px;border:2px solid #00e5ff">
        <div>
          <h1 style="font-size:26px">⚙️ Administration AMATRIX</h1>
          <p>Tableau de bord • Logos • Liens • Hero • Membres</p>
          <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
            <span style="background:rgba(0,0,0,0.35);backdrop-filter:blur(8px);padding:6px 12px;border-radius:20px;font-size:11px;border:1px solid rgba(255,255,255,0.2)">👥 {s["total"]} inscrits</span>
            <span style="background:rgba(37,211,102,0.25);padding:6px 12px;border-radius:20px;font-size:11px">🌍 {s["pays"]} pays</span>
            <span style="background:rgba(42,91,215,0.25);padding:6px 12px;border-radius:20px;font-size:11px">📍 {s["villes"]} villes</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div style="padding:16px">
    {msg}

    <div class="vertical-stack">

      <!-- CONNEXION / DECONNEXION -->
      <div class="admin-card" style="background:linear-gradient(135deg,#0a1930,#1a3a5a);color:#fff;border:none">
        <div class="admin-title" style="color:#00e5ff">🔐 Connexion Administration</div>
        <div class="admin-desc" style="color:#b8d4f0">Tu es connecté en tant qu'administrateur. Gère ton site ici.</div>
        <div style="display:flex;gap:10px;margin-top:12px">
          <a href="/" style="background:#fff;color:#0a1930;padding:10px 18px;border-radius:10px;text-decoration:none;font-weight:800;font-size:12px;border:1px solid #d8e4ff">🏠 Voir Site Public</a>
          <a href="/admin/logout" style="background:#ff3b30;color:#fff;padding:10px 18px;border-radius:10px;text-decoration:none;font-weight:800;font-size:12px">🚪 Se Déconnecter</a>
        </div>
        <div style="margin-top:12px;background:rgba(0,0,0,0.25);padding:10px;border-radius:10px;font-size:11px;color:#8da1c7">Session active • Identifiant : amatrix • Code admin protégé</div>
      </div>

      <!-- STATS -->
      <div class="admin-card">
        <div class="admin-title">📊 Statistiques</div>
        <div class="admin-desc">Vue d'ensemble de la communauté</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px">
          <div style="background:#e6fffa;border:1px solid #b2f0d0;padding:12px;border-radius:12px;text-align:center"><b style="font-size:20px;color:#0a1930">{s["total"]}</b><br><small>Membres</small></div>
          <div style="background:#eef3ff;border:1px solid #c3d9ff;padding:12px;border-radius:12px;text-align:center"><b style="font-size:20px;color:#0a1930">{s["pays"]}</b><br><small>Pays</small></div>
          <div style="background:#f3efff;border:1px solid #e9d8fd;padding:12px;border-radius:12px;text-align:center"><b style="font-size:20px;color:#0a1930">{s["villes"]}</b><br><small>Villes</small></div>
          <div style="background:#fef3c7;border:1px solid #fde68a;padding:12px;border-radius:12px;text-align:center"><b style="font-size:20px;color:#0a1930">{s["week"]}</b><br><small>Semaine</small></div>
        </div>
      </div>

      <!-- LOGO GENERAL -->
      <div class="admin-card">
        <div class="admin-title">🖼️ Logo Général AMATRIX - Case générale</div>
        <div class="admin-desc">Ce logo s'affiche automatiquement dans Accueil, Annonces, Assistance, À propos, S'inscrire, Membres, Admin. Sélectionne depuis galerie, il s'applique partout.</div>
        <div style="display:flex;gap:16px;align-items:center;margin:12px 0">
          <img src="{general_logo_preview}" style="width:90px;height:90px;border-radius:18px;object-fit:cover;border:2px solid #00e5ff;box-shadow:0 4px 16px rgba(0,229,255,0.3)">
          <div style="flex:1"><b>Aperçu actuel</b><br><small style="color:#6b7aa0">Ce logo apparaît dans toutes les pages qui ont le logo AMATRIX</small></div>
        </div>
        <form method="POST" enctype="multipart/form-data" style="margin-top:12px">
          <input type="hidden" name="action" value="save_general_logo">
          <label style="font-size:12px;font-weight:800">Codes admin *</label>
          <input name="code_admin" type="password" required style="width:100%;padding:12px;border-radius:10px;border:1px solid #c2d3f0;margin-top:4px">
          <label style="font-size:12px;font-weight:800;margin-top:12px;display:block">📸 Choisir logo depuis galerie</label>
          <input name="general_logo" type="file" accept="image/*" required style="width:100%;padding:12px;border-radius:10px;border:1px dashed #8aa9f0;margin-top:4px;background:#f0f5ff">
          <button style="width:100%;background:#0a1930;color:#fff;padding:14px;border-radius:10px;border:none;margin-top:12px;font-weight:800" type="submit">💾 Enregistrer Logo Général - Appliquer partout</button>
        </form>
      </div>

      <!-- LOGOS 3 CERCLES -->
      <div class="admin-card">
        <div class="admin-title">⭕ Logos des 3 Cercles - Chaîne / Recrutement / Communauté</div>
        <div class="admin-desc">Mets un logo différent pour chaque cercle. Cercle = rond qui affiche ton image. Sélection galerie, ça change directement sur Accueil ET Assistance (les 3 cases contacts).</div>
        <form method="POST" enctype="multipart/form-data" style="margin-top:12px">
          <input type="hidden" name="action" value="save_cercle_logos">
          <label style="font-size:12px;font-weight:800">Codes admin *</label>
          <input name="code_admin" type="password" required style="width:100%;padding:12px;border-radius:10px;border:1px solid #c2d3f0;margin-top:4px">
          <div class="vertical-stack" style="margin-top:16px">
            <div style="background:#f0f5ff;border:1px solid #d8e4ff;padding:14px;border-radius:12px;display:flex;gap:12px;align-items:center">
              <img src="{c1_prev}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid #00e5ff">
              <div style="flex:1"><b>1. Chaîne</b><br><small>S'affiche Accueil + Assistance Chaîne</small><input name="cercle1_logo" type="file" accept="image/*" style="width:100%;padding:8px;border-radius:10px;border:1px dashed #8aa9f0;background:#fff;margin-top:6px"></div>
            </div>
            <div style="background:#f0faf5;border:1px solid #c2f0d0;padding:14px;border-radius:12px;display:flex;gap:12px;align-items:center">
              <img src="{c2_prev}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid #25D366">
              <div style="flex:1"><b>2. Recrutement</b><br><small>S'affiche Accueil + Assistance Recrutement</small><input name="cercle2_logo" type="file" accept="image/*" style="width:100%;padding:8px;border-radius:10px;border:1px dashed #8aa9f0;background:#fff;margin-top:6px"></div>
            </div>
            <div style="background:#f3f0ff;border:1px solid #d8e4ff;padding:14px;border-radius:12px;display:flex;gap:12px;align-items:center">
              <img src="{c3_prev}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid #6a4ad9">
              <div style="flex:1"><b>3. Communauté</b><br><small>S'affiche Accueil + Assistance Communauté</small><input name="cercle3_logo" type="file" accept="image/*" style="width:100%;padding:8px;border-radius:10px;border:1px dashed #8aa9f0;background:#fff;margin-top:6px"></div>
            </div>
          </div>
          <button style="width:100%;background:#2a5bd7;color:#fff;padding:14px;border-radius:10px;border:none;margin-top:16px;font-weight:800" type="submit">💾 Enregistrer Logos 3 Cercles - Accueil + Assistance</button>
        </form>
      </div>

      <!-- HERO PRINCIPAL IMAGE QUI FLOTTE -->
      <div class="admin-card">
        <div class="admin-title">🎨 Héros Principal - Image qui flotte</div>
        <div class="admin-desc">Change l'image principale qui flotte à droite sur Accueil (ordinateur/code). Tu peux mettre une autre photo depuis galerie. Elle flotte avec animation.</div>
        <div style="display:flex;gap:16px;align-items:center;margin:12px 0">
          <img src="{st["hero_image"]}" style="width:90px;height:70px;border-radius:12px;object-fit:cover;border:1px solid #d8e4ff">
          <div style="flex:1"><b>Aperçu actuel Hero</b><br><small style="color:#6b7aa0">Image qui flotte sur page d'accueil à droite</small></div>
        </div>
        <form method="POST" enctype="multipart/form-data" style="margin-top:12px">
          <input type="hidden" name="action" value="save_hero_image">
          <label style="font-size:12px;font-weight:800">Codes admin *</label>
          <input name="code_admin" type="password" required style="width:100%;padding:12px;border-radius:10px;border:1px solid #c2d3f0;margin-top:4px">
          <label style="font-size:12px;font-weight:800;margin-top:12px;display:block">📸 Choisir nouvelle image Hero depuis galerie</label>
          <input name="hero_image_file" type="file" accept="image/*" style="width:100%;padding:12px;border-radius:10px;border:1px dashed #8aa9f0;margin-top:4px;background:#f0f5ff">
          <div style="text-align:center;margin:8px 0;color:#6b7aa0;font-size:11px">— ou colle URL —</div>
          <input name="hero_image" placeholder="https://..." style="width:100%;padding:12px;border-radius:10px;border:1px solid #d8e4ff">
          <button style="width:100%;background:#0a1930;color:#fff;padding:14px;border-radius:10px;border:none;margin-top:12px;font-weight:800" type="submit">💾 Changer Image Hero qui flotte</button>
        </form>
        <form method="POST" style="margin-top:16px;border-top:1px solid #eef2ff;padding-top:16px">
          <input type="hidden" name="action" value="save_hero">
          <label style="font-size:12px;font-weight:800">Codes admin *</label>
          <input name="code_admin" type="password" required style="width:100%;padding:12px;border-radius:10px;border:1px solid #c2d3f0;margin-top:4px">
          <label style="font-size:12px;font-weight:800;margin-top:12px;display:block">Badge</label>
          <input name="hero_badge" value="{st["hero_badge"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:10px">
          <label style="font-size:12px;font-weight:800;margin-top:8px;display:block">Titre Hero</label>
          <input name="hero_title" value="{st["hero_title"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:10px">
          <label style="font-size:12px;font-weight:800;margin-top:8px;display:block">Description</label>
          <textarea name="hero_desc" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:10px">{st["hero_desc"]}</textarea>
          <button style="width:100%;background:#1a3a5a;color:#fff;padding:12px;border-radius:10px;border:none;margin-top:12px;font-weight:800" type="submit">💾 Sauver Textes Hero</button>
        </form>
      </div>

      <!-- LIENS -->
      <div class="admin-card">
        <div class="admin-title">🔗 Liens - Chaîne / Recrutement / Communauté</div>
        <div class="admin-desc">Change les liens WhatsApp. Une seule case verticale avec 3 champs. S'applique sur Accueil (3 cercles) et Assistance (3 contacts verre).</div>
        <form method="POST" style="margin-top:12px">
          <input type="hidden" name="action" value="save_links">
          <label style="font-size:12px;font-weight:800">Codes admin *</label>
          <input name="code_admin" type="password" required style="width:100%;padding:12px;border-radius:10px;border:1px solid #c2d3f0;margin-top:4px">
          <label style="font-size:12px;font-weight:800;margin-top:14px;display:block">🔗 Lien Chaîne WhatsApp</label>
          <input name="link_chaine" value="{st["link_chaine"]}" style="width:100%;padding:12px;margin-top:4px;border:1px solid #d8e4ff;border-radius:10px">
          <label style="font-size:12px;font-weight:800;margin-top:12px;display:block">👥 Lien Groupe Recrutement</label>
          <input name="link_recrutement" value="{st["link_recrutement"]}" style="width:100%;padding:12px;margin-top:4px;border:1px solid #d8e4ff;border-radius:10px">
          <label style="font-size:12px;font-weight:800;margin-top:12px;display:block">👨‍💻 Lien Communauté Devs</label>
          <input name="link_communaute" value="{st["link_communaute"]}" style="width:100%;padding:12px;margin-top:4px;border:1px solid #d8e4ff;border-radius:10px">
          <button style="width:100%;background:#25D366;color:#fff;padding:14px;border-radius:10px;border:none;margin-top:16px;font-weight:800" type="submit">💾 Enregistrer Liens - Chaîne + Recrutement + Communauté</button>
        </form>
      </div>

      <!-- TEXTES 3 CERCLES -->
      <div class="admin-card">
        <div class="admin-title">✏️ Textes des 3 Cercles</div>
        <div class="admin-desc">Change les titres et boutons des cercles sans toucher aux logos.</div>
        <form method="POST" style="margin-top:12px">
          <input type="hidden" name="action" value="save_cercles">
          <label style="font-size:12px;font-weight:800">Codes admin *</label>
          <input name="code_admin" type="password" required style="width:100%;padding:12px;border-radius:10px;border:1px solid #c2d3f0;margin-top:4px">
          <div class="vertical-stack" style="margin-top:16px">
            <div style="background:#f0f5ff;padding:14px;border-radius:12px;border:1px solid #d8e4ff">
              <b>Cercle 1 - Chaîne</b>
              <label style="font-size:11px;margin-top:8px;display:block">Titre</label><input name="cercle1_titre" value="{st["cercle1_titre"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
              <label style="font-size:11px;margin-top:8px;display:block">Texte icône (si pas de logo)</label><input name="cercle1_icone" value="{st["cercle1_icone"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
              <label style="font-size:11px;margin-top:8px;display:block">Bouton</label><input name="cercle1_btn" value="{st["cercle1_btn"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
            </div>
            <div style="background:#f0faf5;padding:14px;border-radius:12px;border:1px solid #c2f0d0">
              <b>Cercle 2 - Recrutement</b>
              <label style="font-size:11px;margin-top:8px;display:block">Titre</label><input name="cercle2_titre" value="{st["cercle2_titre"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
              <label style="font-size:11px;margin-top:8px;display:block">Texte icône</label><input name="cercle2_icone" value="{st["cercle2_icone"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
              <label style="font-size:11px;margin-top:8px;display:block">Bouton</label><input name="cercle2_btn" value="{st["cercle2_btn"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
            </div>
            <div style="background:#f3f0ff;padding:14px;border-radius:12px;border:1px solid #d8e4ff">
              <b>Cercle 3 - Communauté</b>
              <label style="font-size:11px;margin-top:8px;display:block">Titre</label><input name="cercle3_titre" value="{st["cercle3_titre"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
              <label style="font-size:11px;margin-top:8px;display:block">Texte icône</label><input name="cercle3_icone" value="{st["cercle3_icone"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
              <label style="font-size:11px;margin-top:8px;display:block">Bouton</label><input name="cercle3_btn" value="{st["cercle3_btn"]}" style="width:100%;padding:10px;margin-top:4px;border:1px solid #d8e4ff;border-radius:8px">
            </div>
          </div>
          <button style="width:100%;background:#2a5bd7;color:#fff;padding:14px;border-radius:10px;border:none;margin-top:16px;font-weight:800" type="submit">💾 Sauver Textes 3 Cercles</button>
        </form>
      </div>

      <!-- MEMBRES -->
      <div class="admin-card">
        <div class="admin-title">👥 Tableau de bord - Formulaires inscrits ({s["total"]})</div>
        <div class="admin-desc">Tous les membres qui ont rempli le formulaire exact avec vraie photo. Tu peux supprimer.</div>
        <div style="margin-top:12px;display:flex;flex-direction:column;gap:8px;max-height:600px;overflow-y:auto">{html_members}</div>
      </div>

      <!-- DECONNEXION FINALE -->
      <div class="admin-card" style="background:linear-gradient(135deg,#fff5f5,#fee2e2);border:1px solid #fecaca">
        <div class="admin-title" style="color:#dc2626">🚪 Déconnexion</div>
        <div class="admin-desc">Quitter l'administration en sécurité</div>
        <a href="/admin/logout" style="display:block;background:#dc2626;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;text-align:center;margin-top:12px">Se Déconnecter Maintenant →</a>
        <a href="/" style="display:block;background:#fff;color:#0a1930;padding:14px;border-radius:10px;text-decoration:none;font-weight:800;text-align:center;margin-top:10px;border:1px solid #d8e4ff">🏠 Retour Site Public</a>
      </div>

    </div>
  </div>
</div>
''')

@app.route('/admin/logout')
def logout(): session.clear(); return redirect('/admin')

if __name__=='__main__':
    init_db(); os.makedirs('static',exist_ok=True); os.makedirs('static/uploads',exist_ok=True)
    print("ADMIN VERTICAL FIX - 3 logos assistance + apropos restaure + hero image changeable")
    app.run(host='0.0.0.0',port=9000,debug=True)
