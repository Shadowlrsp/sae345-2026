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
('chaise-baroque-bleu-royal', 60.00, 105.00, 189.90, 'Casa Padrino', 'Baroque Royal', 'chaise-baroque-bleu-royal.jpg', 20, 3, 1),
('chaises-protea', 60.00, 76.50, 229.95, 'Sklum', 'Protea', 'chaises-protea.jpg', 50, 3, 1),
('chaise-tallin-tissu', 66.00, 78.00, 199.95, 'Sklum', 'Tallin', 'chaise-tallin-tissu.jpg', 30, 3, 1),
('chaise-nv-gallery-arcade', 61.00, 79.50, 279.00, 'NV Gallery', 'Arcade', 'chaise-nv-gallery-arcade.jpg', 15, 3, 1),
('chaise-royal-event', 51.00, 103.00, 129.00, 'Home Luxury', 'Wedding Royal', 'chaise-royal-event.jpg', 100, 3, 1),
('chaise-trone-baroque-vert', 61.00, 133.00, 699.90, 'Casa Padrino', 'Trone Luxe', 'chaise-trone-baroque-vert.jpg', 5, 3, 1),
('chaise-baroque-gris-or', 70.00, 100.00, 399.90, 'Casa Padrino', 'Luxe Gold', 'chaise-baroque-gris-or.jpg', 10, 3, 1),
('chaise-chesterfield-cuir', 65.00, 108.00, 899.90, 'Casa Padrino', 'Chesterfield', 'chaise-chesterfield-cuir.jpg', 8, 3, 1),
('chaise-luxe-marron-bois', 63.00, 76.00, 1149.90, 'Casa Padrino', 'Luxury Dining', 'chaise-luxe-marron-bois.jpg', 4, 3, 1),
('chaise-design-creme-or', 57.00, 82.00, 2399.90, 'Casa Padrino', 'Gold Edition', 'chaise-design-creme-or.jpg', 2, 3, 1),
('chaise-cuir-marron-fonce', 55.00, 86.00, 699.90, 'Casa Padrino', 'Dark Leather', 'chaise-cuir-marron-fonce.jpg', 12, 3, 1),
('chaise-black-club', 48.00, 79.00, 799.90, 'Casa Padrino', 'Hotel Club', 'chaise-black-club.jpg', 20, 3, 1),
('chaise-cuir-beige-noir', 59.00, 88.00, 899.90, 'Casa Padrino', 'Nubuck Edition', 'chaise-cuir-beige-noir.jpg', 6, 3, 1),
('chaise-baroque-floral', 60.00, 93.00, 199.90, 'Casa Padrino', 'Floral Edition', 'chaise-baroque-floral.jpg', 15, 3, 1);

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
(1, 6, 550.00, 1),
(1, 6, 550.00, 1),
(5, 3, 510.5, 2),
(16, 10, 910.0, 9),
(17, 1, 420.99, 9),
(6, 9, 800.0, 1),
(13, 1, 810.99, 4),
(6, 9, 110.99, 7),
(18, 5, 660.49, 7),
(10, 5, 580.0, 6),
(1, 4, 110.49, 5),
(19, 4, 590.49, 3),
(19, 10, 240.0, 3),
(4, 6, 470.0, 7),
(7, 1, 500.0, 9),
(18, 7, 820.49, 6),
(11, 15, 940.5, 6),
(7, 4, 340.5, 4),
(3, 2, 820.49, 6),
(5, 9, 380.0, 2),
(16, 9, 640.5, 4),
(18, 12, 140.49, 6),
(10, 13, 980.49, 1),
(7, 5, 320.0, 10),
(6, 7, 510.99, 1),
(18, 15, 660.0, 9),
(4, 2, 90.49, 4),
(13, 11, 170.0, 6),
(19, 12, 180.49, 5),
(16, 13, 920.0, 1),
(17, 10, 710.0, 2),
(14, 3, 500.5, 1),
(17, 7, 860.5, 1),
(18, 7, 470.5, 10),
(7, 7, 250.5, 10),
(6, 11, 190.99, 10),
(2, 2, 720.5, 1),
(7, 15, 410.5, 8),
(2, 7, 440.5, 2),
(1, 9, 250.99, 8),
(16, 2, 310.5, 10),
(19, 15, 600.99, 8),
(17, 3, 780.49, 4),
(5, 3, 650.0, 1),
(7, 1, 510.99, 5),
(3, 9, 740.0, 2),
(16, 11, 470.5, 2),
(10, 11, 570.99, 8),
(7, 15, 210.99, 3),
(18, 5, 310.5, 9),
(7, 11, 680.49, 4),
(12, 1, 120.5, 8),
(2, 13, 115.00, 1);

INSERT INTO ligne_panier (utilisateur_id, meuble_id, quantite, date_ajout) VALUES
(3, 2, 1, '2026-01-24 09:00:00'),
(3, 5, 1, '2026-01-24 09:05:00'),
# Ajoute
(2, 1, 3, '2026-01-24 19:25:00'),
(3, 13, 5, '2026-01-24 12:15:00'),
(3, 7, 2, '2026-01-24 14:44:00'),
(3, 8, 1, '2026-01-24 15:32:00'),
(2, 11, 1, '2026-01-24 21:12:00'),
(2, 5, 2, '2026-01-24 22:27:00'),
(2, 4, 1, '2026-01-24 09:51:00'),
(3, 12, 3, '2026-01-24 07:27:00'),
(2, 8, 1, '2026-01-24 10:21:00'),
(3, 6, 6, '2026-01-31 21:14:51'),
(3, 6, 8, '2026-01-26 14:49:30'),
(3, 10, 2, '2026-01-11 17:39:01'),
(3, 8, 8, '2026-01-14 13:11:47'),
(3, 10, 6, '2026-01-31 08:42:49'),
(3, 11, 4, '2026-01-7 22:09:34'),
(3, 11, 3, '2026-01-23 14:15:38'),
(3, 9, 6, '2026-01-21 16:26:50'),
(3, 2, 9, '2026-01-16 21:40:35'),
(3, 6, 4, '2026-01-18 16:23:28'),
(3, 6, 4, '2026-01-17 09:26:31'),
(3, 15, 7, '2026-01-9 21:48:30'),
(3, 2, 6, '2026-01-25 22:57:05'),
(3, 1, 1, '2026-01-14 06:18:49'),
(3, 3, 8, '2026-01-1 21:04:15'),
(3, 12, 6, '2026-01-26 22:39:50'),
(3, 7, 2, '2026-01-7 16:31:52'),
(3, 4, 8, '2026-01-8 08:55:52'),
(3, 1, 5, '2026-01-31 08:33:27'),
(3, 13, 2, '2026-01-12 07:07:07'),
(3, 4, 6, '2026-01-27 12:50:30'),
(3, 6, 3, '2026-01-20 21:57:20'),
(3, 4, 1, '2026-01-28 21:05:23'),
(3, 2, 1, '2026-01-23 15:42:31'),
(3, 15, 4, '2026-01-18 11:51:21'),
(3, 7, 9, '2026-01-21 18:53:30'),
(3, 10, 9, '2026-01-29 07:05:39'),
(3, 6, 1, '2026-01-9 16:47:04'),
(3, 4, 3, '2026-01-9 09:26:41'),
(3, 2, 10, '2026-01-11 12:55:09'),
(3, 5, 9, '2026-01-12 08:03:03'),
(3, 7, 9, '2026-01-29 22:42:00'),
(3, 15, 10, '2026-01-5 19:59:26'),
(3, 5, 6, '2026-01-17 21:59:06'),
(3, 4, 10, '2026-01-7 15:25:42'),
(3, 7, 9, '2026-01-10 17:45:26'),
(3, 15, 9, '2026-01-22 10:56:33'),
(3, 7, 7, '2026-01-8 13:01:51'),
(3, 7, 5, '2026-01-4 18:40:42'),
(3, 14, 2, '2026-01-23 22:50:28'),
(3, 5, 7, '2026-01-3 22:58:55'),
(3, 8, 10, '2026-01-6 11:41:52'),
(3, 9, 1, '2026-01-1 22:43:37'),
(3, 10, 3, '2026-01-8 13:37:52'),
(3, 2, 10, '2026-01-18 20:33:59'),
(3, 6, 5, '2026-01-4 15:52:16'),
(3, 14, 1, '2026-01-15 17:38:55'),
(3, 1, 5, '2026-01-1 16:46:53'),
(3, 1, 8, '2026-01-9 08:23:46'),
(3, 13, 2, '2026-01-23 22:02:39'),
(3, 3, 2, '2026-01-24 16:53:00')
;
