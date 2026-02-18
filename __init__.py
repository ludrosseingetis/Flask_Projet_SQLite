from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# ==========================================
# GESTION DES CONNEXIONS BDD
# ==========================================

# 1. Connexion pour la BDD des LIVRES (database.db)
def get_db_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 2. Connexion pour la BDD des CLIENTS & TACHES (database2.db)
def get_db2_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database2.db') # Cible la nouvelle BDD
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def est_authentifie():
    return session.get('authentifie')

# ==========================================
# ROUTES LIVRES (database.db)
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
# ROUTES CLIENTS & TACHES (database2.db)
# ==========================================

# NOTE : J'ai modifié cette route pour qu'elle utilise get_db2_connection()
# car 'clients' est maintenant dans database2.db
@app.route('/consultation/')
def ReadBDD():
    conn = get_db2_connection() # Utilisation de la BDD 2
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = get_db2_connection() # Utilisation de la BDD 2
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# --- NOUVELLE ROUTE TACHES ---
@app.route('/taches/')
def ReadTaches():
    conn = get_db2_connection()
    cursor = conn.cursor()
    
    # On fait une jointure pour afficher le Nom du client à côté de la tâche
    # Si tu veux juste les tâches sans le nom du client, utilise : "SELECT * FROM taches"
    sql = """
        SELECT taches.*, clients.nom, clients.prenom 
        FROM taches 
        JOIN clients ON taches.id_client = clients.id
    """
    
    # Si la jointure plante car il n'y a pas encore de clients liés, utilise simplement :
    # sql = "SELECT * FROM taches"

    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    
    # Tu devras créer un fichier 'read_taches.html' ou réutiliser 'read_data.html'
    return render_template('read_data.html', data=data)


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
