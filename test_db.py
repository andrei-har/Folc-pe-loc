from models import db, Utilizator
from flask import Flask

# Creează o mini-aplicație Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/folc_pe_loc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inițializează db
db.init_app(app)

# Testează conexiunea
with app.app_context():
    try:
        # Creează toate tabelele
        db.create_all()
        print("✅ SUCCESS! Tabelele au fost create în MySQL!")
        
        # Verifică ce tabele există
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tabele create: {tables}")
        
    except Exception as e:
        print(f"❌ EROARE: {e}")