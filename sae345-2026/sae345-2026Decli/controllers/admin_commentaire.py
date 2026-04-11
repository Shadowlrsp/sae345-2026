#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, session
from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                        template_folder='templates')

@admin_commentaire.route('/admin/article/commentaires', methods=['GET'])
def admin_article_details():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)

    sql = '''
    SELECT c.utilisateur_id, c.meuble_id AS id_article, u.login AS nom, c.commentaire, c.valider, c.date_publication
    FROM commentaire c
    JOIN utilisateur u ON u.id_utilisateur = c.utilisateur_id
    WHERE c.meuble_id = %s
    ORDER BY c.valider ASC, c.date_publication DESC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()


    sql = '''
    SELECT id_meuble AS id_article, nom_meuble AS nom, prix_meuble AS prix, photo AS image, description,
           (SELECT AVG(note) FROM note WHERE meuble_id = m.id_meuble) AS moyenne_notes,
           (SELECT COUNT(*) FROM note WHERE meuble_id = m.id_meuble) AS nb_notes
    FROM meuble m
    WHERE m.id_meuble = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    sql = '''
    SELECT COUNT(*) AS nb_commentaires_total,
           SUM(CASE WHEN valider = 1 THEN 1 ELSE 0 END) AS nb_commentaires_valider
    FROM commentaire
    WHERE meuble_id = %s
    '''
    mycursor.execute(sql, (id_article,))
    nb_commentaires = mycursor.fetchone()

    return render_template('admin/article/show_article_commentaires.html',
                           commentaires=commentaires,
                           article=article,
                           nb_commentaires=nb_commentaires)

@admin_commentaire.route('/admin/article/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_utilisateur = request.form.get('id_utilisateur', None)
    id_article = request.form.get('id_article', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''
    DELETE FROM commentaire
    WHERE utilisateur_id = %s
    AND meuble_id = %s
    AND date_publication = %s
    '''
    mycursor.execute(sql, (id_utilisateur, id_article, date_publication))
    get_db().commit()
    return redirect('/admin/article/commentaires?id_article='+id_article)

@admin_commentaire.route('/admin/article/commentaires/repondre', methods=['POST','GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_utilisateur = request.args.get('id_utilisateur', None)
        id_article = request.args.get('id_article', None)
        date_publication = request.args.get('date_publication', None)
        return render_template('admin/article/add_commentaire.html',
                               id_utilisateur=id_utilisateur,
                               id_article=id_article,
                               date_publication=date_publication)

    mycursor = get_db().cursor()
    id_admin = session['id_user']
    id_article = request.form.get('id_article', None)
    id_utilisateur = request.form.get('id_utilisateur', None)
    date_publication = request.form.get('date_publication', None)
    commentaire = request.form.get('commentaire', None)
    sql = '''
    INSERT INTO commentaire(commentaire, utilisateur_id, meuble_id, date_publication, valider)
    VALUES (%s, %s, %s, NOW(), 1)
    '''
    mycursor.execute(sql, (commentaire, id_admin, id_article))
    get_db().commit()
    return redirect('/admin/article/commentaires?id_article='+id_article)

@admin_commentaire.route('/admin/article/commentaires/valider', methods=['POST','GET'])
def admin_comment_valider():
    id_article = request.args.get('id_article', None)
    mycursor = get_db().cursor()
    sql = '''
    UPDATE commentaire
    SET valider = 1
    WHERE meuble_id = %s
    '''
    mycursor.execute(sql, (id_article,))
    get_db().commit()
    return redirect('/admin/article/commentaires?id_article='+id_article)