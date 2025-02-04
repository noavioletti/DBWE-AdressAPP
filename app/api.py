#Python Funktionen aus Modulen importieren
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .models import Address
from . import db

#Blueprint mit Name api registrieren und in Variable speichern API-Routen von anderen Routen in der Anwendung zu trennen.
api_bp = Blueprint('api', __name__)

#HTTP-GET-Route für anfragen von Adressen
@api_bp.route('/addresses', methods=['GET'])
@login_required
def get_addresses():
    #suchen in DB nach Adressen
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    #ausgabe von adressen
    return jsonify([{
        'id': addr.id,
        'vorname': addr.vorname,
        'nachname': addr.nachname,
        'telefonnummer_privat': addr.telefonnummer_privat,
        'telefonnummer_geschaeftlich': addr.telefonnummer_geschaeftlich,
        'email': addr.email,
        'strasse': addr.strasse,
        'plz': addr.plz,
        'ort': addr.ort,
        'land': addr.land
    } for addr in addresses])