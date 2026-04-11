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
    
    sql_type = '''
        SELECT t.id_type_meuble, 
               t.libelle_type_meuble AS libelle, 
               COUNT(DISTINCT m.id_meuble) AS nbr_meubles,
               COUNT(dm.id_declinaison_meuble) AS nbr_declinaisons
        FROM type_meuble t
        LEFT JOIN meuble m ON t.id_type_meuble = m.type_meuble_id AND m.actif = 1
        LEFT JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id AND dm.actif = 1
        GROUP BY t.id_type_meuble, t.libelle_type_meuble
    '''
    mycursor.execute(sql_type)
    datas_show = mycursor.fetchall()
    
    labels = [str(row['libelle']) for row in datas_show]
    values_meubles = [int(row['nbr_meubles']) for row in datas_show]
    values_declinaisons = [int(row['nbr_declinaisons']) for row in datas_show]

    sql_decli_details = '''
        SELECT 
            CONCAT(m.nom_meuble, ' (', IFNULL(c.libelle_couleur, 'Std'), ' / ', IFNULL(t.libelle_taille, 'Std'), ')') AS nom_decli,
            dm.stock AS qte_stock,
            (dm.stock * dm.prix_declinaison) AS cout_stock
        FROM declinaison_meuble dm
        JOIN meuble m ON dm.meuble_id = m.id_meuble
        LEFT JOIN couleur c ON dm.couleur_id = c.id_couleur
        LEFT JOIN taille t ON dm.taille_id = t.id_taille
        WHERE dm.actif = 1 AND dm.stock > 0
        ORDER BY cout_stock DESC
    '''
    mycursor.execute(sql_decli_details)
    datas_decli = mycursor.fetchall()
    
    labels_decli = [str(row['nom_decli']) for row in datas_decli]
    qtes_decli = [int(row['qte_stock']) for row in datas_decli]
    couts_decli = [float(row['cout_stock']) for row in datas_decli]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , types_articles_nb=datas_show
                           , labels=labels
                           , values_meubles=values_meubles
                           , values_declinaisons=values_declinaisons
                           , labels_decli=labels_decli
                           , qtes_decli=qtes_decli
                           , couts_decli=couts_decli)

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


