#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                           template_folder='templates')


@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get', 'post'])
def admin_commande_show():
    mycursor = get_db().cursor()

    # On utilise 'login', 'date_achat' et 'libelle' sans alias pour coller à ton HTML
    sql = '''
        SELECT c.id_commande,
               u.login,
               c.date_achat,
               e.libelle,
               COUNT(lc.meuble_id) AS nbr_articles,
               SUM(lc.prix * lc.quantite) AS prix_total,
               c.etat_id
        FROM commande c
        JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
        JOIN etat e ON c.etat_id = e.id_etat
        LEFT JOIN ligne_commande lc ON c.id_commande = lc.commande_id
        GROUP BY c.id_commande, u.login, c.date_achat, e.libelle, c.etat_id
        ORDER BY c.etat_id, c.date_achat DESC;
    '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)

    if id_commande != None:
        sql_articles = '''
            SELECT lc.meuble_id,
                   m.nom_meuble AS nom,
                   lc.quantite,
                   lc.prix,
                   (lc.prix * lc.quantite) AS total_ligne
            FROM ligne_commande lc
            JOIN meuble m ON lc.meuble_id = m.id_meuble
            WHERE lc.commande_id = %s;
        '''
        mycursor.execute(sql_articles, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql_client = '''
            SELECT u.login, u.nom, u.email
            FROM commande c
            JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
            WHERE c.id_commande = %s;
        '''
        mycursor.execute(sql_client, (id_commande,))
        commande_adresses = mycursor.fetchone()

    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get', 'post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        sql = ''' UPDATE commande SET etat_id = 2 WHERE id_commande = %s; '''
        mycursor.execute(sql, (commande_id,))
        get_db().commit()
        flash(u'Commande validée', 'alert-success')

    return redirect('/admin/commande/show')