DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL -- Pas de virgule ici !
);

DROP TABLE IF EXISTS taches;
CREATE TABLE taches (
    id_tache INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    titre TEXT NOT NULL,
    description TEXT NOT NULL,
    id_client INTEGER NOT NULL, -- Mettre INTEGER pour correspondre à l'ID client
    FOREIGN KEY(id_client) REFERENCES clients(id) -- Pour lier les tables
);
