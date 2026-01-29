#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__,
                        template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()
    mycursor.execute("DROP TABLE IF EXISTS ligne_panier")
    mycursor.execute("DROP TABLE IF EXISTS ligne_commande")
    mycursor.execute("DROP TABLE IF EXISTS commande")
    mycursor.execute("DROP TABLE IF EXISTS meuble")
    mycursor.execute("DROP TABLE IF EXISTS utilisateur")
    mycursor.execute("DROP TABLE IF EXISTS etat")
    mycursor.execute("DROP TABLE IF EXISTS type_meuble")
    mycursor.execute("DROP TABLE IF EXISTS materiau")

    mycursor.execute('''
        CREATE TABLE utilisateur (
            id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
            login VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            nom VARCHAR(255) NOT NULL,
            est_actif TINYINT(1) NOT NULL DEFAULT 1
        ) DEFAULT CHARSET utf8mb4;
    ''')
    mycursor.execute('''
        INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
        (1,'admin','admin@admin.fr','scrypt:32768:8:1$irSP6dJEjy1yXof2$56295be51bb989f467598b63ba6022405139656d6609df8a71768d42738995a21605c9acbac42058790d30fd3adaaec56df272d24bed8385e66229c81e71a4f4','ROLE_admin','admin',1),
        (2,'client','client@client.fr','scrypt:32768:8:1$iFP1d8bdBmhW6Sgc$7950bf6d2336d6c9387fb610ddaec958469d42003fdff6f8cf5a39cf37301195d2e5cad195e6f588b3644d2a9116fa1636eb400b0cb5537603035d9016c15910','ROLE_client','client',1),
        (3,'client2','client2@client2.fr','scrypt:32768:8:1$l3UTNxiLZGuBKGkg$ae3af0d19f0d16d4a495aa633a1cd31ac5ae18f98a06ace037c0f4fb228ed86a2b6abc64262316d0dac936eb72a67ae82cd4d4e4847ee0fb0b19686ee31194b3','ROLE_client','client2',1);
    ''')

    mycursor.execute('''
        CREATE TABLE type_meuble (
            id_type_meuble INT AUTO_INCREMENT PRIMARY KEY,
            libelle_type_meuble VARCHAR(255) NOT NULL
        ) DEFAULT CHARSET utf8mb4;
    ''')
    mycursor.execute("INSERT INTO type_meuble (id_type_meuble, libelle_type_meuble) VALUES (1, 'Assises'), (2, 'Tables'), (3, 'Rangement'), (4, 'Luminaires');")

    mycursor.execute('''
        CREATE TABLE etat (
            id_etat INT AUTO_INCREMENT PRIMARY KEY,
            libelle VARCHAR(255) NOT NULL
        ) DEFAULT CHARSET utf8mb4;
    ''')
    mycursor.execute("INSERT INTO etat (libelle) VALUES ('En attente'), ('En préparation'), ('Expédié'), ('Livré'), ('Annulé');")

    mycursor.execute('''
        CREATE TABLE materiau (
            id_materiau INT AUTO_INCREMENT PRIMARY KEY,
            libelle_materiau VARCHAR(255) NOT NULL
        ) DEFAULT CHARSET utf8mb4;
    ''')
    mycursor.execute("INSERT INTO materiau (libelle_materiau) VALUES ('Chêne Massif'),('Acier Noir'),('Velours'),('Marbre Blanc'),('Tissu'),('Cuir'),('Similicuir'),('Bois Massif');")

    mycursor.execute('''
        CREATE TABLE meuble (
            id_meuble INT AUTO_INCREMENT PRIMARY KEY,
            nom_meuble VARCHAR(255) NOT NULL,
            largeur DECIMAL(10,2),
            hauteur DECIMAL(10,2),
            prix_meuble DECIMAL(10,2) NOT NULL,
            fournisseur VARCHAR(255),
            marque VARCHAR(255),
            photo VARCHAR(255),
            stock INT NOT NULL DEFAULT 0,
            materiau_id INT NOT NULL,
            type_meuble_id INT NOT NULL,
            CONSTRAINT fk_meuble_materiau FOREIGN KEY (materiau_id) REFERENCES materiau(id_materiau),
            CONSTRAINT fk_meuble_type FOREIGN KEY (type_meuble_id) REFERENCES type_meuble(id_type_meuble)
        ) DEFAULT CHARSET utf8mb4;
    ''')
    mycursor.execute('''
        INSERT INTO meuble (nom_meuble, largeur, hauteur, prix_meuble, fournisseur, marque, photo, stock, materiau_id, type_meuble_id) VALUES
('chaise-baroque-bleu-royal', 60.00, 105.00, 189.90, 'Casa Padrino', 'Baroque Royal', 'chaise-baroque-bleu-royal.jpg', 20, 3, 1),
('chaises-protea', 60.00, 76.50, 229.95, 'Sklum', 'Protea', 'chaises-protea.jpg', 50, 5, 1),
('chaise-tallin-tissu', 66.00, 78.00, 199.95, 'Sklum', 'Tallin', 'chaise-tallin-tissu.jpg', 30, 5, 1),
('chaise-nv-gallery-arcade', 61.00, 79.50, 279.00, 'NV Gallery', 'Arcade', 'chaise-nv-gallery-arcade.jpg', 15, 5, 1),
('chaise-royal-event', 51.00, 103.00, 129.00, 'Home Luxury', 'Wedding Royal', 'chaise-event.jpg', 100, 5, 1),
('chaise-trone-baroque-vert', 61.00, 133.00, 699.90, 'Casa Padrino', 'Trone Luxe', 'chaise-trone-baroque-vert.jpg', 5, 5, 1),
('chaise-baroque-gris-or', 70.00, 100.00, 399.90, 'Casa Padrino', 'Luxe Gold', 'chaise-baroque-gris-or.jpg', 10, 5, 1),
('chaise-chesterfield-cuir', 65.00, 108.00, 899.90, 'Casa Padrino', 'Chesterfield', 'chaise-chesterfield-cuir.jpg', 8, 5, 1),
('chaise-luxe-marron-bois', 63.00, 76.00, 1149.90, 'Casa Padrino', 'Luxury Dining', 'chaise-luxe-marron-bois.jpg', 4, 5, 1),
('chaise-design-creme-or', 57.00, 82.00, 2399.90, 'Casa Padrino', 'Gold Edition', 'chaise-design-creme-or.jpg', 2, 5, 1),
('chaise-cuir-marron-fonce', 55.00, 86.00, 699.90, 'Casa Padrino', 'Dark Leather', 'chaise-cuir-marron-fonce.jpg', 12, 5, 1),
('chaise-black-club', 48.00, 79.00, 799.90, 'Casa Padrino', 'Hotel Club', 'chaise-black-club.jpg', 20, 7, 1),
('chaise-cuir-beige-noir', 59.00, 88.00, 899.90, 'Casa Padrino', 'Nubuck Edition', 'chaise-cuir-beige-noir.jpg', 6, 6, 1),
('chaise-baroque-floral', 60.00, 93.00, 199.90, 'Casa Padrino', 'Floral Edition', 'chaise-barock.jpg', 15, 6, 1),
('chaise-longue-rio', 60.00, 33.00, 79250.90, 'Selency', 'Niemeyer', 'chaise-longue-rio.jpg', 15, 6, 1);
    ''')

    mycursor.execute('''
        CREATE TABLE commande (
            id_commande INT AUTO_INCREMENT PRIMARY KEY,
            date_achat DATETIME NOT NULL,
            utilisateur_id INT NOT NULL,
            etat_id INT NOT NULL,
            CONSTRAINT fk_commande_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
            CONSTRAINT fk_commande_etat FOREIGN KEY (etat_id) REFERENCES etat(id_etat)
        ) DEFAULT CHARSET utf8mb4;
    ''')

    mycursor.execute('''
        CREATE TABLE ligne_commande (
            commande_id INT NOT NULL,
            meuble_id INT NOT NULL,
            prix DECIMAL(10,2),
            quantite INT,
            PRIMARY KEY (commande_id, meuble_id),
            CONSTRAINT fk_ligne_cmd_commande FOREIGN KEY (commande_id) REFERENCES commande(id_commande),
            CONSTRAINT fk_ligne_cmd_meuble FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble)
        ) DEFAULT CHARSET utf8mb4;
    ''')

    mycursor.execute('''
        CREATE TABLE ligne_panier (
            utilisateur_id INT NOT NULL,
            meuble_id INT NOT NULL,
            quantite INT,
            date_ajout DATETIME,
            PRIMARY KEY (utilisateur_id, meuble_id),
            CONSTRAINT fk_panier_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
            CONSTRAINT fk_panier_meuble FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble)
        ) DEFAULT CHARSET utf8mb4;
    ''')

    get_db().commit()
    print("base de données initialisée")
    return redirect('/')
