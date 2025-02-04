#Python Funktionen aus Modulen importieren
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo, Length

#Definition python class für EditAdress, welche in routes.py wieder verwendet wird.
class EditAddressForm(FlaskForm):
    vorname = StringField('Vorname', validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired()])
    telefonnummer_privat = StringField('Telefonnummer Privat', validators=[DataRequired()])
    telefonnummer_geschaeftlich = StringField('Telefonnummer Geschäftlich')
    email = StringField('Email')
    strasse = StringField('Strasse', validators=[DataRequired()])
    plz = StringField('PLZ', validators=[DataRequired()])
    ort = StringField('Ort', validators=[DataRequired()])
    land = StringField('Land', validators=[DataRequired()])