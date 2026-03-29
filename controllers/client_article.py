#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                           template_folder='templates')


@client_article.route('/client/index')
@client_article.route('/client/article/show')
def client_article_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''SELECT m.id_meuble AS id_article,
       m.nom_meuble AS nom,
       MIN(dm.prix_declinaison) AS prix,
       SUM(dm.stock) AS stock,
       m.photo AS image,
       ma.libelle_materiau AS libelle_materiau,
       t.libelle_type_meuble AS libelle_type_meuble,
       t.id_type_meuble AS type_meuble_id,
       COUNT(dm.id_declinaison_meuble) AS nb_declinaison
       FROM meuble m
       LEFT JOIN materiau ma ON m.materiau_id = ma.id_materiau
       LEFT JOIN type_meuble t ON m.type_meuble_id = t.id_type_meuble
       LEFT JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id
    '''

    list_param = []
    condition_and = []


    if session.get('filter_word'):
        condition_and.append(" m.nom_meuble LIKE %s ")
        list_param.append("%" + session['filter_word'] + "%")

    if session.get('filter_prix_min'):
        condition_and.append(" m.prix_meuble >= %s ")
        list_param.append(session['filter_prix_min'])

    if session.get('filter_prix_max'):
        condition_and.append(" m.prix_meuble <= %s ")
        list_param.append(session['filter_prix_max'])

    if session.get('filter_types'):
        placeholders = ', '.join(['%s'] * len(session['filter_types']))
        condition_and.append(f" m.type_meuble_id IN ({placeholders}) ")
        list_param.extend(session['filter_types'])

    if len(condition_and) > 0:
        sql += " WHERE " + " AND ".join(condition_and)

    sql += """ GROUP BY 
               m.id_meuble, 
               m.nom_meuble, 
               m.prix_meuble, 
               m.stock, 
               m.photo, 
               ma.libelle_materiau, 
               t.libelle_type_meuble, 
               t.id_type_meuble
               ORDER BY m.nom_meuble; """

    # Note : Le GROUP BY est inutile ici car il n'y a plus de calcul de moyenne
    # On retire le GROUP BY car il n'y a plus de fonction d'agrégation (AVG, COUNT)

    # utilisation du filtre
    sql3 = ''' prise en compte des commentaires et des notes dans le SQL    '''

    mycursor.execute(sql, tuple(list_param))
    articles = mycursor.fetchall()

    sql_types = '''
        SELECT id_type_meuble AS id_type_article, 
               libelle_type_meuble AS libelle
        FROM type_meuble
        ORDER BY libelle_type_meuble;
    '''
    mycursor.execute(sql_types)
    types_article = mycursor.fetchall()

    sql_panier = '''
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
    mycursor.execute(sql_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql_total = ''' 
                  SELECT SUM(d.prix_declinaison * lp.quantite) AS prix_total
                  FROM ligne_panier lp
                  JOIN declinaison_meuble d ON d.id_declinaison_meuble = lp.meuble_declinaison_id
                  WHERE lp.utilisateur_id = %s 
        '''
        mycursor.execute(sql_total, (id_client,))
        result = mycursor.fetchone()
        prix_total = result['prix_total']
    else:
        prix_total = None

    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )