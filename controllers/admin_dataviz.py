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
    sql = '''
        SELECT
            LEFT(a.code_postal, 2) AS dep,
            COUNT(DISTINCT c.id_commande) AS nb_commandes,
            SUM(lc.prix * lc.quantite) AS chiffre_affaire
        FROM commande c
        JOIN adresse a ON c.adresse_livraison_id = a.id_adresse
        JOIN ligne_commande lc ON lc.commande_id = c.id_commande
        GROUP BY dep
        ORDER BY dep;
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()

    labels = [str(row['dep']) for row in datas_show]
    values = [int(row['nb_commandes']) for row in datas_show]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , datas_show=datas_show
                           , labels=labels
                           , values=values)


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()
    sql = '''
        SELECT
            LEFT(a.code_postal, 2) AS dep,
            COUNT(DISTINCT c.id_commande) AS nombre
        FROM commande c
        JOIN adresse a ON c.adresse_livraison_id = a.id_adresse
        WHERE c.adresse_livraison_id IS NOT NULL
        GROUP BY dep;
    '''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()

    max_value = 0
    for element in adresses:
        if element['nombre'] > max_value:
            max_value = element['nombre']

    if max_value != 0:
        for element in adresses:
            indice = element['nombre'] / max_value
            element['indice'] = round(indice, 2)

    return render_template('admin/dataviz/dataviz_etat_map.html'
                           , adresses=adresses)

