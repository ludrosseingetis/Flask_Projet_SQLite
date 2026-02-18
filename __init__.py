from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# ==========================================
# GESTION DES CONNEXIONS BDD
# ==========================================

def get_db_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_db2_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database2.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def est_authentifie():
    return session.get('authentifie')

# ==========================================
# UTILITAIRE : INITIALISATION BDD PROJET
# ==========================================
@app.route('/init_projet_db')
def init_projet_db():
    conn = get_db2_connection()
    # On recrée la table avec les bonnes colonnes
    conn.execute('DROP TABLE IF EXISTS taches')
    conn.execute('''
        CREATE TABLE taches (
            id_tache INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            titre TEXT NOT NULL,
            description TEXT NOT NULL,
            date_echeance DATE,
            est_terminee BOOLEAN DEFAULT 0,
            id_client INTEGER,
            FOREIGN KEY(id_client) REFERENCES clients(id)
        )
    ''')
    conn.commit()
    conn.close()
    return "✅ Base de données réparée ! Vous pouvez maintenant utiliser l'application."

# ==========================================
# ROUTES LIVRES & ACCUEIL
# ==========================================

@app.route('/')
def hello_world():
    conn = get_db_connection()
    livres = conn.execute('SELECT * FROM livres').fetchall()
    conn.close()
    return render_template('hello.html', livres=livres, admin=est_authentifie())

# ==========================================
# ROUTES PROJET TACHES (Sur BDD 2)
# ==========================================

@app.route('/taches/')
def ReadTaches():
    conn = get_db2_connection()
    # Récupération des tâches + info client + tri par statut et date
    sql = """
        SELECT taches.*, clients.nom, clients.prenom 
        FROM taches 
        LEFT JOIN clients ON taches.id_client = clients.id
        ORDER BY taches.est_terminee ASC, taches.date_echeance ASC
    """
    taches = conn.execute(sql).fetchall()
    conn.close()
    return render_template('read_data.html', data=taches)

@app.route('/taches/ajouter', methods=['GET', 'POST'])
def ajouter_tache():
    # Affichage du formulaire
    if request.method == 'GET':
        conn_clients = get_db_connection()
        clients = conn_clients.execute('SELECT * FROM clients').fetchall()
        conn_clients.close()
        return render_template('ajouter_tache.html', clients=clients)

    # Traitement du formulaire
    titre = request.form['titre']
    description = request.form['description']
    date_echeance = request.form['date_echeance']
    id_client = request.form.get('id_client')

    conn = get_db2_connection()
    conn.execute('''
        INSERT INTO taches (titre, description, date_echeance, est_terminee, id_client) 
        VALUES (?, ?, ?, 0, ?)
    ''', (titre, description, date_echeance, id_client))
    conn.commit()
    conn.close()
    return redirect(url_for('ReadTaches'))

@app.route('/taches/terminer/<int:id_tache>')
def terminer_tache(id_tache):
    conn = get_db2_connection()
    # Bascule le statut (0 -> 1, 1 -> 0)
    conn.execute('UPDATE taches SET est_terminee = NOT est_terminee WHERE id_tache = ?', (id_tache,))
    conn.commit()
    conn.close()
    return redirect(url_for('ReadTaches'))

@app.route('/taches/supprimer/<int:id_tache>')
def supprimer_tache(id_tache):
    conn = get_db2_connection()
    conn.execute('DELETE FROM taches WHERE id_tache = ?', (id_tache,))
    conn.commit()
    conn.close()
    return redirect(url_for('ReadTaches'))

# ==========================================
# AUTHENTIFICATION
# ==========================================
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('hello_world'))
    return render_template('formulaire_authentification.html')

if __name__ == "__main__":
  app.run(debug=True)
