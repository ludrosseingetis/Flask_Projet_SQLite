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
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Date de création auto
    date_echeance TEXT, -- Ta colonne de date (optionnelle)
    titre TEXT NOT NULL,
    description TEXT NOT NULL
);
