#Python Funktionen aus Modulen importieren
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    #definieren SQL System
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    flaskSQLALCHEMY_TRACK_MODIFICATIONS = False