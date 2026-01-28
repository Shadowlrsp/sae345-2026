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
    mycursor.execute("INSERT INTO materiau (id_materiau, libelle_materiau) VALUES (1, 'Chêne Massif'), (2, 'Acier Noir'), (3, 'Velours'), (4, 'Marbre Blanc');")

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
        ('Chaise Royal Velours', 50.00, 85.00, 129.00, 'LuxDecor', 'Elegance', 'chaise_velours.jpg', 20, 3, 1),
        ('Fauteuil Lounge Loft', 75.00, 70.00, 245.00, 'NordicStyle', 'Hygge', 'fauteuil_loft.jpg', 12, 3, 1),
        ('Tabouret Industriel', 35.00, 65.00, 89.00, 'FactoryDesign', 'MetalArt', 'tabouret_indus.jpg', 15, 2, 1),
        ('Canapé 3 places Oslo', 210.00, 80.00, 890.00, 'NordicStyle', 'Hygge', 'canape_oslo.jpg', 5, 1, 1),
        ('Table Basse Moon', 80.00, 40.00, 199.00, 'StoneWorks', 'Mineral', 'table_basse_marbre.jpg', 8, 4, 2),
        ('Table à manger Stockholm', 180.00, 75.00, 550.00, 'NordicStyle', 'Hygge', 'table_chene.jpg', 10, 1, 2),
        ('Bureau d''Architecte', 140.00, 75.00, 320.00, 'FactoryDesign', 'MetalArt', 'bureau_architecte.jpg', 7, 2, 2),
        ('Console d''entrée Slim', 100.00, 85.00, 145.00, 'LuxDecor', 'Elegance', 'console_entree.jpg', 14, 2, 2),
        ('Buffet Scandinave', 160.00, 80.00, 480.00, 'NordicStyle', 'Hygge', 'buffet_scandi.jpg', 6, 1, 3),
        ('Bibliothèque Murale Totem', 90.00, 190.00, 290.00, 'FactoryDesign', 'MetalArt', 'bibliotheque_totem.jpg', 9, 2, 3),
        ('Commode 4 tiroirs Pure', 80.00, 100.00, 210.00, 'LuxDecor', 'Elegance', 'commode_blanche.jpg', 11, 1, 3),
        ('Armoire Penderie Forest', 120.00, 200.00, 650.00, 'EcoWood', 'Nature', 'armoire_penderie.jpg', 4, 1, 3),
        ('Lampadaire Arc Chrome', 35.00, 180.00, 115.00, 'LightUp', 'Flash', 'lampadaire_arc.jpg', 25, 2, 4),
        ('Suspension Globe Marbre', 30.00, 30.00, 75.00, 'StoneWorks', 'Mineral', 'suspension_marbre.jpg', 30, 4, 4),
        ('Lampe de bureau Neon', 20.00, 45.00, 49.00, 'LightUp', 'Flash', 'lampe_bureau.jpg', 18, 2, 4),
        ('Applique Murale Laiton', 15.00, 25.00, 62.00, 'LightUp', 'Flash', 'applique_marale.jpg', 22, 2, 4);
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
