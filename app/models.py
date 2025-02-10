#Python Funktionen aus Modulen importieren
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import base64
import os

#DB Struktur für User Tabel
class User(UserMixin, db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)  
    lock_until = db.Column(db.DateTime, nullable=True)  
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Token erzeugen, speichern und zurückgeben
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
        # Token existiert und ist noch nicht abgelaufen
            return self.token
        # Falls der Token nicht existiert oder abgelaufen ist, wird
        # ein zufälliger String erzeugt und base64-kodiert
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

        # Token ungültig machen
    def revoke_token(self):
        # Ablaufdatum auf aktuelle Zeit - 1 sek. setzen
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        
        # Token prüfen
    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None # Token nicht gefunden oder abgelaufen
        return user # Token ist gültig
    
#DB Struktur für Adress Tabelle
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    telefonnummer_privat = db.Column(db.String(20))
    telefonnummer_geschaeftlich = db.Column(db.String(20))
    email = db.Column(db.String(120))
    strasse = db.Column(db.String(120))
    plz = db.Column(db.Integer)
    ort = db.Column(db.String(100))
    land = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
