#Python Funktionen aus Modulen importieren
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

#DB Struktur für User Tabel
class User(UserMixin, db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)  
    lock_until = db.Column(db.DateTime, nullable=True)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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