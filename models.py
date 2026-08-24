#model pt baza de date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Utilizator(UserMixin, db.Model):
    __tablename__ = 'utilizator'
    id_utilizator = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefon = db.Column(db.String(15), nullable=False)
    parola = db.Column(db.String(255), nullable=False)
    nume = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.Enum('client', 'coregraf'), default='client')
    data_inregistrare = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relatii cu alte clase
    evenimente = db.relationship('Eveniment', backref='client', lazy=True)
    recenzii = db.relationship('Recenzie', backref='client', lazy=True)
    
    def get_id(self):
        return str(self.id_utilizator)
    
class TipDans(db.Model):
    __tablename__ = 'tip_dans'
    id_tip_dans = db.Column(db.Integer, primary_key=True)
    nume_dans = db.Column(db.String(100), nullable=False)
    descriere = db.Column(db.Text)
    tip_structura = db.Column(db.Enum('perechi', 'grup'), nullable=False)
    pret_baza = db.Column(db.Float, nullable=False)
    regiune = db.Column(db.String(50))
    durata_minute = db.Column(db.Integer, default=10)
    status = db.Column(db.Enum('activ', 'inactiv'), default='activ')
    imagine_url = db.Column(db.String(255))
    video_url = db.Column(db.String(255))
    data_creare = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relatii
    momente = db.relationship('MomentArtistic', backref='tip_dans', lazy=True)

class Eveniment(db.Model):
    __tablename__ = 'eveniment'
    id_eveniment = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('utilizator.id_utilizator'), nullable=False)
    tip_eveniment = db.Column(db.Enum('nunta', 'botez', 'festival', 'corporate', 'altele'), nullable=False)
    data_eveniment = db.Column(db.Date, nullable=False)
    ora_eveniment = db.Column(db.Time, nullable=False)
    locatie = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('in_asteptare', 'acceptat', 'refuzat', 'finalizat'), default='in_asteptare')
    motiv_refuz = db.Column(db.Text)
    pret_total_calculat = db.Column(db.Float, nullable=False)
    observatii = db.Column(db.Text)
    data_creare = db.Column(db.DateTime, default=datetime.utcnow)
    data_raspuns_coregraf = db.Column(db.DateTime)
    
    # relatii cu alte clase
    momente = db.relationship('MomentArtistic', backref='eveniment', lazy=True, cascade='all, delete-orphan')
    plati = db.relationship('Plati', backref='eveniment', lazy=True, cascade='all, delete-orphan')
    recenzii = db.relationship('Recenzie', backref='eveniment', lazy=True, cascade='all, delete-orphan')

class MomentArtistic(db.Model):
    __tablename__ = 'moment_artistic'
    id_moment = db.Column(db.Integer, primary_key=True)
    id_eveniment = db.Column(db.Integer, db.ForeignKey('eveniment.id_eveniment'), nullable=False)
    id_tip_dans = db.Column(db.Integer, db.ForeignKey('tip_dans.id_tip_dans'), nullable=False)
    nr_dansatori_solicitati = db.Column(db.Integer, nullable=False)
    pret_per_dans = db.Column(db.Float, nullable=False)
    observatii = db.Column(db.Text)

class Plati(db.Model):
    __tablename__ = 'plati'
    id_plata = db.Column(db.Integer, primary_key=True)
    id_eveniment = db.Column(db.Integer, db.ForeignKey('eveniment.id_eveniment'), nullable=False)
    suma = db.Column(db.Float, nullable = False)
    metoda_plata = db.Column(db.Enum('card','cash', 'transfer'), nullable=False)
    data_plata = db.Column(db.DateTime, default=datetime.utcnow)
    status_plata = db.Column(db.Enum('platit', 'in_asteptare'), default='in_asteptare')

class Recenzie(db.Model):
    __tablename__ = 'recenzie'
    id_recenzie = db.Column(db.Integer, primary_key=True)
    id_eveniment = db.Column(db.Integer, db.ForeignKey('eveniment.id_eveniment'), nullable=False)
    id_client = db.Column(db.Integer, db.ForeignKey('utilizator.id_utilizator'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comentariu = db.Column(db.Text)
    data_recenzie = db.Column(db.DateTime, default=datetime.utcnow)