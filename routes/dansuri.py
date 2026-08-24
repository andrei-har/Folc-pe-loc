from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from forms import TipDansForm
from models import db, TipDans
import os

dansuri_bp = Blueprint('dansuri', __name__)

@dansuri_bp.route('/')
@login_required
def lista_dansuri():
    if current_user.rol != 'coregraf':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    dansuri = TipDans.query.order_by(TipDans.data_creare.desc()).all()
    return render_template('lista_dansuri.html', dansuri=dansuri)

@dansuri_bp.route('/adauga', methods=['GET', 'POST'])
@login_required
def adauga_dans():
    if current_user.rol != 'coregraf':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    form = TipDansForm()
    if form.validate_on_submit():
        dans = TipDans(
            nume_dans=form.nume_dans.data,
            descriere=form.descriere.data,
            tip_structura=form.tip_structura.data,
            pret_baza=form.pret_baza.data,
            regiune=form.regiune.data,
            durata_minute=form.durata_minute.data,
            status=form.status.data,
            video_url=form.video_url.data
        )
        
        if 'imagine' in request.files:
            file = request.files['imagine']
            if file and file.filename:
                from app import app
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                dans.imagine_url = f'/static/uploads/{filename}'
        
        db.session.add(dans)
        db.session.commit()
        flash('Dansul a fost adăugat cu succes!', 'success')
        return redirect(url_for('dansuri.lista_dansuri'))
    
    return render_template('adauga_dans.html', form=form)

@dansuri_bp.route('/editeaza/<int:id>', methods=['GET', 'POST'])
@login_required
def editeaza_dans(id):
    if current_user.rol != 'coregraf':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    dans = TipDans.query.get_or_404(id)
    form = TipDansForm(obj=dans)
    
    if form.validate_on_submit():
        dans.nume_dans = form.nume_dans.data
        dans.descriere = form.descriere.data
        dans.tip_structura = form.tip_structura.data
        dans.pret_baza = form.pret_baza.data
        dans.regiune = form.regiune.data
        dans.durata_minute = form.durata_minute.data
        dans.status = form.status.data
        dans.video_url = form.video_url.data
        
        if 'imagine' in request.files:
            file = request.files['imagine']
            if file and file.filename:
                from app import app
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                dans.imagine_url = f'/static/uploads/{filename}'
        
        db.session.commit()
        flash('Dansul a fost actualizat!', 'success')
        return redirect(url_for('dansuri.lista_dansuri'))
    
    return render_template('editeaza_dans.html', form=form, dans=dans)

@dansuri_bp.route('/sterge/<int:id>', methods=['POST'])
@login_required
def sterge_dans(id):
    if current_user.rol != 'coregraf':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    dans = TipDans.query.get_or_404(id)
    
    # Verifică dacă dansul e folosit în evenimente
    from models import MomentArtistic
    momente_asociate = MomentArtistic.query.filter_by(id_tip_dans=id).count()
    
    if momente_asociate > 0:
        flash(f'Nu poți șterge acest dans! Este folosit în {momente_asociate} rezervări.', 'danger')
        return redirect(url_for('dansuri.lista_dansuri'))
    
    db.session.delete(dans)
    db.session.commit()
    flash('Dansul a fost șters!', 'success')
    return redirect(url_for('dansuri.lista_dansuri'))