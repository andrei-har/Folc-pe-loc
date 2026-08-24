from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, FloatField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import *

class RegisterForm(FlaskForm): #validarea datelor unui user
    nume = StringField('Nume și Prenume', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefon = StringField('Telefon', validators=[DataRequired(), Length(min=10, max=15)])
    parola = PasswordField('Parolă', validators=[DataRequired(), Length(min=8)])
    confirmare_parola = PasswordField('Confirmare Parola', validators=[DataRequired(), EqualTo('parola')])

    def validate_email(self, email):
            user = Utilizator.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email-ul este deja înregistrat!')
    
    def validate_telefon(self, telefon):
        if not telefon.data.startswith('07') or len(telefon.data) != 10:
            raise ValidationError('Formatul telefonului trebuie să fie 07xxxxxxxx')


#formul pt logare
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    parola = PasswordField('Parolă', validators=[DataRequired()])


# formul pentru adaugarea unui dans
class TipDansForm(FlaskForm):
    nume_dans = StringField('Nume Dans', validators=[DataRequired(), Length(max=100)])
    descriere = TextAreaField('Descriere')
    tip_structura = SelectField('Tip Structură', choices=[('perechi', 'Perechi'), ('grup', 'Grup')], validators=[DataRequired()])
    pret_baza = FloatField('Preț Bază (RON)', validators=[DataRequired()])
    regiune = StringField('Regiune', validators=[Length(max=50)])
    durata_minute = IntegerField('Durată (minute)', default=10)
    status = SelectField('Status', choices=[('activ', 'Activ'), ('inactiv', 'Inactiv')], default='activ')
    video_url = StringField('Link Video YouTube', validators=[Length(max=255)])


#form pt adaugarea unui eveniment
class EvenimentForm(FlaskForm):
    tip_eveniment = SelectField('Tip Eveniment', 
                                choices=[('nunta', 'Nuntă'), ('botez', 'Botez'), 
                                        ('festival', 'Festival'), ('corporate', 'Corporate'), 
                                        ('altele', 'Altele')], 
                                validators=[DataRequired()])
    data_eveniment = DateField('Data Eveniment', validators=[DataRequired()])
    ora_eveniment = TimeField('Ora Eveniment', validators=[DataRequired()])
    locatie = StringField('Locație', validators=[DataRequired(), Length(max=255)])
    observatii = TextAreaField('Observații')

