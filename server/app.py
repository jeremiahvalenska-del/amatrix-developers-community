from flask import Flask, request, jsonify, session, send_from_directory
from argon2 import PasswordHasher
import sqlite3, os, json, re, secrets, traceback
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY']=True
ph = PasswordHasher()

BASE = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(BASE,'server','amatrix.db')
if not os.path.exists(DB):
    DB = os.path.join(os.path.dirname(__file__),'amatrix.db')

def get_db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def require_auth(f):
    @wraps(f)
    def d(*a,**k):
        if 'admin_id' not in session:
            return jsonify({"error":"Non autorisé"}),401
        return f(*a,**k)
    return d

@app.after_request
def cors(resp):
    resp.headers['Access-Control-Allow-Origin']='*'
    resp.headers['Access-Control-Allow-Headers']='Content-Type'
    resp.headers['Access-Control-Allow-Methods']='GET,POST,PUT,DELETE,OPTIONS'
    return resp

@app.route('/')
def root():
    return send_from_directory(BASE,'index.html')

@app.route('/api/ping')
def ping():
    return jsonify({"ok":True,"db":DB,"exists":os.path.exists(DB)})

@app.route('/api/admins-public')
def ap():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT id,nom,role FROM admins WHERE active=1 ORDER BY id")
    r=[dict(x) for x in cur.fetchall()]; conn.close()
    return jsonify(r)

@app.route('/api/login', methods=['POST','OPTIONS'])
def login():
    if request.method=='OPTIONS': return jsonify({"ok":True})
    d=request.json or {}; aid=d.get('admin_id'); code=d.get('code','') or d.get('password','')
    if not aid or not code: return jsonify({"error":"Manquant"}),400
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT id,nom,password_hash,active,role FROM admins WHERE id=?",(aid,))
    row=cur.fetchone()
    if not row or not row['active']:
        conn.close(); return jsonify({"error":"Compte inactif"}),401
    try:
        ph.verify(row['password_hash'], code)
    except Exception as e:
        conn.close(); return jsonify({"error":"Code incorrect"}),401
    session['admin_id']=row['id']; session.permanent=True
    app.permanent_session_lifetime=timedelta(hours=3)
    cur.execute("UPDATE admins SET derniere_connexion=datetime('now') WHERE id=?",(row['id'],))
    cur.execute("INSERT INTO historique (admin_id,action,resultat) VALUES (?,?,?)",(row['id'],"Connexion","Succès"))
    conn.commit(); conn.close()
    return jsonify({"success":True,"nom":row['nom'],"role":row['role'],"id":row['id']})

@app.route('/api/dashboard')
@require_auth
def dash():
    conn=get_db(); cur=conn.cursor()
    def cnt(q):
        try: cur.execute(q); return cur.fetchone()[0]
        except: return 0
    data={
      "total":cnt("SELECT COUNT(*) FROM membres"),
      "publics":cnt("SELECT COUNT(*) FROM membres WHERE visibility!='private'"),
      "prives":cnt("SELECT COUNT(*) FROM membres WHERE visibility='private'"),
      "actifs":cnt("SELECT COUNT(*) FROM membres WHERE statut='Validé'"),
      "suspendus":cnt("SELECT COUNT(*) FROM membres WHERE statut='Suspendu'"),
      "pays":cnt("SELECT COUNT(DISTINCT pays) FROM membres"),
      "villes":cnt("SELECT COUNT(DISTINCT ville) FROM membres")
    }
    cur.execute("SELECT COUNT(*) FROM admins WHERE active=1"); data["admins_actifs"]=cur.fetchone()[0]
    cur.execute("SELECT * FROM membres ORDER BY id DESC LIMIT 5"); data["dernieres"]=[dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/admins')
@require_auth
def admins_list():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT id,nom,role,numero,active,permissions,derniere_connexion FROM admins ORDER BY id")
    r=[dict(x) for x in cur.fetchall()]; conn.close()
    return jsonify(r)

@app.route('/api/admins/<int:aid>/perms', methods=['POST'])
@require_auth
def perms(aid):
    if session['admin_id']!=1: return jsonify({"error":"Seul fondateur"}),403
    if aid==1: return jsonify({"error":"Fondateur intouchable"}),403
    conn=get_db(); cur=conn.cursor()
    cur.execute("UPDATE admins SET permissions=? WHERE id=?",(json.dumps(request.json.get('permissions')),aid))
    cur.execute("INSERT INTO historique (admin_id,action,resultat) VALUES (?,?,?)",(session['admin_id'],f"Modif perms admin {aid}","Succès"))
    conn.commit(); conn.close()
    return jsonify({"success":True})

@app.route('/api/admins/<int:aid>/toggle', methods=['POST'])
@require_auth
def toggle(aid):
    if session['admin_id']!=1 or aid==1: return jsonify({"error":"Interdit"}),403
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT active FROM admins WHERE id=?",(aid,)); v=cur.fetchone()[0]
    cur.execute("UPDATE admins SET active=? WHERE id=?",(0 if v else 1,aid))
    conn.commit(); conn.close()
    return jsonify({"success":True})

@app.route('/api/change-own-password', methods=['POST'])
@require_auth
def chpwd():
    d=request.json or {}; old=d.get('old_code') or d.get('old_password'); new=d.get('new_code') or d.get('new_password')
    if not new or len(new)<8: return jsonify({"error":"8 chars min"}),400
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT password_hash FROM admins WHERE id=?",(session['admin_id'],)); h=cur.fetchone()[0]
    try: ph.verify(h, old)
    except: conn.close(); return jsonify({"error":"Ancien incorrect"}),401
    cur.execute("UPDATE admins SET password_hash=? WHERE id=?",(ph.hash(new),session['admin_id']))
    cur.execute("INSERT INTO historique (admin_id,action,resultat) VALUES (?,?,?)",(session['admin_id'],"Changement code perso","Succès"))
    conn.commit(); conn.close()
    return jsonify({"success":True})

@app.route('/api/texts', methods=['GET','POST'])
@require_auth
def texts():
    conn=get_db(); cur=conn.cursor()
    if request.method=='GET':
        cur.execute("SELECT key,value FROM texts"); r={x[0]:x[1] for x in cur.fetchall()}; conn.close(); return jsonify(r)
    else:
        if session['admin_id']!=1: conn.close(); return jsonify({"error":"Seul fondateur"}),403
        for k,v in (request.json or {}).items():
            cur.execute("INSERT OR REPLACE INTO texts (key,value) VALUES (?,?)",(k,v))
        conn.commit(); conn.close(); return jsonify({"success":True})

@app.route('/api/communities', methods=['GET','POST'])
@require_auth
def comms():
    conn=get_db(); cur=conn.cursor()
    if request.method=='GET':
        cur.execute("SELECT * FROM communities ORDER BY id DESC"); r=[dict(x) for x in cur.fetchall()]; conn.close(); return jsonify(r)
    d=request.json or {}
    if not d.get('nom') or not d.get('lien'): return jsonify({"error":"Nom+lien requis"}),400
    if not re.match(r'^https?://', d['lien']): return jsonify({"error":"Lien https:// requis"}),400
    cur.execute("INSERT INTO communities (type,nom,lien,photo,description) VALUES (?,?,?,?,?)",(d.get('type','group'),d['nom'],d['lien'],d.get('photo',''),d.get('description','')))
    conn.commit(); conn.close(); return jsonify({"success":True})

@app.route('/api/communities/<int:cid>', methods=['PUT','DELETE'])
@require_auth
def comm_mod(cid):
    conn=get_db(); cur=conn.cursor()
    if request.method=='DELETE':
        cur.execute("DELETE FROM communities WHERE id=?",(cid,)); conn.commit(); conn.close(); return jsonify({"success":True})
    d=request.json or {}
    cur.execute("UPDATE communities SET nom=?,lien=?,photo=?,description=?,active=? WHERE id=?",(d.get('nom'),d.get('lien'),d.get('photo'),d.get('description'),d.get('active',1),cid))
    conn.commit(); conn.close(); return jsonify({"success":True})

@app.route('/api/historique')
@require_auth
def hist():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT h.date,a.nom as admin,h.action,h.resultat FROM historique h LEFT JOIN admins a ON h.admin_id=a.id ORDER BY h.date DESC LIMIT 100")
    r=[dict(x) for x in cur.fetchall()]; conn.close(); return jsonify(r)

@app.route('/api/logout', methods=['POST'])
def logout(): session.clear(); return jsonify({"ok":True})

@app.route('/<path:path>')
def static_files(path):
    if path.startswith('api/'): return jsonify({"error":"Not found"}),404
    try: return send_from_directory(BASE, path)
    except: return jsonify({"error":"Not found"}),404

if __name__=='__main__':
    print(f"✅ V-FINAL sans flask_cors - DB={DB} exists={os.path.exists(DB)}")
    app.run(host='0.0.0.0',port=5000)
