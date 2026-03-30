#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, request
from connexion_db import get_db

admin_dataviz_commentaire = Blueprint(
    'admin_dataviz_commentaire',
    __name__,
    template_folder='templates'
)

@admin_dataviz_commentaire.route('/admin/dataviz/commentaires')
def dataviz_commentaires():
    mycursor = get_db().cursor()
    mycursor.execute("SELECT id_type_meuble, libelle_type_meuble FROM type_meuble")
    types_meubles = mycursor.fetchall()

    type_id = request.args.get('type_meuble_id')
    datas = []
    labels = []
    values_notes = []
    values_commentaires = []
    values_moyennes = []

    if type_id:
        sql = '''
              SELECT m.nom_meuble,
                     COUNT(DISTINCT n.utilisateur_id) AS nb_notes,
                     ROUND(AVG(n.note), 2) AS moyenne_note,
                     COUNT(DISTINCT \
                           CONCAT(c.utilisateur_id, '-', c.meuble_id, '-', c.date_publication)) AS nb_commentaires
              FROM meuble m
                       LEFT JOIN note n ON n.meuble_id = m.id_meuble
                       LEFT JOIN commentaire c ON c.meuble_id = m.id_meuble
                       LEFT JOIN utilisateur u ON u.id_utilisateur = c.utilisateur_id
              WHERE m.type_meuble_id = %s
                AND (u.role IS NULL OR u.role = 'ROLE_client')
              GROUP BY m.id_meuble, m.nom_meuble
              '''
        mycursor.execute(sql, (type_id,))
        datas = mycursor.fetchall()

        # utilisatiob dans chart js
        labels = [row['nom_meuble'] for row in datas]
        values_notes = [row['nb_notes'] for row in datas]
        values_commentaires = [row['nb_commentaires'] for row in datas]
        values_moyennes = [float(row['moyenne_note']) if row['moyenne_note'] else 0 for row in datas]

    return render_template(
        'admin/dataviz/dataviz_commentaires.html',
        datas=datas,
        labels=labels,
        values_notes=values_notes,
        values_commentaires=values_commentaires,
        values_moyennes=values_moyennes,
        types_meubles=types_meubles
    )