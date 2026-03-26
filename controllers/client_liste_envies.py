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



    sql = "SELECT COUNT(*) FROM historique WHERE id_utilisateur = %s"
    mycursor.execute(sql, (id_client,))
    nb_historique = mycursor.fetchone()

    print("NB LISTE ENVIE")
    print(nb_liste_envies['COUNT(*)'])
    get_db().commit()

    sql = '''SELECT *, photo as image, nom_meuble as nom, meuble.prix_meuble as prix FROM historique 
             JOIN meuble ON meuble.id_meuble = historique.id_meuble
             # JOIN utilisateur on historique.id_utilisateur = utilisateur.id_utilisateur
        
             WHERE historique.id_utilisateur = %s
          ORDER BY historique.date_update DESC'''
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()
    print(articles_historique)

    # focus start
    focus_nb_type = None
    focus_other_ppl = None
    print('FOCUS\nFOCUS\nFOCUS\nFOCUS\n')
    id_focus = request.args.get('id_article_detail_wishlist')
    if id_focus:
        # ===== VERT, nombre de personnes autre que nous ayant ajoute l'article en wishlist

        # focus = article depuis le sql
        sql = '''SELECT COUNT(*) - 1 as nbrUtils, meuble.nom_meuble FROM utilisateur
            JOIN liste_envie ON liste_envie.utilisateur_id = utilisateur.id_utilisateur
            JOIN meuble ON id_meuble = liste_envie.meuble_id
            WHERE id_meuble = %s
            GROUP BY meuble_id, nom_meuble
            HAVING COUNT(*) > 1
        '''
        mycursor.execute(sql, id_focus)
        focus_other_ppl = mycursor.fetchone()
        print(f'FOCUS ID {id_focus}')
        print(focus_other_ppl)

        # ===== BLEU, nombre d'articles du meme type hors du courrant dans la wishlist
        sql = '''SELECT type_meuble_id FROM meuble WHERE id_meuble = %s'''
        mycursor.execute(sql, id_focus)
        type_focus = mycursor.fetchone()
        print(type_focus)
        id_type_focus = type_focus['type_meuble_id']

        sql = '''SELECT (COUNT(*)-1) as nbrArticles, type_meuble_id, type_meuble.libelle_type_meuble FROM liste_envie
                JOIN meuble ON meuble_id = meuble.id_meuble
                JOIN type_meuble ON meuble.type_meuble_id = type_meuble.id_type_meuble
                WHERE utilisateur_id = %s AND type_meuble_id = %s
            GROUP BY type_meuble_id, libelle_type_meuble
            HAVING COUNT(*) > 0'''
        mycursor.execute(sql, (id_client, id_type_focus))
        focus_nb_type = mycursor.fetchone()
        print(focus_nb_type)


    return render_template('client/liste_envies/liste_envies_show.html'
                           ,articles_liste_envies=articles_liste_envies
                           , articles_historique=articles_historique
                           , focus_other_ppl=focus_other_ppl
                           , focus_nb_type=focus_nb_type
                           , nb_liste_envies=nb_liste_envies['COUNT(*)']
                           , nb_liste_historique=nb_historique['COUNT(*)']
                           )



def client_historique_add(article_id, client_id):
    # rechercher si l'article pour cet utilisateur est dans l'historique
    # si oui mettre
    mycursor = get_db().cursor()

    # debug all historique
    sql = '''SELECT * FROM historique WHERE id_utilisateur = %s'''
    mycursor.execute(sql, (client_id,))
    get_db().commit()
    result = mycursor.fetchall()
    print(result)
    print("Total historique: " + str(len(result)))

    sql ='''SELECT COUNT(*) FROM historique WHERE id_meuble = %s AND id_utilisateur = %s'''
    mycursor.execute(sql, (article_id, client_id))
    get_db().commit()

    historique_produit = mycursor.fetchone()
    print(f'HISTORIQUE PRODUIT, id_utilisateur={client_id}, id_meuble={article_id}')
    print(historique_produit)
    dans_historique = historique_produit['COUNT(*)']

    # Enleve si plus d'1 mois
    sql = '''DELETE FROM historique
            WHERE date_update < NOW() - INTERVAL 1 MONTH;'''
    mycursor.execute(sql)
    get_db().commit()

    # Check si c'est au dessus de 6
    # Enleve le plus ancien si y'en a plus de six
    # On delete toutes les entrees pas trouvees dans la sous-querry qui est limite par 5 (6 laissait un 7eme article etre ajoute a l'historique)
    # Ca supprime donc effectivement tout sauf les six derniers elements
    # https://www.mariadbtutorial.com/mariadb-basics/mariadb-subqueries/
    sql = """DELETE FROM historique
            WHERE id_utilisateur = %s
            AND (id_utilisateur, id_meuble, date_update) NOT IN (
                SELECT id_utilisateur, id_meuble, date_update
                FROM (
                    SELECT id_utilisateur, id_meuble, date_update
                    FROM historique
                    WHERE id_utilisateur = %s
                    ORDER BY date_update DESC
                    LIMIT 5
                ) AS t
            );"""
    mycursor.execute(sql, (client_id, client_id))
    get_db().commit()

    if int(dans_historique) > 0:
        sql = '''UPDATE historique SET consultations = consultations + 1 WHERE id_utilisateur = %s AND id_meuble = %s'''
        mycursor.execute(sql, (client_id, article_id))
        get_db().commit()
        return

    print("PAS DANS HISTORIQUE, ADD")
    sql ='''INSERT INTO historique (id_utilisateur, id_meuble, date_update) VALUES (%s, %s, NOW())'''
    mycursor.execute(sql, (client_id, article_id))
    get_db().commit()
    # historiques = mycursor.fetchall()


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