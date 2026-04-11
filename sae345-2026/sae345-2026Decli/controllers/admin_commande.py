#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session
from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                           template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')

@admin_commande.route('/admin/commande/show', methods=['GET'])
def admin_commande_show():
    mycursor = get_db().cursor()
    
    sql = '''
        SELECT c.id_commande,
               u.login,
               c.date_achat,
               e.libelle,
               IFNULL(SUM(lc.quantite), 0) AS nbr_articles,
               IFNULL(SUM(lc.prix * lc.quantite), 0) AS prix_total,
               c.etat_id
        FROM commande c
        JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
        JOIN etat e ON c.etat_id = e.id_etat
        LEFT JOIN ligne_commande lc ON c.id_commande = lc.commande_id
        GROUP BY c.id_commande, u.login, c.date_achat, e.libelle, c.etat_id
        ORDER BY c.etat_id ASC, c.date_achat DESC;
    '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    articles_commande = None
    id_commande = request.args.get('id_commande', None)
    
    if id_commande:
        sql_articles = '''
            SELECT lc.meuble_declinaison_id,
                   m.nom_meuble AS nom,
                   lc.quantite,
                   lc.prix,
                   (lc.prix * lc.quantite) AS prix_ligne,
                   co.id_couleur,
                   co.libelle_couleur,
                   ta.id_taille,
                   ta.libelle_taille,
                   cmd.etat_id,
                   cmd.id_commande
            FROM ligne_commande lc
            JOIN commande cmd ON lc.commande_id = cmd.id_commande
            JOIN declinaison_meuble dm ON lc.meuble_declinaison_id = dm.id_declinaison_meuble
            JOIN meuble m ON dm.meuble_id = m.id_meuble
            LEFT JOIN couleur co ON dm.couleur_id = co.id_couleur
            LEFT JOIN taille ta ON dm.taille_id = ta.id_taille
            WHERE lc.commande_id = %s;
        '''
        mycursor.execute(sql_articles, (id_commande))
        articles_commande = mycursor.fetchall()

    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           )

@admin_commande.route('/admin/commande/valider', methods=['POST'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    
    if commande_id:
        sql = ''' UPDATE commande SET etat_id = 3 WHERE id_commande = %s; '''
        mycursor.execute(sql, (commande_id))
        get_db().commit()
        flash(u'Commande validée et expédiée avec succès', 'alert-success')

    return redirect('/admin/commande/show')