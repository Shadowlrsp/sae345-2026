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
            SELECT lp.meuble_declinaison_id AS id_article,
                   m.nom_meuble AS nom,
                   d.prix_declinaison AS prix,
                   d.stock,         
                   lp.quantite,
                   (d.prix_declinaison * lp.quantite) AS total_ligne,
                   c.id_couleur,
                   c.libelle_couleur,
                   ta.id_taille,
                   ta.libelle_taille
            FROM ligne_panier lp
            JOIN declinaison_meuble d ON lp.meuble_declinaison_id = d.id_declinaison_meuble
            JOIN meuble m ON d.meuble_id = m.id_meuble
            LEFT JOIN couleur c ON d.couleur_id = c.id_couleur
            LEFT JOIN taille ta ON d.taille_id = ta.id_taille
            WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        # 2. Le prix total passe bien par les déclinaisons (d.prix_declinaison)
        sql_total = '''
                  SELECT SUM(d.prix_declinaison * lp.quantite) AS prix_total
                  FROM ligne_panier lp
                  JOIN declinaison_meuble d ON d.id_declinaison_meuble = lp.meuble_declinaison_id
                  WHERE lp.utilisateur_id = %s '''
        mycursor.execute(sql_total, (id_client,))
        result = mycursor.fetchone()
        prix_total = result['prix_total']
    else:
        prix_total = None

    return render_template('client/boutique/panier_validation_adresses.html'
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , validation=1
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql_panier = '''
              SELECT lp.meuble_declinaison_id, 
                     lp.quantite, 
                     d.prix_declinaison AS prix
              FROM ligne_panier lp
              JOIN declinaison_meuble d ON d.id_declinaison_meuble = lp.meuble_declinaison_id
              WHERE lp.utilisateur_id = %s '''
    mycursor.execute(sql_panier, (id_client,))
    items_ligne_panier = mycursor.fetchall()

    if not items_ligne_panier:
        flash(u'Votre panier est vide', 'alert-warning')
        return redirect('/client/article/show')

    sql_insert_commande = '''
              INSERT INTO commande(date_achat, utilisateur_id, etat_id)
              VALUES (NOW(), %s, 1) '''
    mycursor.execute(sql_insert_commande, (id_client,))

    sql_last_id = '''SELECT last_insert_id() as last_insert_id'''
    mycursor.execute(sql_last_id)
    id_commande = mycursor.fetchone()['last_insert_id']

    for item in items_ligne_panier:
        sql_insert_ligne = '''
                  INSERT INTO ligne_commande(commande_id, meuble_declinaison_id, prix, quantite)
                  VALUES (%s, %s, %s, %s) '''
        mycursor.execute(sql_insert_ligne, (id_commande,
                                            item['meuble_declinaison_id'],
                                            item['prix'],
                                            item['quantite']))

    sql_delete_panier = "DELETE FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql_delete_panier, (id_client,))

    get_db().commit()
    flash(u'Commande validée avec succès !', 'alert-success')
    return redirect('/client/article/show')

@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = ''' 
          SELECT c.id_commande,
                 c.date_achat,
                 c.etat_id,
                 e.libelle,
                 COUNT(lc.meuble_declinaison_id) AS nbr_articles,
                 IFNULL(SUM(lc.prix * lc.quantite), 0) AS prix_total
          FROM commande c
          LEFT JOIN ligne_commande lc ON lc.commande_id = c.id_commande
          LEFT JOIN etat e ON e.id_etat = c.etat_id
          WHERE c.utilisateur_id = %s
          GROUP BY c.id_commande, c.date_achat, c.etat_id, e.libelle
          ORDER BY c.date_achat DESC '''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = []
    id_commande = request.args.get('id_commande', None)

    if id_commande:
        sql = '''
              SELECT lc.prix, lc.quantite,
                     m.nom_meuble AS nom,
                     (lc.prix * lc.quantite) AS prix_ligne,
                     cou.libelle_couleur,
                     tai.libelle_taille
              FROM ligne_commande lc
              JOIN declinaison_meuble d ON d.id_declinaison_meuble = lc.meuble_declinaison_id
              JOIN meuble m ON m.id_meuble = d.meuble_id
              LEFT JOIN couleur cou ON d.couleur_id = cou.id_couleur
              LEFT JOIN taille tai ON d.taille_id = tai.id_taille
              WHERE lc.commande_id = %s '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()

    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           )