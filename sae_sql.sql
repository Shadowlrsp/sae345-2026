DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS meuble;
DROP TABLE IF EXISTS type_meuble;
DROP TABLE IF EXISTS materiau;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS etat;

CREATE TABLE etat (
  id_etat INT NOT NULL AUTO_INCREMENT,
  libelle VARCHAR(255) NOT NULL,
  PRIMARY KEY (id_etat)
);

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

CREATE TABLE materiau (
  id_materiau INT NOT NULL AUTO_INCREMENT,
  libelle_materiau VARCHAR(255) NOT NULL,
  PRIMARY KEY (id_materiau)
);

CREATE TABLE type_meuble (
  id_type_meuble INT NOT NULL AUTO_INCREMENT,
  libelle_type_meuble VARCHAR(255) NOT NULL,
  PRIMARY KEY (id_type_meuble)
);

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
  materiau_id INT NOT NULL,
  type_meuble_id INT NOT NULL,
  PRIMARY KEY (id_meuble)
);

CREATE TABLE commande (
  id_commande INT NOT NULL AUTO_INCREMENT,
  date_achat DATETIME NOT NULL,
  utilisateur_id INT NOT NULL,
  etat_id INT NOT NULL,
  PRIMARY KEY (id_commande)
);

CREATE TABLE ligne_commande (
  commande_id INT NOT NULL,
  meuble_id INT NOT NULL,
  prix DECIMAL(10,2),
  quantite INT,
  PRIMARY KEY (commande_id, meuble_id)
);

CREATE TABLE ligne_panier (
  utilisateur_id INT NOT NULL,
  meuble_id INT NOT NULL,
  quantite INT,
  date_ajout DATETIME,
  PRIMARY KEY (utilisateur_id, meuble_id)
);

ALTER TABLE meuble
  ADD CONSTRAINT fk_meu_mat FOREIGN KEY (materiau_id) REFERENCES materiau(id_materiau),
  ADD CONSTRAINT fk_meu_typ FOREIGN KEY (type_meuble_id) REFERENCES type_meuble(id_type_meuble);

ALTER TABLE commande
ADD CONSTRAINT fk_cmd_uti FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
ADD CONSTRAINT fk_cmd_eta FOREIGN KEY (etat_id) REFERENCES etat(id_etat);

ALTER TABLE ligne_commande
ADD CONSTRAINT fk_lic_cmd FOREIGN KEY (commande_id) REFERENCES commande(id_commande),
ADD CONSTRAINT fk_lic_meu FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble);

ALTER TABLE ligne_panier
ADD CONSTRAINT fk_lip_uti FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
ADD CONSTRAINT fk_lip_meu FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble);

# temporaire pour test à refaire proprement
INSERT INTO utilisateur(id_utilisateur, login, email, password, role, nom, est_actif) VALUES
(1,'admin','admin@admin.fr','scrypt:32768:8:1$irSP6dJEjy1yXof2$56295be51bb989f467598b63ba6022405139656d6609df8a71768d42738995a21605c9acbac42058790d30fd3adaaec56df272d24bed8385e66229c81e71a4f4','ROLE_admin','admin',1),
(2,'client','client@client.fr','scrypt:32768:8:1$iFP1d8bdBmhW6Sgc$7950bf6d2336d6c9387fb610ddaec958469d42003fdff6f8cf5a39cf37301195d2e5cad195e6f588b3644d2a9116fa1636eb400b0cb5537603035d9016c15910','ROLE_client','client',1),
(3,'client2','client2@client2.fr','scrypt:32768:8:1$l3UTNxiLZGuBKGkg$ae3af0d19f0d16d4a495aa633a1cd31ac5ae18f98a06ace037c0f4fb228ed86a2b6abc64262316d0dac936eb72a67ae82cd4d4e4847ee0fb0b19686ee31194b3','ROLE_client','client2',1);

INSERT INTO etat (libelle) VALUES ('En attente'), ('En préparation'), ('Expédié'), ('Livré'), ('Annulé');
INSERT INTO materiau (libelle_materiau) VALUES ('Chêne Massif'), ('Acier Noir'), ('Velours'), ('Marbre Blanc');
INSERT INTO type_meuble (libelle_type_meuble) VALUES ('Assises'), ('Tables'), ('Rangement'), ('Luminaires');

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
('Applique Murale Laiton', 15.00, 25.00, 62.00, 'LightUp', 'Flash', 'applique_murale.jpg', 22, 2, 4);

INSERT INTO commande (date_achat, utilisateur_id, etat_id) VALUES
('2026-01-20 10:30:00', 2, 4),
('2026-01-21 11:30:00', 2, 4),
('2026-01-22 14:45:00', 2, 4),
('2026-01-22 12:12:00', 3, 4),
('2026-01-23 14:15:00', 2, 4),
('2026-01-23 15:13:00', 3, 4),
('2026-01-23 12:21:00', 2, 4),
('2026-01-24 11:45:00', 2, 4),
('2026-01-25 06:41:00', 3, 4),
('2026-01-25 20:11:00', 3, 4),
('2026-01-25 19:04:00', 3, 4),
('2026-01-26 17:55:00', 2, 4),
('2026-01-26 14:41:00', 3, 4),
('2026-01-26 13:23:00', 2, 4),
('2026-01-26 11:41:00', 2, 4),
('2026-01-26 15:53:00', 3, 4),
('2026-01-27 17:16:00', 2, 4),
('2026-01-29 15:22:00', 3, 4),
('2026-01-19 21:38:27', 3, 2),
('2026-01-24 06:40:54', 3, 2),
('2026-01-18 15:28:42', 3, 3),
('2026-01-31 09:08:22', 3, 3),
('2026-01-27 08:37:58', 3, 3),
('2026-01-16 19:24:55', 3, 3),
('2026-01-1 19:09:22', 3, 1),
('2026-01-11 16:48:59', 3, 1),
('2026-01-30 09:14:52', 3, 3),
('2026-01-9 16:09:04', 3, 1),
('2026-01-2 10:35:59', 3, 2),
('2026-01-15 12:20:09', 3, 3),
('2026-01-5 11:27:56', 3, 4),
('2026-01-5 11:02:54', 3, 4),
('2026-01-16 10:01:05', 3, 1),
('2026-01-25 18:40:44', 3, 1),
('2026-01-16 19:29:17', 3, 1),
('2026-01-23 07:38:23', 3, 2),
('2026-01-2 17:30:01', 3, 2),
('2026-01-28 09:58:36', 3, 3),
('2026-01-19 12:18:24', 3, 4),
('2026-01-7 20:09:11', 3, 3),
('2026-01-7 21:42:09', 3, 3),
('2026-01-28 21:40:18', 3, 1),
('2026-01-6 14:23:12', 3, 4),
('2026-01-27 15:24:46', 3, 2),
('2026-01-10 20:43:08', 3, 1),
('2026-01-8 17:29:36', 3, 3),
('2026-01-30 12:13:21', 3, 3),
('2026-01-16 20:37:14', 3, 1),
('2026-01-5 21:04:25', 3, 3),
('2026-01-1 07:22:43', 3, 3),
('2026-01-23 21:56:25', 3, 4),
('2026-01-1 12:30:46', 3, 2),
('2026-01-3 12:26:32', 3, 1),
('2026-01-22 17:44:54', 3, 3),
('2026-01-23 21:32:29', 3, 2),
('2026-01-8 20:19:16', 3, 2),
('2026-01-2 21:00:30', 3, 4),
('2026-01-26 16:59:13', 3, 3),
('2026-01-15 20:47:14', 3, 1),
('2026-01-24 15:59:37', 3, 1),
('2026-01-22 20:39:59', 3, 4),
('2026-01-12 11:57:59', 3, 4),
('2026-01-18 21:18:55', 3, 2),
('2026-01-12 19:42:32', 3, 1),
('2026-01-7 07:05:26', 3, 1),
('2026-01-10 08:50:34', 3, 3),
('2026-01-3 14:09:28', 3, 1),
('2026-01-21 21:30:37', 3, 4),
('2026-01-29 12:27:00', 3, 4),
('2026-01-23 14:15:00', 3, 1);

INSERT INTO ligne_commande (commande_id, meuble_id, prix, quantite) VALUES
(1, 1, 129.00, 4),
(1, 6, 550.00, 2),
(7, 15, 520.99, 10),
(10, 9, 810.5, 2),
(12, 9, 740.0, 8),
(10, 12, 250.0, 4),
(16, 11, 790.0, 1),
(1, 4, 680.99, 1),
(6, 3, 820.99, 10),
(9, 15, 620.5, 8),
(3, 12, 210.0, 7),
(13, 4, 90.0, 10),
(15, 9, 410.0, 7),
(11, 7, 530.0, 10),
(18, 4, 440.0, 6),
(9, 6, 380.0, 10),
(14, 14, 210.5, 9),
(11, 12, 210.49, 8),
(7, 13, 340.49, 3),
(17, 9, 340.0, 7),
(14, 10, 970.0, 4),
(6, 2, 890.99, 4),
(19, 3, 920.99, 3),
(6, 5, 160.5, 5),
(15, 3, 920.99, 5),
(17, 15, 240.99, 5),
(10, 6, 430.99, 2),
(2, 14, 340.5, 9),
(15, 5, 530.0, 10),
(5, 4, 180.49, 6),
(14, 4, 930.0, 7),
(11, 11, 370.0, 3),
(14, 1, 300.0, 3),
(7, 9, 460.0, 1),
(18, 2, 780.49, 9),
(7, 8, 790.99, 7),
(5, 13, 290.49, 9),
(13, 5, 730.49, 7),
(13, 6, 680.5, 8),
(2, 5, 850.99, 3),
(2, 6, 580.0, 2),
(17, 1, 870.5, 8),
(19, 10, 260.0, 6),
(17, 13, 610.49, 7),
(9, 3, 920.99, 5),
(4, 14, 100.49, 4),
(6, 15, 730.49, 9),
(2, 1, 490.99, 3),
(14, 12, 790.5, 1),
(1, 2, 780.0, 1),
(7, 1, 310.49, 5),
(10, 2, 690.0, 8),
(2, 13, 115.00, 1);

INSERT INTO ligne_panier (utilisateur_id, meuble_id, quantite, date_ajout) VALUES
(2, 1, 3, '2026-01-24 19:25:00'),
(2, 11, 1, '2026-01-24 21:12:00'),
(2, 5, 2, '2026-01-24 22:27:00'),
(2, 4, 1, '2026-01-24 09:51:00'),
(2, 8, 1, '2026-01-24 10:21:00'),
(3, 2, 28, '2026-01-24 09:00:00'),
(3, 5, 23, '2026-01-24 09:05:00'),
(3, 13, 9, '2026-01-24 12:15:00'),
(3, 7, 38, '2026-01-24 14:44:00'),
(3, 8, 19, '2026-01-24 15:32:00'),
(3, 12, 9, '2026-01-24 07:27:00'),
(3, 6, 26, '2026-01-31 21:14:51'),
(3, 10, 20, '2026-01-11 17:39:01'),
(3, 11, 7, '2026-01-07 22:09:34'),
(3, 9, 7, '2026-01-21 16:26:50'),
(3, 15, 30, '2026-01-09 21:48:30'),
(3, 1, 15, '2026-01-14 06:18:49'),
(3, 3, 10, '2026-01-01 21:04:15'),
(3, 4, 28, '2026-01-08 08:55:52'),
(3, 14, 3, '2026-01-23 22:50:28');