import sqlite3
import os

db_name = 'database2.db'
# On vérifie si le fichier existe déjà pour ne pas écraser le schéma
db_exists = os.path.exists(db_name)

connection = sqlite3.connect(db_name)

# On n'exécute le schéma que si la base vient d'être créée
if not db_exists:
    with open('schema2.sql') as f:
        connection.executescript(f.read())
    print("Base de données initialisée.")

cur = connection.cursor()

cur.execute("INSERT INTO clients (nom, prenom) VALUES (?, ?)", ('DUPONT', 'Emilie'))

connection.commit()
connection.close()
