from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os # Indispensable pour que le chemin de la BDD soit toujours juste

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# --- FONCTION DE CONNEXION SÉCURISÉE ---
# Cette fonction gère le chemin et active les noms de colonnes pour TOUTES les routes
def get_db_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Permet d'utiliser livre['titre']
    return conn

def est_authentifie():
    return session.get('authentifie')

# --- ROUTE PRINCIPALE (LIVRES) ---
@app.route('/')
def hello_world():
    conn = get_db_connection()
    
    # Logique de recherche
    query = request.args.get('recherche')
    if query:
        sql = "SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?"
        cursor = conn.execute(sql, ('%' + query + '%', '%' + query + '%'))
        livres = cursor.fetchall()
    else:
        cursor = conn.execute('SELECT * FROM livres')
        livres = cursor.fetchall()
    
    conn.close()
    
    # IMPORTANT : Assure-toi que ton fichier HTML s'appelle bien 'hello.html' 
    # ou change le nom ici pour 'read_datastock.html'
    return render_template('hello.html', livres=livres, admin=est_authentifie())

# --- GESTION DES LIVRES ---

@app.route('/ajouter_livre', methods=['POST'])
def ajouter_livre():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    titre = request.form['titre']
    auteur = request.form['auteur']
    genre = request.form['genre']

    conn = get_db_connection()
    # On ajoute un livre (assure-toi que ta table a bien ces 3 colonnes)
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


# --- AUTHENTIFICATION ---

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Login simple : admin / password
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('hello_world'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

# --- GESTION DES CLIENTS ---

@app.route('/consultation/')
def ReadBDD():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# --- DÉMARRAGE ---
if __name__ == "__main__":
  app.run(debug=True)
