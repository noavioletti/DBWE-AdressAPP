#Python Funktionen aus Modulen importieren
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

#Extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():    
    #definieren APP
    app = Flask(__name__)
    app.config.from_object(Config)

    #initialisieren extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    #registrieren blueprints
    from .routes import main_bp
    from .api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
