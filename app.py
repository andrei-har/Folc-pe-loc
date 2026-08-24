from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, FloatField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from models import db, Utilizator, TipDans, Eveniment, MomentArtistic, Plati, Recenzie


app = Flask(__name__)

app.config['SECRET_KEY'] = 'parola_mea_mega_ultra_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/folc_pe_loc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) #folder creat pt upload-uri



@login_manager.user_loader
def load_user(user_id):
    return Utilizator.query.get(int(user_id))

# incarca toare blueprins din routes
from forms import RegisterForm, LoginForm, TipDansForm, EvenimentForm
from routes import init_routes
init_routes(app)

@app.cli.command()
def init_db():
    """Creează toate tabelele și un user coregraf implicit"""
    db.create_all()
    
    coregraf = Utilizator.query.filter_by(rol='coregraf').first()
    if not coregraf:
        coregraf = Utilizator(
            nume='Administrator Ansamblu',
            email='coregraf@folc.ro',
            telefon='0700000000',
            parola=generate_password_hash('parola123'),
            rol='coregraf'
        )
        db.session.add(coregraf)
        db.session.commit()
        print('✓ Baza de date inițializată!')
        print('✓ User coregraf creat: coregraf@folc.ro / parola123')
    else:
        print('✓ Baza de date deja inițializată!')

if __name__ == '__main__':
    app.run(debug=True,  port=5000)

print("gata merge")