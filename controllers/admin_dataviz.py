#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    # wishlist par categorie
    sql = '''
          SELECT type_meuble.id_type_meuble      AS id_type_article,
                 type_meuble.libelle_type_meuble AS libelle,
                 COUNT(liste_envie.meuble_id)    AS nbr_articles
          FROM type_meuble
                   LEFT JOIN meuble ON meuble.type_meuble_id = type_meuble.id_type_meuble
                   LEFT JOIN liste_envie ON liste_envie.meuble_id = meuble.id_meuble
          GROUP BY type_meuble.id_type_meuble, type_meuble.libelle_type_meuble
          ORDER BY type_meuble.id_type_meuble
          '''
    mycursor.execute(sql)
    get_db().commit()
    types_articles_nb = mycursor.fetchall()
    print(types_articles_nb)

    labels = [ligne['libelle'] for ligne in types_articles_nb]
    values = [ligne['nbr_articles'] for ligne in types_articles_nb]
    print("LABELS WISHLIST")
    print(labels)

    sql = '''
          SELECT type_meuble.id_type_meuble,
                 type_meuble.libelle_type_meuble            AS libelle,
                 COALESCE(SUM(historique.consultations), 0) AS nbr_consultations
          FROM type_meuble
                   LEFT JOIN meuble ON meuble.type_meuble_id = type_meuble.id_type_meuble
                   LEFT JOIN historique ON historique.id_meuble = meuble.id_meuble
              AND MONTH (historique.date_update) = MONTH (NOW())
              AND YEAR (historique.date_update) = YEAR (NOW())
          GROUP BY type_meuble.id_type_meuble, type_meuble.libelle_type_meuble
          ORDER BY type_meuble.id_type_meuble
          '''
    mycursor.execute(sql)
    get_db().commit()
    histo_par_categorie = mycursor.fetchall()
    print(histo_par_categorie)

    histo_values = [int(ligne['nbr_consultations']) for ligne in histo_par_categorie]
    print("HISTO VALUES")
    print(histo_values)

    sql = "SELECT id_type_meuble, libelle_type_meuble FROM type_meuble ORDER BY id_type_meuble"
    mycursor.execute(sql)
    get_db().commit()
    toutes_categories = mycursor.fetchall()
    print(toutes_categories)

    selected_cat = request.args.get('categorie', None)
    detail_articles = []
    detail_labels = []
    detail_wishlist = []
    detail_histo = []

    if selected_cat:
        sql = '''
              SELECT meuble.id_meuble,
                     meuble.nom_meuble,
                     COUNT(DISTINCT liste_envie.utilisateur_id) AS nbr_wishlist,
                      COALESCE(SUM(historique.consultations), 0) AS nbr_historique
              FROM meuble
                       LEFT JOIN liste_envie ON liste_envie.meuble_id = meuble.id_meuble
                       LEFT JOIN historique ON historique.id_meuble = meuble.id_meuble
              WHERE meuble.type_meuble_id = %s
              GROUP BY meuble.id_meuble, meuble.nom_meuble
              ORDER BY meuble.nom_meuble
              '''
        mycursor.execute(sql, (selected_cat,))
        get_db().commit()
        detail_articles = mycursor.fetchall()
        print("DETAIL ARTICLES")
        print(detail_articles)

        detail_labels = [art['nom_meuble'] for art in detail_articles]
        # int obligatoire pcq sinon ca fait un Decimal
        detail_wishlist = [int(art['nbr_wishlist']) for art in detail_articles]
        detail_histo    = [int(art['nbr_historique']) for art in detail_articles]

    return render_template(
        'admin/dataviz/dataviz_etat_1.html',
        types_articles_nb=types_articles_nb,
        labels=labels,
        values=values,
        histo_values=histo_values,
        toutes_categories=toutes_categories,
        selected_cat=selected_cat,
        detail_articles=detail_articles,
        detail_labels=detail_labels,
        detail_wishlist=detail_wishlist,
        detail_histo=detail_histo,
    )


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    # mycursor = get_db().cursor()
    # sql = '''    '''
    # mycursor.execute(sql)
    # adresses = mycursor.fetchall()

    #exemples de tableau "résultat" de la requête
    adresses =  [{'dep': '25', 'nombre': 1}, {'dep': '83', 'nombre': 1}, {'dep': '90', 'nombre': 3}]

    # recherche de la valeur maxi "nombre" dans les départements
    # maxAddress = 0
    # for element in adresses:
    #     if element['nbr_dept'] > maxAddress:
    #         maxAddress = element['nbr_dept']
    # calcul d'un coefficient de 0 à 1 pour chaque département
    # if maxAddress != 0:
    #     for element in adresses:
    #         indice = element['nbr_dept'] / maxAddress
    #         element['indice'] = round(indice,2)

    print(adresses)

    return render_template('admin/dataviz/dataviz_etat_map.html'
                           , adresses=adresses
                          )


