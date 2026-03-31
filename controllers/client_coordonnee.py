#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__,
                              template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql_utilisateur = "SELECT * FROM utilisateur WHERE id_utilisateur = %s"
    mycursor.execute(sql_utilisateur, (id_client,))
    utilisateur = mycursor.fetchone()

    sql_adresses = '''
                   SELECT a.id_adresse,
                          a.nom,
                          a.rue,
                          a.code_postal,
                          a.ville,
                          a.valide,
                          a.est_favorite,
                          COUNT(DISTINCT c.id_commande) AS nb_commandes
                   FROM adresse a
                            LEFT JOIN commande c ON c.adresse_livraison_id = a.id_adresse OR
                                                    c.adresse_facturation_id = a.id_adresse
                   WHERE a.utilisateur_id = %s
                   GROUP BY a.id_adresse,
                            a.nom,
                            a.rue,
                            a.code_postal,
                            a.ville,
                            a.valide,
                            a.est_favorite
                   ORDER BY a.est_favorite DESC, a.valide DESC, a.id_adresse DESC \
                   '''

    mycursor.execute(sql_adresses, (id_client,))
    adresses = mycursor.fetchall()

    nb_adresses = len(adresses)
    nb_adresses_valides = sum(1 for ad in adresses if ad['valide'] == 1)

    return render_template('client/coordonnee/show_coordonnee.html'
                           , utilisateur=utilisateur
                           , adresses=adresses
                           , nb_adresses=nb_adresses
                           , nb_adresses_valides=nb_adresses_valides
                           )


@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_utilisateur_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    mycursor.execute("SELECT id_utilisateur, nom, login, email FROM utilisateur WHERE id_utilisateur = %s", (id_client,))
    utilisateur = mycursor.fetchone()
    return render_template('client/coordonnee/edit_coordonnee.html', utilisateur=utilisateur)

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_utilisateur_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    mycursor.execute("SELECT * FROM utilisateur WHERE (login = %s OR email = %s) AND id_utilisateur != %s", (login, email, id_client))
    if mycursor.fetchone():
        flash(u'Erreur : Login ou email déjà utilisé.', 'alert-warning')
        return redirect('/client/coordonnee/edit')

    mycursor.execute("UPDATE utilisateur SET nom = %s, login = %s, email = %s WHERE id_utilisateur = %s", (nom, login, email, id_client))
    get_db().commit()

    session['login'] = login
    flash(u'Profil mis à jour', 'alert-success')
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')

    mycursor.execute("SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s", (id_adresse, id_client))
    adresse = mycursor.fetchone()

    if not adresse:
        flash(u'Problème : Vous ne pouvez pas supprimer cette adresse.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM commande WHERE adresse_livraison_id = %s OR adresse_facturation_id = %s",
        (id_adresse, id_adresse))
    utilisee = mycursor.fetchone()['nb'] > 0

    if utilisee:
        mycursor.execute("UPDATE adresse SET valide = 0, est_favorite = 0 WHERE id_adresse = %s", (id_adresse,))
    else:
        mycursor.execute("DELETE FROM adresse WHERE id_adresse = %s", (id_adresse,))

    if adresse['est_favorite'] == 1:
        mycursor.execute("""
                         SELECT a.id_adresse
                         FROM adresse a
                                  LEFT JOIN commande c ON c.adresse_livraison_id = a.id_adresse OR
                                                          c.adresse_facturation_id = a.id_adresse
                         WHERE a.utilisateur_id = %s
                           AND a.valide = 1
                         ORDER BY c.date_achat DESC, a.id_adresse DESC LIMIT 1
                         """, (id_client,))
        nouvelle_favorite = mycursor.fetchone()

        if nouvelle_favorite:
            mycursor.execute("UPDATE adresse SET est_favorite = 1 WHERE id_adresse = %s",
                             (nouvelle_favorite['id_adresse'],))

    get_db().commit()
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    mycursor.execute("SELECT * FROM utilisateur WHERE id_utilisateur = %s", (id_client,))
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html', utilisateur=utilisateur)


@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    if len(code_postal) != 5 or not code_postal.isdigit():
        flash(u'Le code postal doit contenir 5 chiffres.', 'alert-warning')
        mycursor.execute("SELECT * FROM utilisateur WHERE id_utilisateur = %s", (id_client,))
        utilisateur = mycursor.fetchone()
        return render_template('client/coordonnee/add_adresse.html', utilisateur=utilisateur, nom=nom, rue=rue,
                               code_postal=code_postal, ville=ville)

    mycursor.execute("SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id = %s AND valide = 1", (id_client,))
    if mycursor.fetchone()['nb'] >= 4:
        flash(u'Limite de 4 adresses valides atteinte.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    mycursor.execute("UPDATE adresse SET est_favorite = 0 WHERE utilisateur_id = %s", (id_client,))
    mycursor.execute(
        "INSERT INTO adresse (utilisateur_id, nom, rue, code_postal, ville, valide, est_favorite) VALUES (%s, %s, %s, %s, %s, 1, 1)",
        (id_client, nom, rue, code_postal, ville))
    get_db().commit()

    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')

    mycursor.execute("SELECT * FROM utilisateur WHERE id_utilisateur = %s", (id_client,))
    utilisateur = mycursor.fetchone()

    mycursor.execute("SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s", (id_adresse, id_client))
    adresse = mycursor.fetchone()

    if not adresse:
        flash(u'Adresse introuvable.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    return render_template('/client/coordonnee/edit_adresse.html', utilisateur=utilisateur, adresse=adresse)


@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')

    if len(code_postal) != 5 or not code_postal.isdigit():
        flash(u'Le code postal doit contenir 5 chiffres.', 'alert-warning')
        return redirect('/client/coordonnee/edit_adresse?id_adresse=' + str(id_adresse))

    mycursor.execute("SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s", (id_adresse, id_client))
    adresse_actuelle = mycursor.fetchone()

    if not adresse_actuelle:
        flash(u'Erreur de sécurité : cette adresse ne vous appartient pas.', 'alert-warning')
        return redirect('/client/coordonnee/show')

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM commande WHERE adresse_livraison_id = %s OR adresse_facturation_id = %s",
        (id_adresse, id_adresse))
    utilisee = mycursor.fetchone()['nb'] > 0

    if utilisee:
        mycursor.execute("UPDATE adresse SET valide = 0, est_favorite = 0 WHERE id_adresse = %s", (id_adresse,))
        mycursor.execute(
            "INSERT INTO adresse (utilisateur_id, nom, rue, code_postal, ville, valide, est_favorite) VALUES (%s, %s, %s, %s, %s, 1, %s)",
            (id_client, nom, rue, code_postal, ville, adresse_actuelle['est_favorite']))
    else:
        mycursor.execute("UPDATE adresse SET nom = %s, rue = %s, code_postal = %s, ville = %s WHERE id_adresse = %s",
                         (nom, rue, code_postal, ville, id_adresse))

    get_db().commit()
    return redirect('/client/coordonnee/show')
