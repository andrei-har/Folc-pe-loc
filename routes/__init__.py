# exista doar pentru importuri

from flask import Flask

def init_routes(app):
    from .auth import auth_bp
    from .client import client_bp
    from .coregraf import coregraf_bp
    from .dansuri import dansuri_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(coregraf_bp, url_prefix='/coregraf')
    app.register_blueprint(dansuri_bp, url_prefix='/coregraf/dansuri')