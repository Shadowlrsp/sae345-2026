#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                            template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''
          SELECT lp.meuble_id,
                 lp.utilisateur_id,
                 lp.quantite,
                 m.nom_meuble                  AS nom,
                 m.prix_meuble                 AS prix,
                 (m.prix_meuble * lp.quantite) AS total_ligne
          FROM ligne_panier lp
                   JOIN meuble m ON m.id_meuble = lp.meuble_id
          WHERE lp.utilisateur_id = %s \
          '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql = '''
              SELECT SUM(m.prix_meuble * lp.quantite) AS prix_total
              FROM ligne_panier lp
                       JOIN meuble m ON m.id_meuble = lp.meuble_id
              WHERE lp.utilisateur_id = %s '''
        mycursor.execute(sql, (id_client,))
        result = mycursor.fetchone()
        prix_total = result['prix_total']
    else:
        prix_total = None

    mycursor.execute("SELECT * FROM adresse WHERE utilisateur_id = %s AND valide = 1 ORDER BY est_favorite DESC",
                     (id_client,))
    adresses = mycursor.fetchall()

    # etape 2 : selection des adresses
    return render_template('client/boutique/panier_validation_adresses.html'
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , validation=1
                           , adresses=adresses
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    id_adresse_livraison = request.form.get('id_adresse_livraison')
    id_adresse_facturation = request.form.get('id_adresse_facturation')

    if request.form.get('adresse_identique') == 'adresse_identique':
        id_adresse_facturation = id_adresse_livraison

    mycursor.execute("UPDATE adresse SET est_favorite = 0 WHERE utilisateur_id = %s", (id_client,))
    mycursor.execute("UPDATE adresse SET est_favorite = 1 WHERE id_adresse = %s", (id_adresse_livraison,))

    # choix de(s) (l')adresse(s)

    id_client = session['id_user']
    sql = '''
          SELECT lp.*, m.prix_meuble
          FROM ligne_panier lp
                   JOIN meuble m ON m.id_meuble = lp.meuble_id
          WHERE lp.utilisateur_id = %s '''
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()

    sql = '''
          INSERT INTO commande(date_achat, utilisateur_id, etat_id, adresse_livraison_id, adresse_facturation_id)
          VALUES (NOW(), %s, 1, %s, %s) \
          '''
    mycursor.execute(sql, (id_client, id_adresse_livraison, id_adresse_facturation))

    sql = '''SELECT last_insert_id() as last_insert_id'''
    mycursor.execute(sql)
    id_commande = mycursor.fetchone()['last_insert_id']
    # numéro de la dernière commande

    for item in items_ligne_panier:
        sql = '''
              DELETE
              FROM ligne_panier
              WHERE utilisateur_id = %s
                AND meuble_id = %s '''
        mycursor.execute(sql, (id_client, item['meuble_id']))

        sql = '''
              INSERT INTO ligne_commande(commande_id, meuble_id, prix, quantite)
              VALUES (%s, %s, %s, %s) '''
        mycursor.execute(sql, (id_commande,
                               item['meuble_id'],
                               item['prix_meuble'],
                               item['quantite']))

    get_db().commit()
    flash(u'Commande ajoutée', 'alert-success')
    return redirect('/client/article/show')


@client_commande.route('/client/commande/show', methods=['get', 'post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
          SELECT c.id_commande,
                 c.date_achat,
                 c.etat_id,
                 e.libelle,
                 COUNT(lc.meuble_id)                   AS nbr_articles,
                 IFNULL(SUM(lc.prix * lc.quantite), 0) AS prix_total
          FROM commande c
                   LEFT JOIN ligne_commande lc ON lc.commande_id = c.id_commande
                   LEFT JOIN etat e ON e.id_etat = c.etat_id
          WHERE c.utilisateur_id = %s
          GROUP BY c.id_commande, c.date_achat, c.etat_id, e.libelle
          ORDER BY c.date_achat ASC '''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = []
    commande_adresses = {}

    id_commande = request.args.get('id_commande', None)

    if id_commande != None:
        sql_verif = "SELECT * FROM commande WHERE id_commande = %s AND utilisateur_id = %s"
        mycursor.execute(sql_verif, (id_commande, id_client))
        commande_existante = mycursor.fetchone()

        if not commande_existante:
            flash(u"Commande introuvable", 'alert-warning')
            return redirect('/client/commande/show')

        sql = '''
              SELECT lc.*,
                     m.nom_meuble            AS nom,
                     (lc.prix * lc.quantite) AS prix_ligne
              FROM ligne_commande lc
                       JOIN meuble m ON m.id_meuble = lc.meuble_id
              WHERE lc.commande_id = %s '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()

        # partie 2 : selection de l'adresse de livraison et de facturation de la commande selectionnée
        mycursor.execute('''
            SELECT al.nom AS nom_liv,
            al.rue AS rue_liv,
            al.code_postal AS cp_liv,
            al.ville AS ville_liv,
            af.nom AS nom_fac,
            af.rue AS rue_fac,
            af.code_postal AS cp_fac,
            af.ville AS ville_fac
            FROM commande c
            LEFT JOIN adresse al ON c.adresse_livraison_id = al.id_adresse
            LEFT JOIN adresse af ON c.adresse_facturation_id = af.id_adresse
            WHERE c.id_commande = %s ''', (id_commande,))
        commande_adresses = mycursor.fetchone()

    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )
