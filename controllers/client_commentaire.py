#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from connexion_db import get_db

client_commentaire = Blueprint('client_commentaire', __name__,
                        template_folder='templates')


@client_commentaire.route('/client/article/details', methods=['GET'])
def client_article_details():
    mycursor = get_db().cursor()
    id_article =  request.args.get('id_article', None)
    id_client = session['id_user']

    ## partie 4
    # client_historique_add(id_article, id_client)

    sql = '''
    SELECT 
        m.id_meuble AS id_article,
        m.nom_meuble AS nom,
        m.prix_meuble AS prix,
        m.photo AS image,
        m.description,
        AVG(n.note) AS moyenne_notes,
        COUNT(n.note) AS nb_notes
    FROM meuble m
    LEFT JOIN note n ON n.meuble_id = m.id_meuble
    WHERE m.id_meuble = %s
    GROUP BY 
        m.id_meuble,
        m.nom_meuble,
        m.prix_meuble,
        m.photo,
        m.description;
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    commandes_articles=[]
    nb_commentaires=[]

    if article is None:
        abort(404, "pb id article")

    sql = '''
    SELECT c.meuble_id AS id_article,
           c.utilisateur_id AS id_utilisateur,
           u.login AS nom,
           c.commentaire,
           c.valider,
           c.date_publication
    FROM commentaire c
    JOIN utilisateur u ON u.id_utilisateur = c.utilisateur_id
    WHERE c.meuble_id = %s
    ORDER BY c.date_publication DESC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    sql = '''
    SELECT COUNT(*) AS nb_commandes_article
    FROM ligne_commande lc
    JOIN commande c ON lc.commande_id = c.id_commande
    WHERE lc.meuble_id = %s
    AND c.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    commandes_articles = mycursor.fetchone()
    nb_commandes = commandes_articles['nb_commandes_article'] if commandes_articles else 0
    sql = '''
    SELECT note
    FROM note
    WHERE utilisateur_id = %s
    AND meuble_id = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    resultat_note = mycursor.fetchone()
    if resultat_note and 'note' in resultat_note:
        note = resultat_note['note']
    else:
        note = None

    print('note récupérée :', note)

    sql = '''
    SELECT
    (SELECT COUNT(*) 
    FROM commentaire 
    WHERE meuble_id=%s) AS nb_commentaires_total,

    (SELECT COUNT(*) 
    FROM commentaire 
    WHERE meuble_id=%s AND utilisateur_id=%s) AS nb_commentaires_utilisateur,

    (SELECT COUNT(*) 
    FROM commentaire 
    WHERE meuble_id=%s AND valider=1) AS nb_commentaires_total_valide,

    (SELECT COUNT(*) 
    FROM commentaire 
    WHERE meuble_id=%s AND utilisateur_id=%s AND valider=1) AS nb_commentaires_utilisateur_valide
    '''
    mycursor.execute(sql, (id_article, id_article, id_client, id_article, id_article, id_client))
    nb_commentaires = mycursor.fetchone()
    if nb_commentaires is None:
        nb_commentaires = {
            'nb_commentaires_total': 0,
            'nb_commentaires_utilisateur': 0,
            'nb_commentaires_total_valide': 0,
            'nb_commentaires_utilisateur_valide': 0
        }
    else:
        for key in nb_commentaires:
            if nb_commentaires[key] is None:
                nb_commentaires[key] = 0

    return render_template('client/article_info/article_details.html'
                           , article=article
                           , commentaires=commentaires
                           , commandes_articles=commandes_articles
                           , note=note
                           , nb_commentaires=nb_commentaires
                           )

@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', None)
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    sql = '''
          SELECT COUNT(*) AS nb_commentaires
          FROM commentaire
          WHERE utilisateur_id = %s
          AND meuble_id = %s 
          '''
    mycursor.execute(sql, (id_client, id_article))
    nb_commentaires = mycursor.fetchone()
    if nb_commentaires['nb_commentaires'] >= 3:
        flash(u'Quota de 3 commentaires atteint pour cet article', 'alert-danger')
        return redirect('/client/article/details?id_article=' + id_article)
    if commentaire == '':
        flash(u'Commentaire non prise en compte')
        return redirect('/client/article/details?id_article='+id_article)
    if commentaire != None and len(commentaire)>0 and len(commentaire) <3 :
        flash(u'Commentaire avec plus de 2 caractères','alert-warning')
        return redirect('/client/article/details?id_article='+id_article)

    tuple_insert = (commentaire, id_client, id_article)
    print(tuple_insert)
    sql = '''
    INSERT INTO commentaire(commentaire, utilisateur_id, meuble_id, date_publication, valider)
    VALUES (%s,%s,%s,NOW(),0)
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_detete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''
    DELETE FROM commentaire
    WHERE utilisateur_id = %s
    AND meuble_id = %s
    AND date_publication = %s
    '''
    tuple_delete=(id_client,id_article,date_publication)
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_insert = (note, id_client, id_article)
    print(tuple_insert)
    sql = '''
    INSERT INTO note(note, utilisateur_id, meuble_id, date_note)
    VALUES (%s,%s,%s,NOW())
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    tuple_update = (note, id_client, id_article)
    print(tuple_update)
    sql = '''
    UPDATE note
    SET note = %s
    WHERE utilisateur_id = %s
    AND meuble_id = %s
    '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)

@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    tuple_delete = (id_client, id_article)
    print(tuple_delete)
    sql = '''
    DELETE FROM note
    WHERE utilisateur_id = %s
    AND meuble_id = %s
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)