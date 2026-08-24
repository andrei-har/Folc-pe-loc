from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from forms import EvenimentForm
from models import db, Eveniment, TipDans, MomentArtistic, Plati, Recenzie
from datetime import datetime, date

client_bp = Blueprint('client', __name__)

@client_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol != 'client':
        return redirect(url_for('coregraf.dashboard'))
    
    evenimente = Eveniment.query.filter_by(id_client=current_user.id_utilizator).order_by(Eveniment.data_creare.desc()).all()
    return render_template('client_dashboard.html', 
                          evenimente=evenimente,
                          data_azi=date.today())

@client_bp.route('/plateste/<int:id>', methods=['GET', 'POST'])
@login_required
def plateste(id):
    if current_user.rol != 'client':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    eveniment = Eveniment.query.get_or_404(id)
    
    if eveniment.id_client != current_user.id_utilizator:
        flash('Acces interzis!', 'danger')
        return redirect(url_for('client.dashboard'))
    
    if eveniment.status != 'acceptat':
        flash('Poti plati doar evenimente acceptate!', 'warning')
        return redirect(url_for('client.dashboard'))
    
    plata_existenta = Plati.query.filter_by(id_eveniment=id, status_plata='platit').first()
    if plata_existenta:
        flash('Evenimentul a fost deja platit!', 'info')
        return redirect(url_for('client.dashboard'))
    
    if request.method == 'POST':
        metoda_plata = request.form.get('metoda_plata')
        
        plata = Plati(
            id_eveniment=eveniment.id_eveniment,
            suma=eveniment.pret_total_calculat,
            metoda_plata=metoda_plata,
            status_plata='platit'
        )
        db.session.add(plata)
        db.session.commit()
        
        flash('Plată efectuată cu succes!', 'success')
        return redirect(url_for('client.dashboard'))
    
    return render_template('plateste.html', eveniment=eveniment)

@client_bp.route('/rezervare/pas1', methods=['GET', 'POST'])
@login_required
def rezervare_pas1():
    if current_user.rol != 'client':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    form = EvenimentForm()
    if form.validate_on_submit():
        session['eveniment_data'] = {
            'tip_eveniment': form.tip_eveniment.data,
            'data_eveniment': form.data_eveniment.data.isoformat(),
            'ora_eveniment': form.ora_eveniment.data.strftime('%H:%M'),
            'locatie': form.locatie.data,
            'observatii': form.observatii.data
        }
        return redirect(url_for('client.rezervare_pas2'))
    
    return render_template('rezervare_pas1.html', form=form)

@client_bp.route('/rezervare/pas2', methods=['GET', 'POST'])
@login_required
def rezervare_pas2():
    if current_user.rol != 'client':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    if 'eveniment_data' not in session:
        return redirect(url_for('client.rezervare_pas1'))
    
    dansuri = TipDans.query.filter_by(status='activ').all()
    
    if request.method == 'POST':
        dansuri_selectate = request.form.getlist('dans_ids')
        if not dansuri_selectate:
            flash('Selectează cel puțin un dans!', 'warning')
            return render_template('rezervare_pas2.html', dansuri=dansuri)
        
        session['dansuri_selectate'] = []
        pret_total = 0
        
        for dans_id in dansuri_selectate:
            dans = TipDans.query.get(int(dans_id))
            
            if dans.tip_structura == 'grup':
                # Pentru grup: nr_dansatori * pret_baza (minim 4)
                nr_dansatori = int(request.form.get(f'nr_dansatori_{dans_id}', 4))
                if nr_dansatori < 4:
                    nr_dansatori = 4
                pret = dans.pret_baza * nr_dansatori
            else:
                # Pentru perechi: 2 * nr_perechi * pret_baza (minim 2 perechi)
                nr_perechi = int(request.form.get(f'nr_perechi_{dans_id}', 2))
                if nr_perechi < 2:
                    nr_perechi = 2
                nr_dansatori = nr_perechi * 2  # convertim în nr dansatori
                pret = dans.pret_baza * nr_dansatori
            
            pret_total += pret
            
            session['dansuri_selectate'].append({
                'id_tip_dans': int(dans_id),
                'nr_dansatori': nr_dansatori,
                'tip_structura': dans.tip_structura,
                'pret': pret
            })
        
        session['pret_total'] = pret_total
        return redirect(url_for('client.rezervare_pas3'))
    
    return render_template('rezervare_pas2.html', dansuri=dansuri)

@client_bp.route('/rezervare/pas3', methods=['GET', 'POST'])
@login_required
def rezervare_pas3():
    if current_user.rol != 'client':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    if 'eveniment_data' not in session or 'dansuri_selectate' not in session:
        return redirect(url_for('client.rezervare_pas1'))
    
    if request.method == 'POST':
        eveniment_data = session['eveniment_data']
        eveniment = Eveniment(
            id_client=current_user.id_utilizator,
            tip_eveniment=eveniment_data['tip_eveniment'],
            data_eveniment=datetime.fromisoformat(eveniment_data['data_eveniment']),
            ora_eveniment=datetime.strptime(eveniment_data['ora_eveniment'], '%H:%M').time(),
            locatie=eveniment_data['locatie'],
            observatii=eveniment_data['observatii'],
            pret_total_calculat=session['pret_total'],
            status='in_asteptare'
        )
        db.session.add(eveniment)
        db.session.flush()
        
        for dans_data in session['dansuri_selectate']:
            moment = MomentArtistic(
                id_eveniment=eveniment.id_eveniment,
                id_tip_dans=dans_data['id_tip_dans'],
                nr_dansatori_solicitati=dans_data['nr_dansatori'],
                pret_per_dans=dans_data['pret']
            )
            db.session.add(moment)
        
        db.session.commit()
        
        session.pop('eveniment_data', None)
        session.pop('dansuri_selectate', None)
        session.pop('pret_total', None)
        
        flash('Cererea a fost trimisă cu succes! Vei primi un răspuns în curând.', 'success')
        return redirect(url_for('client.dashboard'))
    
    eveniment_data = session['eveniment_data']
    dansuri_selectate = []
    for dans_data in session['dansuri_selectate']:
        dans = TipDans.query.get(dans_data['id_tip_dans'])
        dansuri_selectate.append({
            'nume': dans.nume_dans,
            'nr_dansatori': dans_data['nr_dansatori'],
            'tip_structura': dans_data.get('tip_structura', dans.tip_structura),
            'pret': dans_data['pret']
        })
    
    return render_template('rezervare_pas3.html', 
                          eveniment=eveniment_data, 
                          dansuri=dansuri_selectate,
                          pret_total=session['pret_total'])

@client_bp.route('/recenzie/<int:id>', methods=['GET', 'POST'])
@login_required
def adauga_recenzie(id):
    if current_user.rol != 'client':
        flash('Acces interzis!', 'danger')
        return redirect(url_for('auth.index'))
    
    eveniment = Eveniment.query.get_or_404(id)
    
    # Verificări
    if eveniment.id_client != current_user.id_utilizator:
        flash('Acces interzis!', 'danger')
        return redirect(url_for('client.dashboard'))
    
    if eveniment.status != 'acceptat':
        flash('Poți recenza doar evenimente acceptate!', 'warning')
        return redirect(url_for('client.dashboard'))
    
    if eveniment.data_eveniment >= datetime.now().date():
        flash('Poți recenza doar evenimente trecute!', 'warning')
        return redirect(url_for('client.dashboard'))
    
    # Verifică dacă există deja recenzie
    recenzie_existenta = Recenzie.query.filter_by(
        id_eveniment=id,
        id_client=current_user.id_utilizator
    ).first()
    
    if recenzie_existenta:
        flash('Ai recenzat deja acest eveniment!', 'info')
        return redirect(url_for('client.dashboard'))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comentariu = request.form.get('comentariu', '').strip()
        
        if rating < 1 or rating > 5:
            flash('Rating-ul trebuie să fie între 1 și 5!', 'warning')
            return render_template('adauga_recenzie.html', eveniment=eveniment)
        
        recenzie = Recenzie(
            id_eveniment=eveniment.id_eveniment,
            id_client=current_user.id_utilizator,
            rating=rating,
            comentariu=comentariu if comentariu else None
        )
        
        db.session.add(recenzie)
        db.session.commit()
        
        flash('Recenzie adăugată cu succes! Mulțumim pentru feedback!', 'success')
        return redirect(url_for('client.dashboard'))
    
    return render_template('adauga_recenzie.html', eveniment=eveniment)