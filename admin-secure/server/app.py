from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from argon2 import PasswordHasher
import sqlite3, os, secrets, time, json
from datetime import datetime, timedelta
from functools import wraps
app = Flask(__name__, static_folder='../')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY']=True
app.config['SESSION_COOKIE_SAMESITE']='Lax'
CORS(app, supports_credentials=True)
ph = PasswordHasher()
login_attempts={}
def get_db(): return sqlite3.connect('amatrix.db')
def require_auth(f):
    @wraps(f)
    def d(*a,**k):
        if 'admin_id' not in session: return jsonify({"error":"Non autorisé"}),401
        return f(*a,**k)
    return d
@app.route('/api/admins-public')
def admins_public():
    # JAMAIS telephone ni hash - conforme cahier
    return jsonify([{"id":1,"nom":"Akaza Valenska","role":"👑 Fondateur principal — Super administrateur"},{"id":2,"nom":"Mr Reddington","role":"💼 Administrateur secondaire"},{"id":3,"nom":"Rowan","role":"👥 Administrateur secondaire"},{"id":4,"nom":"KIYOTΔKΔ✞SUPREME AP¹","role":"⚙️ Administrateur secondaire"},{"id":5,"nom":"KRÜGER J A P","role":"🎯 Administrateur secondaire"}])
@app.route('/api/login', methods=['POST'])
def login():
    ip=request.remote_addr
    if ip in login_attempts and login_attempts[ip]['count']>=5 and time.time()-login_attempts[ip]['time']<900:
        return jsonify({"error":"Trop de tentatives, attendez 15min"}),429
    data=request.json
    aid=data.get('admin_id'); code=data.get('code')
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT id,nom,password_hash,active,role FROM admins WHERE id=?",(aid,))
    row=cur.fetchone()
    if not row or not row[3]:
        conn.close()
        return jsonify({"error":"Identifiants incorrects"}),401
    try:
        ph.verify(row[2], code)
        if ph.check_needs_rehash(row[2]):
            cur.execute("UPDATE admins SET password_hash=? WHERE id=?",(ph.hash(code),row[0])); conn.commit()
    except Exception as e:
        cur.execute("INSERT INTO historique (admin_id,action,resultat) VALUES (?,?,?)",(aid,"Tentative connexion échouée","Échec"))
        conn.commit(); conn.close()
        login_attempts[ip]={'count':login_attempts.get(ip,{}).get('count',0)+1,'time':time.time()}
        return jsonify({"error":"Code incorrect - commence par Amatrix"}),401
    session['admin_id']=row[0]; session.permanent=True; app.permanent_session_lifetime=timedelta(hours=2)
    cur.execute("UPDATE admins SET derniere_connexion=? WHERE id=?",(datetime.now().isoformat(),row[0]))
    cur.execute("INSERT INTO historique (admin_id,action,resultat) VALUES (?,?,?)",(row[0],"Connexion réussie","Succès"))
    conn.commit(); conn.close(); login_attempts.pop(ip,None)
    return jsonify({"success":True,"nom":row[1]})
@app.route('/api/me')
@require_auth
def me():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT nom,role FROM admins WHERE id=?",(session['admin_id'],))
    r=cur.fetchone(); conn.close()
    return jsonify({"nom":r[0],"role":r[1]}) if r else jsonify({})
@app.route('/api/dashboard')
@require_auth
def dash():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT COUNT(*) FROM membres"); total=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM membres WHERE visibilite='public'"); pub=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM membres WHERE visibilite='private'"); priv=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM membres WHERE date_inscription > datetime('now','-7 days')"); nouv=cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT pays) FROM membres"); pays=cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT ville) FROM membres"); villes=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM admins WHERE active=1"); admins_a=cur.fetchone()[0]
    cur.execute("SELECT * FROM membres ORDER BY date_inscription DESC LIMIT 5"); der=cur.fetchall()
    conn.close()
    return jsonify({"total":total,"publics":pub,"prives":priv,"nouveaux":nouv,"pays":pays,"villes":villes,"admins_actifs":admins_a,"dernieres":der})
@app.route('/api/historique')
@require_auth
def hist():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT h.date, a.nom as admin, h.action, h.resultat FROM historique h LEFT JOIN admins a ON h.admin_id=a.id ORDER BY h.date DESC LIMIT 100")
    rows=[dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
    conn.close(); return jsonify(rows)
@app.route('/api/logout', methods=['POST'])
def logout(): session.clear(); return jsonify({"ok":True})
@app.route('/api/change-password', methods=['POST'])
@require_auth
def change_pwd():
    data=request.json; old=data.get('old_code'); new=data.get('new_code')
    if not new or len(new)<8 or not new.startswith('Amatrix'): return jsonify({"error":"Nouveau code doit commencer par Amatrix et 8+ chars"}),400
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT password_hash FROM admins WHERE id=?",(session['admin_id'],))
    h=cur.fetchone()[0]
    try: ph.verify(h, old)
    except: conn.close(); return jsonify({"error":"Ancien code incorrect"}),401
    cur.execute("UPDATE admins SET password_hash=? WHERE id=?",(ph.hash(new),session['admin_id']))
    cur.execute("INSERT INTO historique (admin_id,action,resultat) VALUES (?,?,?)",(session['admin_id'],"Changement code","Succès"))
    conn.commit(); conn.close(); return jsonify({"success":True})
@app.route('/')
def root(): return send_from_directory('../','index.html')
if __name__=='__main__':
    print("🔒 Serveur sécurisé AMATRIX - Argon2id - Port 5000 - Accueil préservé")
    app.run(host='0.0.0.0',port=5000,debug=False)
