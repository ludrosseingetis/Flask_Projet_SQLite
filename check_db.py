import sqlite3
import os

db_name = 'database2.db'

# 1. Vérifier si le fichier existe physiquement
if not os.path.exists(db_name):
    print(f"❌ Le fichier '{db_name}' n'existe pas.")
else:
    print(f"✅ Le fichier '{db_name}' existe.")
    
    try:
        connection = sqlite3.connect(db_name)
        cur = connection.cursor()

        # 2. Lister toutes les tables créées par l'utilisateur
        # On exclut 'sqlite_sequence' qui est une table interne pour les AUTOINCREMENT
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        tables = cur.fetchall()

        if len(tables) == 0:
            print("⚠️ La base de données est vide (aucune table n'a été créée).")
        else:
            print(f"✅ Tables trouvées : {len(tables)}")
            
            # 3. Compter les données dans chaque table
            for table in tables:
                table_name = table[0]
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                print(f"   - Table '{table_name}' : {count} enregistrement(s)")
                
                # Optionnel : Afficher le contenu
                if count > 0:
                    print(f"     --- Contenu de '{table_name}' ---")
                    cur.execute(f"SELECT * FROM {table_name}")
                    rows = cur.fetchall()
                    for row in rows:
                        print(f"     {row}")
                    print("     -----------------------------")

        connection.close()

    except sqlite3.Error as e:
        print(f"❌ Erreur lors de la lecture de la base : {e}")
