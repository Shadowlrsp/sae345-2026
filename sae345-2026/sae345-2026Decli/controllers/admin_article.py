#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')

@admin_article.route('/admin/article/show', methods=['GET'])
def show_article():
    mycursor = get_db().cursor()
    
    sql = '''SELECT m.id_meuble AS id_article, 
                    m.nom_meuble AS nom, 
                    m.prix_meuble AS prix, 
                    m.photo AS image, 
                    t.libelle_type_meuble AS libelle,
                    t.id_type_meuble AS type_article_id,
                    COUNT(dm.id_declinaison_meuble) AS nb_declinaisons,
                    IFNULL(SUM(dm.stock), 0) AS stock_total,
                    MIN(dm.stock) AS stock_min,
                    
                    (SELECT COUNT(*) FROM ligne_commande lc 
                     JOIN declinaison_meuble dm2 ON lc.meuble_declinaison_id = dm2.id_declinaison_meuble 
                     WHERE dm2.meuble_id = m.id_meuble) AS nb_commandes,
                     
                    (SELECT COUNT(*) FROM commentaire c WHERE c.meuble_id = m.id_meuble AND c.valider = 1) AS nb_commentaires_nouveaux
             FROM meuble m
             JOIN type_meuble t ON m.type_meuble_id = t.id_type_meuble
             LEFT JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id AND dm.actif = 1
             WHERE m.actif = 1
             GROUP BY m.id_meuble, m.nom_meuble, m.prix_meuble, m.photo, t.libelle_type_meuble, t.id_type_meuble
             ORDER BY m.nom_meuble;
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('admin/article/show_article.html', articles=articles)

@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()
    sql = "SELECT id_type_meuble AS id_type_article, libelle_type_meuble AS libelle FROM type_meuble;"
    mycursor.execute(sql)
    types_article = mycursor.fetchall()
    return render_template('admin/article/add_article.html', types_article=types_article)

@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')
    
    stock_initial = request.form.get('stock', 1, type=int) 

    if image:
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        filename = None

    sql_meuble = '''INSERT INTO meuble (nom_meuble, photo, prix_meuble, type_meuble_id, fournisseur, materiau_id)
                    VALUES (%s, %s, %s, %s, %s, 1)'''
    mycursor.execute(sql_meuble, (nom, filename, prix, type_article_id, description))

    id_meuble = mycursor.lastrowid

    sql_declinaison = '''INSERT INTO declinaison_meuble (meuble_id, couleur_id, taille_id, stock, prix_declinaison)
                         VALUES (%s, 1, 1, %s, %s)'''
    mycursor.execute(sql_declinaison, (id_meuble, stock_initial, prix))

    get_db().commit()
    flash(f"Article '{nom}' créé avec un stock de {stock_initial}.", 'alert-success')
    return redirect('/admin/article/show')

@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    sql_verif_decli_actives = "SELECT COUNT(*) AS nb_actives FROM declinaison_meuble WHERE meuble_id = %s AND actif = 1"
    mycursor.execute(sql_verif_decli_actives, (id_article,))
    nb_actives = mycursor.fetchone()['nb_actives']

    if nb_actives > 0:
        flash(u'Suppression impossible : cet article possède encore des déclinaisons en vente. Supprimez-les d\'abord dans la page d\'édition.', 'alert-warning')
        return redirect('/admin/article/show')

    sql_verif_cmd = '''SELECT COUNT(*) AS nb_commandes 
                       FROM ligne_commande lc
                       JOIN declinaison_meuble dm ON lc.meuble_declinaison_id = dm.id_declinaison_meuble
                       WHERE dm.meuble_id = %s'''
    mycursor.execute(sql_verif_cmd, (id_article,))
    nb_commandes = mycursor.fetchone()['nb_commandes']

    if nb_commandes > 0:
        mycursor.execute("UPDATE meuble SET actif = 0 WHERE id_meuble = %s", (id_article,))
        
        mycursor.execute("DELETE FROM ligne_panier WHERE meuble_declinaison_id IN (SELECT id_declinaison_meuble FROM declinaison_meuble WHERE meuble_id = %s)", (id_article,))
        
        flash(u'Article archivé avec succès (Soft Delete). Il est retiré de la boutique mais conservé pour l\'historique des factures.', 'alert-info')

    else:
        mycursor.execute("DELETE FROM note WHERE meuble_id = %s", (id_article,))
        mycursor.execute("DELETE FROM commentaire WHERE meuble_id = %s", (id_article,))
        mycursor.execute("DELETE FROM ligne_panier WHERE meuble_declinaison_id IN (SELECT id_declinaison_meuble FROM declinaison_meuble WHERE meuble_id = %s)", (id_article,))
        
        mycursor.execute("DELETE FROM declinaison_meuble WHERE meuble_id = %s", (id_article,))
        
        mycursor.execute("SELECT photo FROM meuble WHERE id_meuble = %s", (id_article,))
        photo = mycursor.fetchone()['photo']
        if photo and os.path.exists(os.path.join('static/images/', photo)):
            os.remove(os.path.join('static/images/', photo))
            
        mycursor.execute("DELETE FROM meuble WHERE id_meuble = %s", (id_article,))
        
        flash(u'Article supprimé définitivement.', 'alert-success')

    get_db().commit()
    return redirect('/admin/article/show')

@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    
    sql_article = '''SELECT id_meuble AS id_article, nom_meuble AS nom, prix_meuble AS prix, 
                            photo AS image, type_meuble_id AS type_article_id, fournisseur AS description
                     FROM meuble WHERE id_meuble = %s'''
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    sql_types = "SELECT id_type_meuble AS id_type_article, libelle_type_meuble AS libelle FROM type_meuble;"
    mycursor.execute(sql_types)
    types_article = mycursor.fetchall()

    sql_declinaisons = '''
        SELECT dm.id_declinaison_meuble, dm.stock, dm.meuble_id AS article_id,
               t.libelle_taille, t.id_taille,
               c.libelle_couleur, c.id_couleur
        FROM declinaison_meuble dm
        JOIN taille t ON dm.taille_id = t.id_taille
        JOIN couleur c ON dm.couleur_id = c.id_couleur
        WHERE dm.meuble_id = %s AND dm.actif = 1
    '''
    mycursor.execute(sql_declinaisons, (id_article,))
    declinaisons_article = mycursor.fetchall()

    pb_taille_uniq = 0
    pb_couleur_uniq = 0
    if len(declinaisons_article) > 1:
        for d in declinaisons_article:
            if d['id_taille'] == 1: pb_taille_uniq = 1
            if d['id_couleur'] == 1: pb_couleur_uniq = 1

    return render_template('admin/article/edit_article.html',
                           article=article, 
                           types_article=types_article, 
                           declinaisons_article=declinaisons_article,
                           pb_taille_uniq=pb_taille_uniq,
                           pb_couleur_uniq=pb_couleur_uniq)

@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')

    sql = "SELECT photo AS image FROM meuble WHERE id_meuble = %s"
    mycursor.execute(sql, (id_article,))
    image_nom = mycursor.fetchone()['image']

    if image:
        if image_nom and os.path.exists(os.path.join('static/images/', image_nom)):
            os.remove(os.path.join('static/images/', image_nom))
        
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename

    sql = '''UPDATE meuble SET nom_meuble=%s, photo=%s, prix_meuble=%s, 
                    type_meuble_id=%s, fournisseur=%s 
             WHERE id_meuble=%s'''
    mycursor.execute(sql, (nom, image_nom, prix, type_article_id, description, id_article))
    
    get_db().commit()
    message = u'Article modifié, nom:' + nom + ' - type_article :' + type_article_id + ' - prix:' + prix
    flash(message, 'alert-success')
    
    return redirect('/admin/article/show')