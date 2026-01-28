#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')              # remplace /client
def client_article_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = ''' SELECT m.id_meuble,
                     m.nom_meuble,
                     m.prix_meuble,
                     m.stock,
                     m.photo,
                     ma.libelle_materiau,
                     t.libelle_type_meuble
        FROM meuble m
        JOIN materiau ma ON m.materiau_id = ma.id_materiau
        JOIN type_meuble t ON m.type_meuble_id = t.id_type_meuble '''
    list_param = []
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    # pour le filtre
    sql_types = '''
        SELECT id_type_meuble, libelle_type_meuble
        FROM type_meuble
    '''
    mycursor.execute(sql_types)
    types_article = mycursor.fetchall()

    sql_panier = '''
        SELECT m.id_meuble,
               m.nom_meuble,
               m.prix_meuble AS prix,
               lp.quantite,
               (m.prix_meuble * lp.quantite) AS total_ligne
        FROM ligne_panier lp
        JOIN meuble m ON m.id_meuble = lp.meuble_id
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = 0
        for article in articles_panier:
            prix_total += article['total_ligne']
    else:
        prix_total = None

    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )

