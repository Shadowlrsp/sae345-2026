#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, redirect, flash, session
from datetime import datetime
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__, template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = int(request.form.get('quantite', 1))

    # Vérifier le stock disponible
    sql = "SELECT stock FROM meuble WHERE id_meuble = %s"
    mycursor.execute(sql, (id_article,))
    meuble = mycursor.fetchone()

    if meuble is None:
        flash("Meuble introuvable", "alert-danger")
        return redirect('/client/article/show')

    if meuble['stock'] < quantite:
        flash("Stock insuffisant", "alert-warning")
        return redirect('/client/article/show')

    # Vérifier si l'article est déjà dans le panier
    sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne_existante = mycursor.fetchone()

    if ligne_existante:
        sql = "UPDATE ligne_panier SET quantite = quantite + %s WHERE utilisateur_id = %s AND meuble_id = %s"
        mycursor.execute(sql, (quantite, id_client, id_article))
    else:
        sql = "INSERT INTO ligne_panier (utilisateur_id, meuble_id, quantite, date_ajout) VALUES (%s, %s, %s, %s)"
        mycursor.execute(sql, (id_client, id_article, quantite, datetime.now()))

    # Mise à jour du stock
    sql = "UPDATE meuble SET stock = stock - %s WHERE id_meuble = %s"
    mycursor.execute(sql, (quantite, id_article))

    get_db().commit()
    flash("Meuble ajouté au panier", "alert-success")
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne:
        if ligne['quantite'] > 1:
            sql = "UPDATE ligne_panier SET quantite = quantite - 1 WHERE utilisateur_id = %s AND meuble_id = %s"
        else:
            sql = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"

        mycursor.execute(sql, (id_client, id_article))

        # Remettre 1 unité en stock
        sql_stock = "UPDATE meuble SET stock = stock + 1 WHERE id_meuble = %s"
        mycursor.execute(sql_stock, (id_article,))

        get_db().commit()
        flash("Article retiré du panier", "alert-info")

    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne:
        # On rend tout le stock avant de supprimer la ligne
        sql_stock = "UPDATE meuble SET stock = stock + %s WHERE id_meuble = %s"
        mycursor.execute(sql_stock, (ligne['quantite'], id_article))

        sql_delete = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
        mycursor.execute(sql_delete, (id_client, id_article))

        get_db().commit()
        flash("Ligne supprimée", "alert-info")

    return redirect('/client/article/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupérer tout le panier pour rendre le stock
    sql = "SELECT meuble_id, quantite FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    items = mycursor.fetchall()

    for item in items:
        sql_stock = "UPDATE meuble SET stock = stock + %s WHERE id_meuble = %s"
        mycursor.execute(sql_stock, (item['quantite'], item['meuble_id']))

    sql_delete = "DELETE FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql_delete, (id_client,))

    get_db().commit()
    flash("Panier vidé", "alert-info")
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    session['filter_word'] = request.form.get('filter_word', None)
    session['filter_prix_min'] = request.form.get('filter_prix_min', None)
    session['filter_prix_max'] = request.form.get('filter_prix_max', None)
    session['filter_types'] = request.form.getlist('filter_types')
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    return redirect('/client/article/show')