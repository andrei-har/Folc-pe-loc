from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from models import db, Utilizator, Recenzie, Eveniment

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('client_dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.parola.data)
        user = Utilizator(
            nume=form.nume.data,
            email=form.email.data,
            telefon=form.telefon.data,
            parola=hashed_password,
            rol='client'
        )
        db.session.add(user)
        db.session.commit()
        flash('Cont creat cu succes! Te poți autentifica acum.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.rol == 'coregraf':
            return redirect(url_for('coregraf.dashboard'))
        return redirect(url_for('client.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Utilizator.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.parola, form.parola.data):
            login_user(user)

            if user.rol == 'coregraf':
                return redirect(url_for('coregraf.dashboard'))
            return redirect(url_for('client.dashboard'))
        
        flash('Email sau parolă incorectă!', 'danger')
    
    return render_template('login.html', form=form)


@auth_bp.route('/recenzii')
def recenzii_publice():
    """Pagină publică cu toate recenziile - accesibilă și pentru guests"""
    
    # Filtrare
    filtru_rating = request.args.get('rating', 'toate')
    
    query = Recenzie.query
    if filtru_rating != 'toate':
        query = query.filter_by(rating=int(filtru_rating))
    
    recenzii = query.order_by(Recenzie.data_recenzie.desc()).all()
    
    # Statistici
    total_recenzii = Recenzie.query.count()
    rating_mediu = db.session.query(db.func.avg(Recenzie.rating)).scalar() or 0
    
    # Distribuție rating-uri
    distributie = {}
    for i in range(1, 6):
        distributie[i] = Recenzie.query.filter_by(rating=i).count()
    
    return render_template('recenzii_publice.html',
                          recenzii=recenzii,
                          filtru_rating=filtru_rating,
                          total_recenzii=total_recenzii,
                          rating_mediu=round(rating_mediu, 1),
                          distributie=distributie)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))