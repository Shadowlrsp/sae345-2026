#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_article = Blueprint('admin_type_article', __name__,
                        template_folder='templates')

@admin_type_article.route('/admin/type-article/show', methods=['GET'])
def show_type_article():
    mycursor = get_db().cursor()
    sql = '''
        SELECT t.id_type_meuble AS id_type_article, 
               t.libelle_type_meuble AS libelle, 
               COUNT(m.id_meuble) AS nbr_articles
        FROM type_meuble t
        LEFT JOIN meuble m ON t.id_type_meuble = m.type_meuble_id AND m.actif = 1
        GROUP BY t.id_type_meuble, t.libelle_type_meuble
        ORDER BY t.libelle_type_meuble;
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()
    
    return render_template('admin/type_article/show_type_article.html', types_article=types_article)

@admin_type_article.route('/admin/type-article/add', methods=['GET'])
def add_type_article():
    return render_template('admin/type_article/add_type_article.html')

@admin_type_article.route('/admin/type-article/add', methods=['POST'])
def valid_add_type_article():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''INSERT INTO type_meuble (libelle_type_meuble) VALUES (%s);'''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-article/show')

@admin_type_article.route('/admin/type-article/delete', methods=['POST'])
def delete_type_article():
    id_type_article = request.form.get('id_type_article', '')
    mycursor = get_db().cursor()
    sql_check = "SELECT COUNT(*) AS nb FROM meuble WHERE type_meuble_id = %s"
    mycursor.execute(sql_check, (id_type_article,))
    nb_articles = mycursor.fetchone()['nb']
    if nb_articles > 0:
        flash(u'Impossible de supprimer : ce type contient encore des articles.', 'alert-danger')
    else:
        sql_delete = "DELETE FROM type_meuble WHERE id_type_meuble = %s"
        mycursor.execute(sql_delete, (id_type_article,))
        get_db().commit()
        flash(u'Suppression du type article effectuée (id : ' + id_type_article + ').', 'alert-success')
    return redirect('/admin/type-article/show')

@admin_type_article.route('/admin/type-article/edit', methods=['GET'])
def edit_type_article():
    id_type_article = request.args.get('id_type_article', '')
    mycursor = get_db().cursor()
    sql = '''SELECT id_type_meuble AS id_type_article, libelle_type_meuble AS libelle 
             FROM type_meuble 
             WHERE id_type_meuble = %s;'''
    mycursor.execute(sql, (id_type_article,))
    type_article = mycursor.fetchone()
    return render_template('admin/type_article/edit_type_article.html', type_article=type_article)

@admin_type_article.route('/admin/type-article/edit', methods=['POST'])
def valid_edit_type_article():
    libelle = request.form['libelle']
    id_type_article = request.form.get('id_type_article', '')
    tuple_update = (libelle, id_type_article)
    mycursor = get_db().cursor()
    sql = '''UPDATE type_meuble 
             SET libelle_type_meuble = %s 
             WHERE id_type_meuble = %s;'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    
    flash(u'Type article modifié, id: ' + id_type_article + " - nouveau libellé : " + libelle, 'alert-success')
    return redirect('/admin/type-article/show')








