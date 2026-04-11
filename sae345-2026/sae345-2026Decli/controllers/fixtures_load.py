#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__, template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()

    mycursor.execute("DROP TABLE IF EXISTS ligne_panier;")
    mycursor.execute("DROP TABLE IF EXISTS ligne_commande;")
    mycursor.execute("DROP TABLE IF EXISTS commande;")
    mycursor.execute("DROP TABLE IF EXISTS commentaire;")
    mycursor.execute("DROP TABLE IF EXISTS note;")
    mycursor.execute("DROP TABLE IF EXISTS declinaison_meuble;")
    mycursor.execute("DROP TABLE IF EXISTS couleur;")
    mycursor.execute("DROP TABLE IF EXISTS taille;")
    mycursor.execute("DROP TABLE IF EXISTS meuble;")
    mycursor.execute("DROP TABLE IF EXISTS utilisateur;")
    mycursor.execute("DROP TABLE IF EXISTS type_meuble;")
    mycursor.execute("DROP TABLE IF EXISTS materiau;")
    mycursor.execute("DROP TABLE IF EXISTS etat;")

    mycursor.execute('''
        CREATE TABLE etat (
          id_etat INT NOT NULL AUTO_INCREMENT,
          libelle VARCHAR(255) NOT NULL,
          PRIMARY KEY (id_etat)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE utilisateur (
          id_utilisateur INT NOT NULL AUTO_INCREMENT,
          login VARCHAR(255) NOT NULL,
          email VARCHAR(255) NOT NULL,
          password VARCHAR(255) NOT NULL,
          role VARCHAR(255) NOT NULL,
          nom VARCHAR(255) NOT NULL,
          est_actif TINYINT(1) NOT NULL DEFAULT 1,
          PRIMARY KEY (id_utilisateur)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE materiau (
          id_materiau INT NOT NULL AUTO_INCREMENT,
          libelle_materiau VARCHAR(255) NOT NULL,
          PRIMARY KEY (id_materiau)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE type_meuble (
          id_type_meuble INT NOT NULL AUTO_INCREMENT,
          libelle_type_meuble VARCHAR(255) NOT NULL,
          PRIMARY KEY (id_type_meuble)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE meuble (
          id_meuble INT NOT NULL AUTO_INCREMENT,
          nom_meuble VARCHAR(255) NOT NULL,
          largeur DECIMAL(10,2),
          hauteur DECIMAL(10,2),
          prix_meuble DECIMAL(10,2) NOT NULL,
          fournisseur VARCHAR(255),
          marque VARCHAR(255),
          photo VARCHAR(255),
          stock INT NOT NULL DEFAULT 0,
          type_meuble_id INT NOT NULL,
          materiau_id INT NOT NULL,
          description TEXT,
          actif TINYINT(1) NOT NULL DEFAULT 1,
          PRIMARY KEY (id_meuble)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE couleur (
          id_couleur INT NOT NULL AUTO_INCREMENT,
          libelle_couleur VARCHAR(255),
          code_couleur VARCHAR(255),
          PRIMARY KEY (id_couleur)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE taille (
          id_taille INT NOT NULL AUTO_INCREMENT,
          libelle_taille VARCHAR(255),
          code_taille VARCHAR(255),
          PRIMARY KEY (id_taille)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE declinaison_meuble (
          id_declinaison_meuble INT NOT NULL AUTO_INCREMENT,
          stock INT,
          prix_declinaison DECIMAL(10,2),
          couleur_id INT NOT NULL,
          taille_id INT NOT NULL,
          meuble_id INT NOT NULL,
          actif TINYINT(1) NOT NULL DEFAULT 1,
          PRIMARY KEY (id_declinaison_meuble)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE commande (
          id_commande INT NOT NULL AUTO_INCREMENT,
          date_achat DATETIME NOT NULL,
          utilisateur_id INT NOT NULL,
          etat_id INT NOT NULL,
          PRIMARY KEY (id_commande)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE ligne_commande (
          commande_id INT NOT NULL,
          meuble_declinaison_id INT NOT NULL,
          prix DECIMAL(10,2),
          quantite INT,
          PRIMARY KEY (commande_id, meuble_declinaison_id)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE ligne_panier (
          utilisateur_id INT NOT NULL,
          meuble_declinaison_id INT NOT NULL,
          quantite INT,
          date_ajout DATETIME,
          PRIMARY KEY (utilisateur_id, meuble_declinaison_id)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE commentaire (
          utilisateur_id INT NOT NULL,
          meuble_id INT NOT NULL,
          commentaire TEXT NOT NULL,
          valider TINYINT(1) NOT NULL DEFAULT 0,
          date_publication DATETIME NOT NULL,
          PRIMARY KEY (utilisateur_id, meuble_id, date_publication)
        );
    ''')

    mycursor.execute('''
        CREATE TABLE note (
          utilisateur_id INT NOT NULL,
          meuble_id INT NOT NULL,
          note INT NOT NULL,
          date_note DATETIME NOT NULL,
          PRIMARY KEY (utilisateur_id, meuble_id)
        );
    ''')

    mycursor.execute("ALTER TABLE meuble ADD CONSTRAINT fk_meu_typ FOREIGN KEY (type_meuble_id) REFERENCES type_meuble(id_type_meuble);")
    mycursor.execute("ALTER TABLE meuble ADD CONSTRAINT fk_meu_mat FOREIGN KEY (materiau_id) REFERENCES materiau(id_materiau);")
    
    mycursor.execute("ALTER TABLE declinaison_meuble ADD CONSTRAINT fk_meu_decli_couleur FOREIGN KEY (couleur_id) REFERENCES couleur(id_couleur);")
    mycursor.execute("ALTER TABLE declinaison_meuble ADD CONSTRAINT fk_meu_decli_taille FOREIGN KEY (taille_id) REFERENCES taille(id_taille);")
    mycursor.execute("ALTER TABLE declinaison_meuble ADD CONSTRAINT fk_meu_decli_meu FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble);")
    
    mycursor.execute("ALTER TABLE commande ADD CONSTRAINT fk_cmd_uti FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur);")
    mycursor.execute("ALTER TABLE commande ADD CONSTRAINT fk_cmd_eta FOREIGN KEY (etat_id) REFERENCES etat(id_etat);")
    
    mycursor.execute("ALTER TABLE ligne_commande ADD CONSTRAINT fk_lic_cmd FOREIGN KEY (commande_id) REFERENCES commande(id_commande);")
    mycursor.execute("ALTER TABLE ligne_commande ADD CONSTRAINT fk_lic_meu FOREIGN KEY (meuble_declinaison_id) REFERENCES declinaison_meuble(id_declinaison_meuble);")
    
    mycursor.execute("ALTER TABLE ligne_panier ADD CONSTRAINT fk_lip_uti FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur);")
    mycursor.execute("ALTER TABLE ligne_panier ADD CONSTRAINT fk_lip_meu FOREIGN KEY (meuble_declinaison_id) REFERENCES declinaison_meuble(id_declinaison_meuble);")
    
    mycursor.execute("ALTER TABLE commentaire ADD CONSTRAINT fk_com_uti FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur);")
    mycursor.execute("ALTER TABLE commentaire ADD CONSTRAINT fk_com_meu FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble);")
    
    mycursor.execute("ALTER TABLE note ADD CONSTRAINT fk_note_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur);")
    mycursor.execute("ALTER TABLE note ADD CONSTRAINT fk_note_meuble FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble);")

    mycursor.execute('''
        INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
        (1,'admin','admin@admin.fr','scrypt:32768:8:1$irSP6dJEjy1yXof2$56295be51bb989f467598b63ba6022405139656d6609df8a71768d42738995a21605c9acbac42058790d30fd3adaaec56df272d24bed8385e66229c81e71a4f4','ROLE_admin','admin',1),
        (2,'client','client@client.fr','scrypt:32768:8:1$iFP1d8bdBmhW6Sgc$7950bf6d2336d6c9387fb610ddaec958469d42003fdff6f8cf5a39cf37301195d2e5cad195e6f588b3644d2a9116fa1636eb400b0cb5537603035d9016c15910','ROLE_client','client',1),
        (3,'client2','client2@client2.fr','scrypt:32768:8:1$l3UTNxiLZGuBKGkg$ae3af0d19f0d16d4a495aa633a1cd31ac5ae18f98a06ace037c0f4fb228ed86a2b6abc64262316d0dac936eb72a67ae82cd4d4e4847ee0fb0b19686ee31194b3','ROLE_client','client2',1),
        (4,'client3','client3@client3.fr','scrypt:32768:8:1$hq8diH3ymWIQK8o3$8a820843c6762144a5356158f2a953e46ecccbfd013be6e01e6d266fb17e885e0d77e61fa45885c0790763c7b2aa905b722020dceae5565f5c7d4695742ef367','ROLE_client','client3',1),
        (5,'client4','client4@client4.fr','scrypt:32768:8:1$VRITasYBAWBhbDks$f7179bbaa23906a27406050350a430086c04a6aef9fbcd3f48884262e6762eb3ef1c1edcf55b0b2b43fd0636860b83fafc364ecb321a3f1a9f7da7cb8c0e872e','ROLE_client','client4',1);
    ''')

    mycursor.execute("INSERT INTO etat (libelle) VALUES ('En attente'), ('En préparation'), ('Expédié'), ('Livré'), ('Annulé');")
    mycursor.execute("INSERT INTO materiau (libelle_materiau) VALUES ('Chêne Massif'), ('Acier'), ('Velours'), ('Marbre'), ('Métal'),('Bronze'),('Laiton');")
    mycursor.execute("INSERT INTO type_meuble (libelle_type_meuble) VALUES ('Assises'), ('Tables'), ('Rangement'), ('Luminaires');")

    mycursor.execute('''
        INSERT INTO meuble (nom_meuble, largeur, hauteur, prix_meuble, fournisseur, marque, photo, stock, materiau_id, type_meuble_id, description) VALUES
        ('chaise-baroque-bleu-royal', 60.00, 105.00, 189.90, 'Casa Padrino', 'Baroque Royal', 'chaise-baroque-bleu-royal.jpg', 20, 3, 1, 'Chaise élégante au style Louis XV avec un velours bleu profond et des finitions sculptées.'),
        ('chaises-protea', 60.00, 76.50, 229.95, 'Sklum', 'Protea', 'chaises-protea.jpg', 50, 3, 1, 'Assise moderne au design organique, alliant confort ergonomique et esthétique minimaliste.'),
        ('chaise-tallin-tissu', 66.00, 78.00, 199.95, 'Sklum', 'Tallin', 'chaise-tallin-tissu.jpg', 30, 3, 1, 'Chaise scandinave épurée avec un revêtement en tissu doux, idéale pour un intérieur cosy.'),
        ('chaise-nv-gallery-arcade', 61.00, 79.50, 279.00, 'NV Gallery', 'Arcade', 'chaise-nv-gallery-arcade.jpg', 15, 3, 1, 'Une pièce design aux lignes courbes et sophistiquées pour une salle à manger chic.'),
        ('chaise-royal-event', 51.00, 103.00, 129.00, 'Home Luxury', 'Wedding Royal', 'chaise-event.jpg', 100, 3, 1, 'Chaise de réception prestigieuse, parfaite pour les mariages et événements de haut standing.'),
        ('chaise-trone-baroque-vert', 61.00, 133.00, 699.90, 'Casa Padrino', 'Trone Luxe', 'chaise-trone-baroque-vert.jpg', 5, 3, 1, 'Véritable trône majestueux en bois sculpté et velours vert émeraude pour une décoration royale.'),
        ('chaise-baroque-gris-or', 70.00, 100.00, 399.90, 'Casa Padrino', 'Luxe Gold', 'chaise-baroque-gris-or.jpg', 10, 3, 1, 'Alliance sublime du gris anthracite et de la dorure à la feuille pour un style opulent.'),
        ('chaise-chesterfield-cuir', 65.00, 108.00, 899.90, 'Casa Padrino', 'Chesterfield', 'chaise-chesterfield-cuir.jpg', 8, 3, 1, 'L''emblématique capitonnage Chesterfield décliné en chaise de bureau ou de salle à manger.'),
        ('chaise-luxe-marron-bois', 63.00, 76.00, 1149.90, 'Casa Padrino', 'Luxury Dining', 'chaise-luxe-marron-bois.jpg', 4, 3, 1, 'Artisanat d''exception en bois massif et cuir premium pour un confort inégalé.'),
        ('chaise-design-creme-or', 57.00, 82.00, 2399.90, 'Casa Padrino', 'Gold Edition', 'chaise-design-creme-or.jpg', 2, 3, 1, 'Pièce de collection en édition limitée mêlant structure dorée et textile crème soyeux.'),
        ('chaise-cuir-marron-fonce', 55.00, 86.00, 699.90, 'Casa Padrino', 'Dark Leather', 'chaise-cuir-marron-fonce.jpg', 12, 3, 1, 'Chaise de caractère en cuir vieilli, apportant une touche industrielle et luxueuse.'),
        ('chaise-black-club', 48.00, 79.00, 799.90, 'Casa Padrino', 'Hotel Club', 'chaise-black-club.jpg', 20, 3, 1, 'Assise compacte et robuste conçue pour les salons privés et hôtels de luxe.'),
        ('chaise-cuir-beige-noir', 59.00, 88.00, 899.90, 'Casa Padrino', 'Nubuck Edition', 'chaise-cuir-beige-noir.jpg', 6, 3, 1, 'Contrastes modernes entre un cuir nubuck beige et une structure noire minimaliste.'),
        ('chaise-baroque-floral', 60.00, 93.00, 199.90, 'Casa Padrino', 'Floral Edition', 'chaise-barock.jpg', 15, 3, 1, 'Motifs floraux brodés et bois blanc pour un charme romantique et printanier.'),
        ('chaise-longue-rio', 60.00, 33.00, 79250.90, 'Selency', 'Niemeyer', 'chaise-longue-rio.jpg', 15, 3, 1, 'Chef-d''œuvre du design par Oscar Niemeyer, une pièce historique alliant bois et cannage.'),
        ('Tulip Oval Table à manger', 199.00, 72.00, 10302.22, 'Sahara', 'Saarinen', 'table1.jpg', 15, 2, 2, 'Icône du design du XXe siècle, cette table ovale élimine le désordre des pieds traditionnels.'),
        ('Table à manger BLOSSOM', 180.00, 76.00, 3023.00, 'Homestorys', 'Mobitec', 'table2.jpg', 15, 1, 2, 'Table chaleureuse en bois massif avec des bords arrondis pour des repas conviviaux.'),
        ('Table a manger Rectangulaire', 220.00, 100.00, 1059.95, 'Masie', 'Flawas', 'table3.jpg', 15, 1, 2, 'Grande table robuste en fibre de bois, parfaite pour les familles nombreuses.'),
        ('Tulip oval XL', 244.00, 72.00, 8553.19, 'Homestorys', 'Mobitec', 'table4.jpg', 15, 1, 2, 'Version généreuse de la table Tulip, alliant élégance sculpturale et grande capacité.'),
        ('Table à manger DIAMANTE', 270.00, 75.00, 25498.00, 'DesignItaly', 'Sicis', 'table5.jpg', 15, 5, 2, 'Luxe ultime avec un plateau en mosaïque de verre et une structure artistique unique.'),
        ('Commode en Noir', 200.00, 73.00, 2561.00, 'Tylko', 'Tylko', 'rangement1.jpg', 15, 2, 3, 'Rangement modulaire aux finitions noires mates, précis au millimètre près.'),
        ('Rangement vinyle', 260.00, 73.00, 1840.00, 'Tylko', 'Tylko', 'rangement2.jpg', 15, 2, 3, 'Meuble spécifiquement compartimenté pour organiser votre collection de disques vinyles.'),
        ('Commode noyer', 202.00, 83.00, 1761.00, 'Tylko', 'Tylko', 'rangement3.jpg', 15, 2, 3, 'Élégance naturelle du noyer pour ce meuble de rangement spacieux et durable.'),
        ('Etagère murale', 440.00, 253.00, 10659.00, 'Tylko', 'Tylko', 'rangement4.jpg', 15, 2, 3, 'Bibliothèque monumentale s''adaptant parfaitement à vos murs pour un rangement total.'),
        ('Etagère gryd', 193.00, 160.00, 1295.00, 'Tylko', 'Tylko', 'rangement5.jpg', 15, 2, 3, 'Structure légère et moderne pour exposer vos objets de décoration avec style.'),
        ('Pipistrello - Terre de Sienne - Édition limitée Voltex', 55.00, 86.00, 1199.00, 'Voltex', 'Martilleni', 'lum1.jpg', 15, 2, 4, 'La célèbre lampe télescopique Gae Aulenti dans un coloris Terre de Sienne exclusif.'),
        ('Falling sun Chandelier', 45.00, 200.00, 1805.00, 'Grau', 'Grau', 'lum2.jpg', 15, 2, 4, 'Suspension poétique imitant la lumière du soleil couchant pour une ambiance apaisante.'),
        ('Abeleisa Lustre', 150.00, 360.00, 14000.00, 'Neutralightning', 'Neutralightning', 'lum3.jpg', 15, 7, 4, 'Lustre monumental en laiton poli, pièce maîtresse pour les grands halls d''entrée.'),
        ('Plotuvyn Lustre', 70.00, 150.00, 7905.00, 'Neutralightning', 'Neutralightning', 'lum4.jpg', 15, 7, 4, 'Linaire contemporain aux finitions dorées, alliant éclairage LED et design industriel.'),
        ('Avalon triple', 130.00, 102.00, 48410.00, 'Espace-Lumière', 'CTO-Lightening', 'lum5.jpg', 15, 6, 4, 'Luminaire de haute joaillerie en bronze et albâtre, diffusant une lumière chaude et tamisée.');
    ''')

    mycursor.execute('''
        INSERT INTO couleur (id_couleur, libelle_couleur, code_couleur) VALUES
        (1, 'Couleur Unique', '#000000'),
        (2, 'Bleu Royal', '#002366'),
        (3, 'Vert Émeraude', '#50C878'),
        (4, 'Gris Anthracite', '#383E42'),
        (5, 'Or', '#D4AF37'),
        (6, 'Noir Mat', '#28282B'),
        (7, 'Crème', '#FFFDD0'),
        (8, 'Terre de Sienne', '#A0522D'),
        (9, 'Noyer', '#5D3922');
    ''')

    mycursor.execute('''
        INSERT INTO taille (id_taille, libelle_taille, code_taille) VALUES
        (1, 'Taille Unique', 'U'),
        (2, 'Standard', 'S'),
        (3, 'Large', 'L'),
        (4, 'XL', 'XL');
    ''')

    mycursor.execute('''
        INSERT INTO declinaison_meuble (id_declinaison_meuble, stock, prix_declinaison, couleur_id, taille_id, meuble_id) VALUES
        (1, 20, 189.90, 2, 2, 1), (2, 50, 229.95, 7, 2, 2), (3, 30, 199.95, 4, 2, 3),
        (4, 15, 279.00, 2, 2, 4), (5, 100, 129.00, 7, 2, 5), (6, 5, 699.90, 3, 2, 6),
        (7, 10, 399.90, 4, 2, 7), (8, 8, 899.90, 6, 2, 8), (9, 4, 1149.90, 9, 2, 9),
        (10, 2, 2399.90, 7, 2, 10), (11, 12, 699.90, 9, 2, 11), (12, 20, 799.90, 6, 2, 12),
        (13, 6, 899.90, 6, 2, 13), (14, 15, 199.90, 7, 2, 14), (15, 15, 79250.90, 9, 2, 15),
        (16, 10, 199.90, 2, 3, 1), (17, 25, 229.95, 6, 2, 2), (18, 15, 249.95, 6, 3, 2),
        (19, 20, 199.95, 9, 2, 3), (20, 5, 289.00, 2, 3, 4), (21, 50, 129.00, 5, 2, 5),
        (22, 5, 429.90, 4, 3, 7), (23, 4, 949.90, 6, 3, 8), (24, 2, 1099.90, 6, 4, 8),
        (25, 8, 749.90, 9, 3, 11), (26, 10, 849.90, 6, 3, 12), (27, 3, 949.90, 6, 3, 13),
        (28, 10, 199.90, 4, 2, 14), (29, 2, 85000.00, 6, 3, 15), (30, 8, 249.95, 3, 3, 2);
    ''')

    mycursor.execute('''
        INSERT INTO declinaison_meuble (stock, prix_declinaison, couleur_id, taille_id, meuble_id)
        SELECT m.stock, m.prix_meuble, 1, 1, m.id_meuble
        FROM meuble m
        WHERE m.id_meuble > 15;
    ''')

    mycursor.execute('''
        INSERT INTO commande (date_achat, utilisateur_id, etat_id) VALUES
        ('2026-01-20 10:30:00', 2, 4), ('2026-01-21 11:30:00', 2, 4), ('2026-01-22 14:45:00', 2, 4),
        ('2026-01-22 12:12:00', 3, 4), ('2026-01-23 14:15:00', 2, 4), ('2026-01-23 15:13:00', 3, 4),
        ('2026-01-23 12:21:00', 2, 4), ('2026-01-24 11:45:00', 2, 4), ('2026-01-25 06:41:00', 3, 4),
        ('2026-01-25 20:11:00', 3, 4), ('2026-01-25 19:04:00', 3, 4), ('2026-01-26 17:55:00', 2, 4),
        ('2026-01-26 14:41:00', 3, 4), ('2026-01-26 13:23:00', 2, 4), ('2026-01-26 11:41:00', 2, 4),
        ('2026-01-26 15:53:00', 3, 4), ('2026-01-27 17:16:00', 2, 4), ('2026-01-29 15:22:00', 3, 4),
        ('2026-01-19 21:38:27', 3, 2);
    ''')

    mycursor.execute('''
        INSERT INTO ligne_commande (commande_id, meuble_declinaison_id, prix, quantite) VALUES
        (1, 1, 129.00, 4), (1, 6, 550.00, 1), (7, 15, 520.99, 10), (10, 9, 810.5, 2),
        (12, 9, 740.0, 8), (10, 12, 250.0, 4), (16, 11, 790.0, 1), (1, 4, 680.99, 1),
        (6, 3, 820.99, 10), (9, 15, 620.5, 8), (3, 12, 210.0, 7), (13, 4, 90.0, 10),
        (15, 9, 410.0, 7), (11, 7, 530.0, 10), (18, 4, 440.0, 6), (9, 6, 380.0, 10),
        (14, 14, 210.5, 9), (11, 12, 210.49, 8), (7, 13, 340.49, 3), (17, 9, 340.0, 7),
        (14, 10, 970.0, 4), (6, 2, 890.99, 4), (19, 3, 920.99, 3), (6, 5, 160.5, 5),
        (15, 3, 920.99, 5), (17, 15, 240.99, 5), (10, 6, 430.99, 2), (2, 14, 340.5, 9),
        (15, 5, 530.0, 10), (5, 4, 180.49, 6), (14, 4, 930.0, 7), (11, 11, 370.0, 3),
        (14, 1, 300.0, 3), (7, 9, 460.0, 1), (18, 2, 780.49, 9), (7, 8, 790.99, 7),
        (5, 13, 290.49, 9), (13, 5, 730.49, 7), (13, 6, 680.5, 8), (2, 5, 850.99, 3),
        (2, 6, 580.0, 2), (17, 1, 870.5, 8), (19, 10, 260.0, 6), (17, 13, 610.49, 7),
        (9, 3, 920.99, 5), (4, 14, 100.49, 4), (6, 15, 730.49, 9), (2, 1, 490.99, 3),
        (14, 12, 790.5, 1), (1, 2, 780.0, 1), (7, 1, 310.49, 5), (10, 2, 690.0, 8),
        (2, 13, 115.00, 1);
    ''')

    mycursor.execute('''
        INSERT INTO ligne_panier (utilisateur_id, meuble_declinaison_id, quantite, date_ajout) VALUES
        (2, 1, 3, '2026-01-24 19:25:00'), (3, 8, 1, '2026-01-24 15:32:00'), (2, 11, 1, '2026-01-24 21:12:00'),
        (2, 5, 2, '2026-01-24 22:27:00'), (2, 4, 1, '2026-01-24 09:51:00'), (2, 8, 1, '2026-01-24 10:21:00'),
        (3, 11, 3, '2026-01-23 14:15:38'), (3, 1, 1, '2026-01-14 06:18:49'), (3, 12, 6, '2026-01-26 22:39:50'),
        (3, 7, 2, '2026-01-07 16:31:52'), (3, 13, 2, '2026-01-12 07:07:07'), (3, 6, 3, '2026-01-20 21:57:20'),
        (3, 2, 10, '2026-01-11 12:55:09'), (3, 4, 10, '2026-01-07 15:25:42'), (3, 15, 9, '2026-01-22 10:56:33'),
        (3, 14, 2, '2026-01-23 22:50:28'), (3, 5, 7, '2026-01-03 22:58:55'), (3, 10, 3, '2026-01-08 13:37:52'),
        (3, 3, 2, '2026-01-24 16:53:00');
    ''')

    mycursor.execute('''
        INSERT INTO note (utilisateur_id, meuble_id, note, date_note) VALUES
        (2,1,5,'2026-03-01 10:00:00'), (3,1,4,'2026-03-01 11:00:00'), (2,2,4,'2026-03-02 10:00:00'),
        (3,2,3,'2026-03-02 11:00:00'), (2,3,5,'2026-03-03 10:00:00'), (3,3,4,'2026-03-03 11:00:00'),
        (2,16,5,'2026-03-04 10:00:00'), (3,16,4,'2026-03-04 11:00:00'), (2,17,3,'2026-03-04 12:00:00'),
        (3,17,4,'2026-03-04 13:00:00'), (2,21,5,'2026-03-04 14:00:00'), (3,21,4,'2026-03-04 15:00:00'),
        (2,26,4,'2026-03-04 16:00:00'), (3,26,5,'2026-03-04 17:00:00'), (2, 4, 5, '2026-03-08 09:15:00'),
        (3, 4, 4, '2026-03-08 10:20:00'), (2, 5, 3, '2026-03-08 14:00:00'), (3, 5, 4, '2026-03-08 15:30:00'),
        (2, 6, 5, '2026-03-09 11:00:00'), (3, 6, 5, '2026-03-09 12:45:00'), (2, 7, 4, '2026-03-10 08:00:00'),
        (3, 7, 4, '2026-03-10 09:12:00'), (2, 8, 5, '2026-03-10 16:20:00'), (3, 15, 5, '2026-03-11 10:00:00'),
        (2, 18, 4, '2026-03-11 14:20:00'), (3, 18, 2, '2026-03-11 15:10:00'), (2, 19, 5, '2026-03-12 09:00:00'),
        (3, 20, 5, '2026-03-12 11:30:00'), (2, 22, 4, '2026-03-13 10:00:00'), (3, 23, 5, '2026-03-13 14:00:00'),
        (2, 24, 5, '2026-03-13 16:45:00'), (3, 25, 3, '2026-03-14 09:20:00'), (2, 27, 4, '2026-03-14 11:00:00'),
        (3, 28, 5, '2026-03-14 13:15:00'), (2, 29, 5, '2026-03-14 15:00:00'), (3, 30, 4, '2026-03-14 17:30:00'),
        (4,1,4,'2026-03-15 10:00:00'), (4,2,5,'2026-03-15 11:00:00'), (4,3,3,'2026-03-15 12:00:00'),
        (4,4,5,'2026-03-16 09:00:00'), (4,6,4,'2026-03-16 10:30:00'), (4,8,5,'2026-03-16 14:00:00'),
        (4,18,3,'2026-03-17 09:45:00'), (4,21,4,'2026-03-17 11:00:00'), (5,1,5,'2026-03-15 13:00:00'),
        (5,2,4,'2026-03-15 14:00:00'), (5,5,4,'2026-03-16 15:00:00'), (5,7,5,'2026-03-16 16:00:00'),
        (5,15,5,'2026-03-17 10:00:00'), (5,19,4,'2026-03-17 11:30:00'), (5,23,5,'2026-03-17 13:00:00'),
        (5,30,4,'2026-03-17 15:00:00');
    ''')

    mycursor.execute('''
        INSERT INTO commentaire (utilisateur_id, meuble_id, commentaire, valider, date_publication) VALUES
        (2,1,'Chaise très confortable et élégante',1,'2026-03-05 10:00:00'),
        (3,1,'Bon rapport qualité prix',1,'2026-03-05 11:00:00'),
        (2,2,'Design moderne très réussi',1,'2026-03-06 10:00:00'),
        (3,2,'Un peu chère mais belle finition',1,'2026-03-06 11:00:00'),
        (2,3,'Parfaite pour salle à manger',1,'2026-03-06 12:00:00'),
        (2,16,'Table magnifique pour recevoir',1,'2026-03-07 10:00:00'),
        (3,16,'Grande et solide',1,'2026-03-07 11:00:00'),
        (2,21,'Très bon meuble de rangement',1,'2026-03-07 12:00:00'),
        (3,21,'Pratique et esthétique',1,'2026-03-07 13:00:00'),
        (2,26,'Lampe superbe dans le salon',1,'2026-03-07 14:00:00'),
        (3,26,'Très belle lumière',1,'2026-03-07 15:00:00'),
        (2, 4, 'Lignes magnifiques, elle fait un effet fou dans mon salon.', 1, '2026-03-08 09:20:00'),
        (3, 5, 'Idéale pour les grandes réceptions, très stable.', 1, '2026-03-08 15:45:00'),
        (2, 6, 'Un vrai trône ! La couleur verte est encore plus belle en vrai.', 1, '2026-03-09 11:10:00'),
        (3, 7, 'Le mélange gris et or est très classe, montage facile.', 1, '2026-03-10 09:30:00'),
        (2, 8, 'Le cuir est de super qualité, on sent que c''est du solide.', 1, '2026-03-10 16:30:00'),
        (3, 15, 'Une pièce de collection. Le prix est élevé mais le design est intemporel.', 1, '2026-03-11 10:05:00'),
        (3, 18, 'Un peu déçu par la couleur du bois par rapport à la photo.', 1, '2026-03-11 15:20:00'),
        (2, 19, 'Très spacieuse, on tient facilement à 8 personnes.', 1, '2026-03-12 09:15:00'),
        (3, 20, 'Le plateau en mosaïque est une œuvre d''art. Livraison très soignée.', 1, '2026-03-12 11:45:00'),
        (2, 22, 'Enfin un meuble adapté pour mes vinyles, les cases sont parfaites.', 1, '2026-03-13 10:15:00'),
        (3, 23, 'Le noyer apporte beaucoup de chaleur à la pièce.', 1, '2026-03-13 14:10:00'),
        (2, 24, 'Immense ! J''ai pu ranger toute ma bibliothèque.', 1, '2026-03-13 17:00:00'),
        (3, 25, 'Design sympa mais un peu long à monter seul.', 1, '2026-03-14 09:40:00'),
        (2, 27, 'L''effet coucher de soleil est magique le soir.', 1, '2026-03-14 11:15:00'),
        (3, 28, 'Majestueux. Installé dans l''entrée, il impressionne tous mes invités.', 1, '2026-03-14 13:30:00'),
        (2, 29, 'Style industriel chic, l''éclairage LED est puissant mais agréable.', 1, '2026-03-14 15:15:00'),
        (3, 30, 'Lumière très douce, parfait pour une ambiance tamisée.', 1, '2026-03-14 17:45:00'),
        (4,1,'Bonne chaise, confortable au quotidien.',1,'2026-03-15 10:05:00'),
        (4,2,'Très joli design, correspond bien à la description.',1,'2026-03-15 11:10:00'),
        (4,3,'Correct mais j''attendais mieux pour le prix.',1,'2026-03-15 12:10:00'),
        (4,4,'Super rendu dans mon salon, très satisfait.',1,'2026-03-16 09:10:00'),
        (4,6,'Bonne qualité globale, assise agréable.',1,'2026-03-16 10:40:00'),
        (4,8,'Excellente qualité du cuir, très durable.',1,'2026-03-16 14:10:00'),
        (4,18,'Couleur un peu différente mais reste joli.',1,'2026-03-17 09:50:00'),
        (4,21,'Pratique pour le rangement, je recommande.',1,'2026-03-17 11:10:00'),
        (5,1,'Parfaite, rien à redire.',1,'2026-03-15 13:10:00'),
        (5,2,'Bon produit mais livraison un peu longue.',1,'2026-03-15 14:10:00'),
        (5,5,'Très stable et solide, bon achat.',1,'2026-03-16 15:10:00'),
        (5,7,'Design élégant, facile à monter.',1,'2026-03-16 16:10:00'),
        (5,15,'Magnifique pièce, effet garanti.',1,'2026-03-17 10:10:00'),
        (5,19,'Grande table pratique pour famille.',1,'2026-03-17 11:40:00'),
        (5,23,'Bois de très bonne qualité.',1,'2026-03-17 13:10:00'),
        (5,30,'Ambiance parfaite avec cette lumière.',1,'2026-03-17 15:10:00');
    ''')

    get_db().commit()
    print("Base de données réinitialisée avec succès !")
    flash("La base de données a été réinitialisée.", "alert-success")
    return redirect('/')