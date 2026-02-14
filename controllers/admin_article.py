#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
# from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    # admin_article_1 : Liste des meubles avec leur type et stock
    sql = '''SELECT m.id_meuble AS id_article, m.nom_meuble AS nom, m.prix_meuble AS prix, 
                    m.stock, m.photo AS image, t.libelle_type_meuble AS libelle
             FROM meuble m
             JOIN type_meuble t ON m.type_meuble_id = t.id_type_meuble
             ORDER BY m.nom_meuble;
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('admin/article/show_article.html', articles=articles)


@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()
    # Récupération des types pour le menu déroulant du formulaire
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
    stock = request.form.get('stock', 0)
    description = request.form.get('description', '')  # Correspond à fournisseur ou marque dans ton SQL
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        filename = None

    # admin_article_2 : Ajout d'un meuble (on utilise materiau_id=1 par défaut si non fourni)
    sql = '''INSERT INTO meuble (nom_meuble, photo, prix_meuble, type_meuble_id, fournisseur, stock, materiau_id)
             VALUES (%s, %s, %s, %s, %s, %s, 1)'''

    tuple_add = (nom, filename, prix, type_article_id, description, stock)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    flash(u'Article ajouté', 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    # admin_article_3 : Vérifier si l'article est dans des commandes (remplace déclinaisons)
    sql = "SELECT COUNT(*) AS nb_commandes FROM ligne_commande WHERE meuble_id = %s"
    mycursor.execute(sql, id_article)
    nb_commandes = mycursor.fetchone()

    if nb_commandes['nb_commandes'] > 0:
        flash(u'Impossible de supprimer : cet article est présent dans des commandes', 'alert-warning')
    else:
        # admin_article_4 : Récupérer le nom de l'image avant suppression
        sql = "SELECT photo AS image FROM meuble WHERE id_meuble = %s"
        mycursor.execute(sql, id_article)
        article = mycursor.fetchone()
        image = article['image']

        # admin_article_5 : Suppression
        sql = "DELETE FROM meuble WHERE id_meuble = %s"
        mycursor.execute(sql, id_article)
        get_db().commit()

        if image and os.path.exists(os.path.join('static/images/', image)):
            os.remove('static/images/' + image)

        flash(u'Article supprimé', 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    # admin_article_6 : Récupérer l'article
    sql = '''SELECT id_meuble AS id_article, nom_meuble AS nom, prix_meuble AS prix, 
                    stock, photo AS image, type_meuble_id AS type_article_id, fournisseur AS description
             FROM meuble WHERE id_meuble = %s'''
    mycursor.execute(sql, id_article)
    article = mycursor.fetchone()

    # admin_article_7 : Liste des types
    sql = "SELECT id_type_meuble AS id_type_article, libelle_type_meuble AS libelle FROM type_meuble;"
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html', article=article, types_article=types_article)


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    stock = request.form.get('stock', 0)
    description = request.form.get('description')

    # admin_article_8 : Récupérer l'ancienne image
    sql = "SELECT photo AS image FROM meuble WHERE id_meuble = %s"
    mycursor.execute(sql, id_article)
    image_nom = mycursor.fetchone()['image']

    if image:
        if image_nom and os.path.exists(os.path.join('static/images/', image_nom)):
            os.remove(os.path.join('static/images/', image_nom))

        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename

    # admin_article_9 : Update avec le stock
    sql = '''UPDATE meuble SET nom_meuble=%s, photo=%s, prix_meuble=%s, 
                    type_meuble_id=%s, fournisseur=%s, stock=%s 
             WHERE id_meuble=%s'''
    mycursor.execute(sql, (nom, image_nom, prix, type_article_id, description, stock, id_article))
    get_db().commit()

    flash(u'Article modifié', 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article = []
    commentaires = {}
    return render_template('admin/article/show_avis.html', article=article, commentaires=commentaires)


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    return admin_avis(article_id)