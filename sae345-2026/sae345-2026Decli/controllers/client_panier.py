#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, redirect, flash, session, render_template
from datetime import datetime
from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__, template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = int(request.form.get('quantite', 1))

    sql = "SELECT stock FROM declinaison_meuble WHERE id_declinaison_meuble = %s"
    mycursor.execute(sql, (id_article,))
    declinaison = mycursor.fetchone()

    if declinaison is None or declinaison['stock'] < quantite:
        flash("Stock insuffisant pour cette déclinaison", "alert-warning")
        return redirect('/client/article/show')

    sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne_existante = mycursor.fetchone()

    if ligne_existante:
        sql = "UPDATE ligne_panier SET quantite = quantite + %s WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
        mycursor.execute(sql, (quantite, id_client, id_article))
    else:
        sql = "INSERT INTO ligne_panier (utilisateur_id, meuble_declinaison_id, quantite, date_ajout) VALUES (%s, %s, %s, %s)"
        mycursor.execute(sql, (id_client, id_article, quantite, datetime.now()))

    sql = "UPDATE declinaison_meuble SET stock = stock - %s WHERE id_declinaison_meuble = %s"
    mycursor.execute(sql, (quantite, id_article))

    get_db().commit()
    flash("Quantité modifié +", "alert-info")
    return redirect('/client/article/show')

@client_panier.route('/client/panier/declinaison')
def client_article_declinaison():
    mycursor = get_db().cursor()
    
    id_article = request.args.get('id_article', type=int)

    if not id_article:
        abort(400, "Erreur : L'identifiant de l'article est manquant.")

    sql_article = '''
        SELECT id_meuble AS id_article, 
               nom_meuble AS nom, 
               prix_meuble AS prix, 
               photo AS image, 
               description 
        FROM meuble
        WHERE id_meuble = %s
    '''
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    if not article:
        flash("L'article demandé n'existe pas.", "alert-warning")
        return redirect('/client/article/show')

    sql_declinaisons = '''
        SELECT dm.id_declinaison_meuble AS id_declinaison_article,
               dm.stock,
               dm.prix_declinaison AS prix,
               c.id_couleur,
               c.libelle_couleur,
               c.code_couleur,
               t.id_taille,
               t.libelle_taille
        FROM declinaison_meuble dm
        LEFT JOIN couleur c ON dm.couleur_id = c.id_couleur
        LEFT JOIN taille t ON dm.taille_id = t.id_taille
        WHERE dm.meuble_id = %s
        ORDER BY c.libelle_couleur, t.libelle_taille
    '''
    mycursor.execute(sql_declinaisons, (id_article,))
    declinaisons = mycursor.fetchall()

    return render_template('client/boutique/declinaison_article.html', 
                           article=article, 
                           declinaisons=declinaisons)

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne:
        if ligne['quantite'] > 1:
            sql = "UPDATE ligne_panier SET quantite = quantite - 1 WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
            mycursor.execute(sql, (id_client, id_article))
        else:
            sql = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
            mycursor.execute(sql, (id_client, id_article))

        sql_stock = "UPDATE declinaison_meuble SET stock = stock + 1 WHERE id_declinaison_meuble = %s"
        mycursor.execute(sql_stock, (id_article,))

        get_db().commit()
        flash("Quantité modifiée -", "alert-info")

    return redirect('/client/article/show')

@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')

    sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
    mycursor.execute(sql, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne:
        sql_stock = "UPDATE declinaison_meuble SET stock = stock + %s WHERE id_declinaison_meuble = %s"
        mycursor.execute(sql_stock, (ligne['quantite'], id_article))

        sql_delete = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND meuble_declinaison_id = %s"
        mycursor.execute(sql_delete, (id_client, id_article))

        get_db().commit()
        flash("Ligne supprimée", "alert-info")

    return redirect('/client/article/show')

@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = "SELECT meuble_declinaison_id, quantite FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    items = mycursor.fetchall()

    for item in items:
        sql_stock = "UPDATE declinaison_meuble SET stock = stock + %s WHERE id_declinaison_meuble = %s"
        mycursor.execute(sql_stock, (item['quantite'], item['meuble_declinaison_id']))

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