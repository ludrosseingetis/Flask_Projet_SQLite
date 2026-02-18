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
# ROUTES TACHES (Sur BDD 2 + BDD 1)
# ==========================================

@app.route('/taches/')
def ReadTaches():
    # 1. Récupérer les Tâches depuis BDD 2
    conn2 = get_db2_connection()
    taches_rows = conn2.execute('SELECT * FROM taches').fetchall()
    conn2.close()

    # 2. Récupérer les Clients depuis BDD 1 (pour avoir les noms)
    conn1 = get_db_connection()
    clients_rows = conn1.execute('SELECT * FROM clients').fetchall()
    conn1.close()

    # 3. Fusionner les données manuellement (Jointure Python)
    # On crée un dictionnaire pour trouver rapidement un client par son ID
    clients_dict = {client['id']: client for client in clients_rows}
    
    data_fusionnee = []
    for tache in taches_rows:
        # On convertit la ligne SQLite en dictionnaire pour pouvoir la modifier
        tache_dict = dict(tache)
        
        # On cherche le client associé
        client_associe = clients_dict.get(tache['id_client'])
        
        if client_associe:
            tache_dict['nom'] = client_associe['nom']
            tache_dict['prenom'] = client_associe['prenom']
        else:
            tache_dict['nom'] = "Client Inconnu"
            tache_dict['prenom'] = ""
            
        data_fusionnee.append(tache_dict)
    
    return render_template('read_data.html', data=data_fusionnee)


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
