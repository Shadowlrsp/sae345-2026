#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                         template_folder='templates')

@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['GET'])
def add_declinaison_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    
    sql_article = '''SELECT id_meuble AS id_article, nom_meuble AS nom, photo AS image 
                     FROM meuble WHERE id_meuble = %s'''
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    mycursor.execute("SELECT id_couleur, libelle_couleur FROM couleur")
    couleurs = mycursor.fetchall()
    mycursor.execute("SELECT id_taille, libelle_taille FROM taille")
    tailles = mycursor.fetchall()

    sql_check = "SELECT COUNT(*) as nb FROM declinaison_meuble WHERE meuble_id = %s AND taille_id = 1"
    mycursor.execute(sql_check, (id_article,))
    d_taille_uniq = mycursor.fetchone()['nb']

    sql_check_c = "SELECT COUNT(*) as nb FROM declinaison_meuble WHERE meuble_id = %s AND couleur_id = 1"
    mycursor.execute(sql_check_c, (id_article,))
    d_couleur_uniq = mycursor.fetchone()['nb']

    return render_template('admin/article/add_declinaison_article.html', 
                           article=article, couleurs=couleurs, tailles=tailles, 
                           d_taille_uniq=d_taille_uniq, d_couleur_uniq=d_couleur_uniq)

@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    stock = request.form.get('stock', 0, type=int)
    id_taille = request.form.get('id_taille')
    id_couleur = request.form.get('id_couleur')

    mycursor.execute("SELECT COUNT(*) as nb FROM declinaison_meuble WHERE meuble_id = %s", (id_article,))
    nb_existantes = mycursor.fetchone()['nb']

    sql_check_unique = "SELECT * FROM declinaison_meuble WHERE meuble_id=%s AND (taille_id=1 OR couleur_id=1)"
    mycursor.execute(sql_check_unique, (id_article,))
    decli_existante = mycursor.fetchone()

    if (id_taille == "1" or id_couleur == "1") and nb_existantes > 0:
        flash(u'Impossible d\'ajouter une propriété "Unique" : des variantes spécifiques existent déjà.', 'alert-warning')
        return redirect('/admin/article/edit?id_article=' + id_article)

    if decli_existante:
        if decli_existante['taille_id'] == 1 and decli_existante['couleur_id'] == 1:
            flash(u'Cet article est configuré comme "Unique". Supprimez cette variante pour ajouter des tailles/couleurs spécifiques.', 'alert-danger')
            return redirect('/admin/article/edit?id_article=' + id_article)

    sql_check_doublon = "SELECT * FROM declinaison_meuble WHERE meuble_id = %s AND taille_id = %s AND couleur_id = %s"
    mycursor.execute(sql_check_doublon, (id_article, id_taille, id_couleur))
    if mycursor.fetchone():
        flash(u'Erreur : Cette combinaison (Taille/Couleur) existe déjà pour cet article ! Éditez plutôt son stock.', 'alert-warning')
        return redirect('/admin/article/edit?id_article=' + id_article)

    sql = "INSERT INTO declinaison_meuble (meuble_id, taille_id, couleur_id, stock, prix_declinaison) VALUES (%s, %s, %s, %s, (SELECT prix_meuble FROM meuble WHERE id_meuble=%s))"
    mycursor.execute(sql, (id_article, id_taille, id_couleur, stock, id_article))
    get_db().commit()
    
    flash(u'Nouvelle déclinaison ajoutée avec succès !', 'alert-success')
    return redirect('/admin/article/edit?id_article=' + id_article)


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['GET'])
def edit_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article')
    mycursor = get_db().cursor()
    
    sql_decli = '''
        SELECT dm.*, m.nom_meuble AS nom, m.photo AS image_article, m.id_meuble AS article_id
        FROM declinaison_meuble dm
        JOIN meuble m ON dm.meuble_id = m.id_meuble
        WHERE dm.id_declinaison_meuble = %s
    '''
    mycursor.execute(sql_decli, (id_declinaison_article,))
    declinaison_article = mycursor.fetchone()

    if not declinaison_article:
        flash(u'Déclinaison introuvable.', 'alert-danger')
        return redirect('/admin/article/show')

    id_article = declinaison_article['article_id']

    mycursor.execute("SELECT id_couleur, libelle_couleur FROM couleur")
    couleurs = mycursor.fetchall()
    
    mycursor.execute("SELECT id_taille, libelle_taille FROM taille")
    tailles = mycursor.fetchall()

    mycursor.execute("SELECT COUNT(*) as nb FROM declinaison_meuble WHERE meuble_id = %s AND taille_id = 1", (id_article,))
    d_taille_uniq = mycursor.fetchone()['nb']

    mycursor.execute("SELECT COUNT(*) as nb FROM declinaison_meuble WHERE meuble_id = %s AND couleur_id = 1", (id_article,))
    d_couleur_uniq = mycursor.fetchone()['nb']

    return render_template('admin/article/edit_declinaison_article.html',
                           declinaison_article=declinaison_article,
                           tailles=tailles,
                           couleurs=couleurs,
                           d_taille_uniq=d_taille_uniq,
                           d_couleur_uniq=d_couleur_uniq)

@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    mycursor = get_db().cursor()
    
    id_declinaison_article = request.form.get('id_declinaison_article')
    id_article = request.form.get('id_article')
    stock = request.form.get('stock', 0, type=int)
    taille_id = request.form.get('id_taille')
    couleur_id = request.form.get('id_couleur')

    sql_check_doublon = '''SELECT * FROM declinaison_meuble 
                           WHERE meuble_id = %s AND taille_id = %s AND couleur_id = %s 
                           AND id_declinaison_meuble != %s AND actif = 1'''
    mycursor.execute(sql_check_doublon, (id_article, taille_id, couleur_id, id_declinaison_article))
    
    if mycursor.fetchone():
        flash(u'Erreur : Cette combinaison (Taille/Couleur) existe déjà pour cet article !', 'alert-danger')
        return redirect('/admin/declinaison_article/edit?id_declinaison_article=' + str(id_declinaison_article))
        
    
    sql_check_cmd = "SELECT COUNT(*) AS nb FROM ligne_commande WHERE meuble_declinaison_id = %s"
    mycursor.execute(sql_check_cmd, (id_declinaison_article,))
    is_ordered = mycursor.fetchone()['nb'] > 0

    if is_ordered:
        mycursor.execute("UPDATE declinaison_meuble SET actif = 0 WHERE id_declinaison_meuble = %s", (id_declinaison_article,))
        sql_insert = '''INSERT INTO declinaison_meuble (meuble_id, taille_id, couleur_id, stock, prix_declinaison, actif) 
                        VALUES (%s, %s, %s, %s, (SELECT prix_declinaison FROM declinaison_meuble WHERE id_declinaison_meuble=%s), 1)'''
        mycursor.execute(sql_insert, (id_article, taille_id, couleur_id, stock, id_declinaison_article))
        flash(u'Variante déjà commandée dans le passé : une copie a été créée avec vos nouvelles modifications et l\'ancienne a été archivée.', 'alert-success')
    else:
        sql_update = '''UPDATE declinaison_meuble 
                        SET stock = %s, taille_id = %s, couleur_id = %s 
                        WHERE id_declinaison_meuble = %s'''
        mycursor.execute(sql_update, (stock, taille_id, couleur_id, id_declinaison_article))
        flash(u'Les informations de la variante ont été mises à jour.', 'alert-success')

    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + str(id_article))



@admin_declinaison_article.route('/admin/declinaison_article/delete', methods=['POST'])
def admin_delete_declinaison_article():
    id_declinaison_article = request.form.get('id_declinaison_article')
    id_article = request.form.get('id_article')
    mycursor = get_db().cursor()

    sql_check = "SELECT COUNT(*) AS nb FROM ligne_commande WHERE meuble_declinaison_id = %s"
    mycursor.execute(sql_check, (id_declinaison_article,))
    
    if mycursor.fetchone()['nb'] > 0:
        mycursor.execute("UPDATE declinaison_meuble SET actif = 0 WHERE id_declinaison_meuble = %s", (id_declinaison_article,))
        flash(u'Variante archivée (déjà présente sur des factures).', 'alert-info')
    else:
        mycursor.execute("DELETE FROM ligne_panier WHERE meuble_declinaison_id = %s", (id_declinaison_article,))
        mycursor.execute("DELETE FROM declinaison_meuble WHERE id_declinaison_meuble = %s", (id_declinaison_article,))
        flash(u'Variante supprimée avec succès.', 'alert-success')

    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + str(id_article))