#! /usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime

from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                        template_folder='templates')


@client_liste_envies.route('/client/envie/add', methods=['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''SELECT COUNT(*) FROM liste_envie WHERE utilisateur_id=%s'''
    mycursor.execute(sql, (id_client,))
    get_db().commit()
    index_ = mycursor.fetchone()['COUNT(*)']
    print(index_)

    sql = '''INSERT INTO liste_envie (utilisateur_id, meuble_id, date_envie, article_index) 
             VALUES (%s, %s, NOW(), %s)'''
    mycursor.execute(sql, (id_client, id_article, index_+1))
    get_db().commit()
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envie/delete', methods=['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    sql = '''DELETE FROM liste_envie WHERE utilisateur_id = %s AND meuble_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()

    # TODO : De base ct /client/envies/show mais c vrmnt pas logique
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    # on prend tout de la liste envie et on 'transforme' en article
    sql = '''SELECT meuble.id_meuble AS id_article, stock, prix_meuble as prix, photo AS image, nom_meuble as nom 
             FROM liste_envie
          JOIN meuble ON meuble.id_meuble = liste_envie.meuble_id
          WHERE liste_envie.utilisateur_id = %s
        ORDER BY liste_envie.article_index
          '''
    mycursor.execute(sql, (id_client,))
    get_db().commit()
    articles_liste_envies = mycursor.fetchall()
    print(articles_liste_envies)

    sql = "SELECT COUNT(*) FROM liste_envie WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    nb_liste_envies = mycursor.fetchone()
    print(nb_liste_envies)
    get_db().commit()
    articles_historique = []
    return render_template('client/liste_envies/liste_envies_show.html'
                           ,articles_liste_envies=articles_liste_envies
                           , articles_historique=articles_historique
                           , nb_liste_envies=nb_liste_envies
                           )



def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    client_id = session['id_user']
    # rechercher si l'article pour cet utilisateur est dans l'historique
    # si oui mettre
    sql ='''   '''
    mycursor.execute(sql, (article_id, client_id))
    historique_produit = mycursor.fetchall()
    sql ='''   '''
    mycursor.execute(sql, (client_id))
    historiques = mycursor.fetchall()


# @client_liste_envies.route('/client/envies/up', methods=['get'])
# @client_liste_envies.route('/client/envies/down', methods=['get'])
# @client_liste_envies.route('/client/envies/last', methods=['get'])
# @client_liste_envies.route('/client/envies/first', methods=['get'])
# def client_liste_envies_article_move():
#     mycursor = get_db().cursor()
#     id_client = session['id_user']
#     id_article = request.args.get('id_article')
#     action = request.path.split('/')[-1]
#
#     sql = '''SELECT * FROM liste_envie WHERE meuble_id = %s AND utilisateur_id = %s'''
#     mycursor.execute(sql, (id_article, id_client))
#     get_db().commit()
#     meuble_courant = mycursor.fetchone()
#
#     print(f"action={action}, meuble={meuble_courant}")
#     index_courant = meuble_courant['article_index']
#
#     # Les deux voisins et reload la page, et sort avec cet index
#     if action == 'down':
#         # On change le courant et celui d'au dessus
#         # Courant, on change
#         sql = '''UPDATE liste_envie
#                 SET article_index = article_index + 1
#               WHERE meuble_id = %s AND utilisateur_id = %s'''
#         mycursor.execute(sql, (id_article, id_client))
#         get_db().commit()
#         # Au dessus, on change
#         sql = '''UPDATE liste_envie
#         SET article_index = article_index - 1
#               WHERE article_index = %s
#               AND utilisateur_id = %s'''
#         mycursor.execute(sql, (index_courant, id_client))
#         get_db().commit()
#         pass
#
#     sql = '''SELECT *, m.id_meuble, m.nom_meuble FROM liste_envie
#              JOIN meuble m ON m.id_meuble = liste_envie.meuble_id
#              WHERE utilisateur_id = %s'''
#     mycursor.execute(sql, (id_client,))
#     get_db().commit()
#     articles_liste_envies = mycursor.fetchall()
#     fmsg = ''
#     for article in articles_liste_envies:
#         fmsg += f'nom={article["nom_meuble"]} index={article["article_index"]}, '
#     flash(fmsg, 'success')
#     return redirect('/client/envies/show')
@client_liste_envies.route('/client/envies/up', methods=['get'])
@client_liste_envies.route('/client/envies/down', methods=['get'])
@client_liste_envies.route('/client/envies/last', methods=['get'])
@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_article_move():

    db = get_db()
    cursor = db.cursor()

    id_client = session['id_user']
    id_article = request.args.get('id_article')
    # Dernier / dans l'url = l'action
    action = request.path.split('/')[-1]

    # article courant
    sql = '''SELECT article_index
        FROM liste_envie
        WHERE meuble_id = %s AND utilisateur_id = %s'''
    cursor.execute(sql, (id_article, id_client))
    meuble = cursor.fetchone()

    if not meuble:
        return redirect('/client/envies/show')

    index_courant = meuble['article_index']

    if action == 'up':
        sql = '''SELECT meuble_id, article_index
                FROM liste_envie
                WHERE utilisateur_id=%s AND article_index < %s
                ORDER BY article_index DESC
                LIMIT 1'''
        cursor.execute(sql, (id_client, index_courant))
        voisin = cursor.fetchone()

        # si voisin existent on change
        if voisin:
            sql = '''UPDATE liste_envie 
                   SET article_index=%s 
                   WHERE meuble_id=%s AND utilisateur_id=%s'''
            cursor.execute(sql,(voisin['article_index'], id_article, id_client))

            cursor.execute(
                '''UPDATE liste_envie 
                   SET article_index=%s 
                   WHERE meuble_id=%s AND utilisateur_id=%s''',
                (index_courant, voisin['meuble_id'], id_client)
            )

    elif action == 'down':
        sql = '''SELECT meuble_id, article_index
                FROM liste_envie
                WHERE utilisateur_id=%s AND article_index > %s
                ORDER BY article_index
                LIMIT 1'''

        cursor.execute(sql, (id_client, index_courant))
        voisin = cursor.fetchone()

        if voisin:
            cursor.execute(
                '''UPDATE liste_envie 
                   SET article_index=%s 
                   WHERE meuble_id=%s AND utilisateur_id=%s''',
                (voisin['article_index'], id_article, id_client)
            )

            cursor.execute(
                '''UPDATE liste_envie 
                   SET article_index=%s 
                   WHERE meuble_id=%s AND utilisateur_id=%s''',
                (index_courant, voisin['meuble_id'], id_client)
            )

    elif action == 'first':
        sql = '''UPDATE liste_envie
               SET article_index = article_index + 1
               WHERE utilisateur_id=%s AND article_index < %s'''
        cursor.execute(sql, (id_client, index_courant))

        sql = '''UPDATE liste_envie
               SET article_index = 1
               WHERE meuble_id=%s AND utilisateur_id=%s'''
        cursor.execute(sql, (id_article, id_client))

    elif action == 'last':
        sql = '''SELECT MAX(article_index) AS max_i
               FROM liste_envie
               WHERE utilisateur_id=%s'''
        cursor.execute(sql, (id_client,))

        max_index = cursor.fetchone()['max_i']
        sql = '''UPDATE liste_envie
               SET article_index = article_index - 1
               WHERE utilisateur_id=%s AND article_index > %s''',
        cursor.execute(sql, (id_client, index_courant))

        sql = '''UPDATE liste_envie
               SET article_index=%s
               WHERE meuble_id=%s AND utilisateur_id=%s'''
        cursor.execute(sql, (max_index, id_article, id_client))

    db.commit()

    return redirect('/client/envies/show')