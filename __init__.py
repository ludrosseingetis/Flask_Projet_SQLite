from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    # Assurez-vous que 'hello.html' existe bien dans le dossier templates
    return render_template('hello.html')

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
            session['role'] = 'admin'
            return redirect(url_for('lecture'))
            
        elif request.form['username'] == 'user' and request.form['password'] == '1234':
            session['authentifie'] = True
            session['role'] = 'user'
            return redirect(url_for('ReadficheNom', post_nom='Dupont'))
            
        else:
            return render_template('formulaire_authentification.html', error=True)
            
    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_nom/<string:post_nom>')
def ReadficheNom(post_nom):
    if not est_authentifie() or session.get('role') != 'user':
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM clients WHERE nom LIKE ?', (post_nom,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

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

@app.route('/stock/')
def Readstock():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client_route():
    # Si c'est un GET, on affiche le formulaire
    if request.method == 'GET':
        return render_template('formulaire.html')
    
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
        conn.commit()
        conn.close()
        return redirect('/consultation/')

if __name__ == "__main__":
  app.run(debug=True)
