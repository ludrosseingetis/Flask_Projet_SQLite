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
# ROUTES TACHES (Sur BDD 2 UNIQUEMENT)
# ==========================================

@app.route('/taches/')
def ReadTaches():
    # On se connecte uniquement à la BDD 2
    conn = get_db2_connection()
    cursor = conn.cursor()
    
    # On effectue une jointure SQL classique car les tables 'taches' et 'clients'
    # sont supposées être toutes les deux dans database2.db
    sql = """
        SELECT *
        FROM taches 
        
    """
    
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    
    return render_template('read_data.html', data=data)

@app.route('/ajouter_tache', methods=['GET', 'POST'])
def ajouter_tache():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        # Récupération des données du formulaire
        titre = request.form.get('titre')
        description = request.form.get('description')

        conn = get_db2_connection()
        try:
            # On insère les données dans database2.db
            conn.execute('''
                INSERT INTO taches (titre, description) 
                VALUES (?, ?)
            ''', (titre, description))
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout : {e}")
        finally:
            conn.close()
        
        return redirect(url_for('ReadTaches'))

    # Si la méthode est GET (accès direct via l'URL), on affiche le formulaire
    return render_template('ajouter_tache.html')
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
