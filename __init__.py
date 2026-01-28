from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

# --- MODIFICATION ICI : La route '/' gère maintenant l'affichage des livres ---
@app.route('/')
def hello_world():
    # Connexion spécifique pour la bibliothèque (avec accès par nom de colonne)
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row # Important pour utiliser livre['titre'] dans le HTML
    
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
    
    # On passe les livres et le statut admin au template hello.html
    return render_template('hello.html', livres=livres, admin=est_authentifie())

# --- NOUVEAU : Routes pour la gestion des LIVRES ---

@app.route('/ajouter_livre', methods=['POST'])
def ajouter_livre():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    titre = request.form['titre']
    auteur = request.form['auteur']
    genre = request.form['genre']

    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)', (titre, auteur, genre))
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world'))

@app.route('/supprimer_livre/<int:id>', methods=['POST'])
def supprimer_livre(id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM livres WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world'))

@app.route('/emprunter/<int:id_livre>', methods=['POST'])
def emprunter(id_livre):
    id_client = request.form['id_client']
    
    conn = sqlite3.connect('database.db')
    # 1. Créer l'emprunt
    conn.execute('INSERT INTO emprunts (id_client, id_livre) VALUES (?, ?)', (id_client, id_livre))
    # 2. Mettre à jour le stock
    conn.execute('UPDATE livres SET disponible = 0 WHERE id = ?', (id_livre,))
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world'))

@app.route('/rendre/<int:id_livre>', methods=['POST'])
def rendre(id_livre):
    conn = sqlite3.connect('database.db')
    conn.execute('UPDATE livres SET disponible = 1 WHERE id = ?', (id_livre,))
    conn.commit()
    conn.close()
    return redirect(url_for('hello_world'))

# --- TES ROUTES EXISTANTES (Je n'y touche pas) ---

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('lecture')) # Tu peux changer ça par url_for('hello_world') si tu préfères revenir à l'accueil
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

@app.route('/logout') # J'ai ajouté ça c'est pratique
def logout():
    session.pop('authentifie', None)
    return redirect(url_for('hello_world'))

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html') 

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Je garde ta valeur hardcodée 1002938
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

@app.route('/fiche_nom/<string:nom_client>')
def recherche_nom(nom_client):
    auth = request.authorization
    if not auth or not (auth.username == 'user' and auth.password == '12345'):
        return ('Accès réservé à l\'utilisateur "user".', 401, 
                {'WWW-Authenticate': 'Basic realm="Acces Client"'})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom_client,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# Route pour ajouter un livre (Action du formulaire)
@app.route('/ajouter_livre', methods=['POST'])
def ajouter_livre():
    # 1. Vérification de sécurité : Seul l'admin peut ajouter
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    # 2. Récupération des données tapées dans le formulaire
    titre = request.form['titre']
    auteur = request.form['auteur']
    genre = request.form['genre']

    # 3. Connexion et Enregistrement dans la Base de Données
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO livres (titre, auteur, genre) VALUES (?, ?, ?)', 
                 (titre, auteur, genre))
    conn.commit()
    conn.close()

    # 4. On retourne à la page d'accueil pour voir le nouveau livre
    return redirect(url_for('hello_world'))
                                                                                              
if __name__ == "__main__":
  app.run(debug=True)
