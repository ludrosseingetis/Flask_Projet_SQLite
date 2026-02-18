from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# ==========================================
# GESTION DES CONNEXIONS BDD
# ==========================================

# 1. Connexion BDD PRINCIPALE (Livres + Clients)
def get_db_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 2. Connexion BDD SECONDAIRE (Tâches uniquement)
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
# Lance cette route une fois (http://localhost:5000/init_projet_db) 
# pour créer la table avec les nouvelles colonnes (date, terminé, etc.)
@app.route('/init_projet_db')
def init_projet_db():
    conn = get_db2_connection()
    # On supprime l'ancienne table pour la recréer proprement avec les nouveaux champs
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
    return "Base de données Tâches (BDD2) mise à jour pour le projet ! (Table 'taches' recréée)"

# ==========================================
# ROUTES LIVRES (Sur BDD 1)
# ==========================================

@app.route('/')
def hello_world():
    conn = get_db_connection()
    query = request.args.get('recherche')
    if query:
        sql = "SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?"
        cursor = conn.execute(sql, ('%' + query + '%', '%' + query + '%'))
        livres = cursor.fetchall()
    else:
        cursor = conn.execute('SELECT * FROM livres')
        livres = cursor.fetchall()
    conn.close()
    return render_template('hello.html', livres=livres, admin=est_authentifie())

@app.route('/ajouter_livre', methods=['POST'])
def ajouter_livre():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    titre = request.form['titre']
    auteur = request.form['auteur']
    genre = request.form['genre']

    conn = get_db_connection()
    conn.execute('INSERT INTO livres (titre, auteur, catégorie) VALUES (?, ?, ?)', (titre, auteur, genre))
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world'))

@app.route('/supprimer_livre/<int:id>', methods=['POST'])
def supprimer_livre(id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world'))

# ==========================================
# ROUTES CLIENTS (Sur BDD 1)
# ==========================================

@app.route('/consultation/')
def ReadBDD():
    # Les clients sont maintenant dans la BDD 1
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    # Les clients sont maintenant dans la BDD 1
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# ==========================================
# ROUTES PROJET TACHES (Sur BDD 2)
# ==========================================

# 1. Afficher la liste des tâches (Accueil du module Tâches)
@app.route('/taches/')
def ReadTaches():
    conn = get_db2_connection()
    cursor = conn.cursor()
    
    # On récupère les tâches avec les infos clients (LEFT JOIN pour garder les tâches même sans client)
    sql = """
        SELECT taches.*, clients.nom, clients.prenom 
        FROM taches 
        LEFT JOIN clients ON taches.id_client = clients.id
        ORDER BY taches.est_terminee ASC, taches.date_echeance ASC
    """
    
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    
    # Tu devras mettre à jour ton template HTML pour afficher 
    # 'date_echeance' et un bouton pour 'terminer' ou 'supprimer'
    return render_template('read_data.html', data=data)

# 2. Ajouter une tâche (Formulaire + Traitement)
@app.route('/taches/ajouter', methods=['GET', 'POST'])
def ajouter_tache():
    # Si c'est le formulaire (GET)
    if request.method == 'GET':
        # On a besoin de la liste des clients pour le menu déroulant
        # Attention : Les clients sont dans la BDD 1 !
        conn_clients = get_db_connection() # BDD 1
        clients = conn_clients.execute('SELECT * FROM clients').fetchall()
        conn_clients.close()
        return render_template('ajouter_tache.html', clients=clients) # Créer ce template !

    # Si c'est l'envoi (POST)
    titre = request.form['titre']
    description = request.form['description']
    date_echeance = request.form['date_echeance']
    id_client = request.form.get('id_client') # Peut être None si pas sélectionné

    conn = get_db2_connection() # BDD 2
    conn.execute('''
        INSERT INTO taches (titre, description, date_echeance, est_terminee, id_client) 
        VALUES (?, ?, ?, 0, ?)
    ''', (titre, description, date_echeance, id_client))
    conn.commit()
    conn.close()
    return redirect(url_for('ReadTaches'))

# 3. Marquer une tâche comme terminée
@app.route('/taches/terminer/<int:id_tache>')
def terminer_tache(id_tache):
    conn = get_db2_connection()
    # On inverse le statut (si 0 devient 1, si 1 devient 0) ou on met juste à 1
    conn.execute('UPDATE taches SET est_terminee = 1 WHERE id_tache = ?', (id_tache,))
    conn.commit()
    conn.close()
    return redirect(url_for('ReadTaches'))

# 4. Supprimer une tâche
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
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

if __name__ == "__main__":
  app.run(debug=True)
