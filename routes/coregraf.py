from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Eveniment, Plati
from datetime import datetime
from datetime import datetime, date

coregraf_bp = Blueprint('coregraf', __name__)

@coregraf_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol != 'coregraf':
        return redirect(url_for('client.dashboard'))
    
    cereri_noi = Eveniment.query.filter_by(status='in_asteptare').order_by(Eveniment.data_creare.desc()).all()
    evenimente_viitoare = Eveniment.query.filter(
        Eveniment.status == 'acceptat',
        Eveniment.data_eveniment >= datetime.now().date()
    ).order_by(Eveniment.data_eveniment).limit(5).all()
    
    total_venituri = db.session.query(db.func.sum(Eveniment.pret_total_calculat)).filter_by(status='acceptat').scalar() or 0
    total_evenimente = Eveniment.query.count()
    
    return render_template('coregraf_dashboard.html', 
                          cereri_noi=cereri_noi,
                          evenimente_viitoare=evenimente_viitoare,
                          total_venituri=total_venituri,
                          total_evenimente=total_evenimente)

@coregraf_bp.route('/istoric')
@login_required
def istoric():
    if current_user.rol != 'coregraf':
        return redirect(url_for('client.dashboard'))
    
    status_filtru = request.args.get('status', 'toate')
    perioada_filtru = request.args.get('perioada', 'toate')  # ✅ ADAUGĂ
    
    query = Eveniment.query
    
    # filtru status
    if status_filtru != 'toate':
        query = query.filter_by(status=status_filtru)
    
   
    data_azi = date.today()
    if perioada_filtru == 'viitor':
        query = query.filter(Eveniment.data_eveniment >= data_azi)
    elif perioada_filtru == 'trecut':
        query = query.filter(Eveniment.data_eveniment < data_azi)
    
    evenimente = query.order_by(Eveniment.data_creare.desc()).all()
    
    # Statistici
    total_acceptate = Eveniment.query.filter_by(status='acceptat').count()
    total_refuzate = Eveniment.query.filter_by(status='refuzat').count()
    total_asteptare = Eveniment.query.filter_by(status='in_asteptare').count()
    
    return render_template('istoric_evenimente.html',
                          evenimente=evenimente,
                          status_filtru=status_filtru,
                          perioada_filtru=perioada_filtru,  
                          total_acceptate=total_acceptate,
                          total_refuzate=total_refuzate,
                          total_asteptare=total_asteptare,
                          now=datetime.now)  

@coregraf_bp.route('/cerere/<int:id>', methods=['GET', 'POST'])
@login_required
def gestiune_cerere(id):
    if current_user.rol != 'coregraf':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    eveniment = Eveniment.query.get_or_404(id)
    
    if request.method == 'POST':
        actiune = request.form.get('actiune')
        
        if actiune == 'accepta':
            eveniment.status = 'acceptat'
            eveniment.data_raspuns_coregraf = datetime.utcnow()
            db.session.commit()
            flash('Cererea a fost acceptată!', 'success')
        
        elif actiune == 'refuza':
            motiv = request.form.get('motiv_refuz')
            if not motiv:
                flash('Motivul refuzului este obligatoriu!', 'warning')
                return render_template('gestiune_cerere.html', eveniment=eveniment)
            
            eveniment.status = 'refuzat'
            eveniment.motiv_refuz = motiv
            eveniment.data_raspuns_coregraf = datetime.utcnow()
            db.session.commit()
            flash('Cererea a fost refuzată!', 'info')
        
        return redirect(url_for('coregraf.dashboard'))
    
    return render_template('gestiune_cerere.html', eveniment=eveniment)