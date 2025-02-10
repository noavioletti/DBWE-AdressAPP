#Python Funktionen aus Modulen importieren
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from .models import Address, User
from . import db
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

#Blueprint mit Name api registrieren und in Variable speichern API-Routen von anderen Routen in der Anwendung zu trennen.
api_bp = Blueprint('api', __name__)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password_hash):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password_hash):
        return user
    return None

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

#Token gültig machen
@api_bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})

#Token ungültig machen
@api_bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204

#HTTP-GET: Anzeigen Adressen
@api_bp.route('/addresses', methods=['GET'])
@token_auth.login_required
def get_addresses():
    #Authentifizierter Benutzer
    user = token_auth.current_user()
    #suchen in DB nach Adressen
    addresses = Address.query.filter_by(user_id=user.id).all()
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

#HTTP-POST: Neue Adresse hinzufügen
@api_bp.route('/addresses', methods=['POST'])
@token_auth.login_required
def add_address():
    user = token_auth.current_user()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Kein JSON-Daten empfangen"}), 400

    new_address = Address(
        user_id=user.id,
        vorname=data.get('vorname'),
        nachname=data.get('nachname'),
        telefonnummer_privat=data.get('telefonnummer_privat'),
        telefonnummer_geschaeftlich=data.get('telefonnummer_geschaeftlich'),
        email=data.get('email'),
        strasse=data.get('strasse'),
        plz=data.get('plz'),
        ort=data.get('ort'),
        land=data.get('land')
    )

    db.session.add(new_address)
    db.session.commit()

    return jsonify({"message": "Adresse erfolgreich hinzugefügt", "id": new_address.id}), 201

#HTTP-PUT: Adresse aktualisieren
@api_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@token_auth.login_required
def update_address(address_id):
    user = token_auth.current_user()
    address = Address.query.filter_by(id=address_id, user_id=user.id).first()

    if not address:
        return jsonify({"error": "Adresse nicht gefunden oder nicht autorisiert"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Kein JSON-Daten empfangen"}), 400

    address.vorname = data.get('vorname', address.vorname)
    address.nachname = data.get('nachname', address.nachname)
    address.telefonnummer_privat = data.get('telefonnummer_privat', address.telefonnummer_privat)
    address.telefonnummer_geschaeftlich = data.get('telefonnummer_geschaeftlich', address.telefonnummer_geschaeftlich)
    address.email = data.get('email', address.email)
    address.strasse = data.get('strasse', address.strasse)
    address.plz = data.get('plz', address.plz)
    address.ort = data.get('ort', address.ort)
    address.land = data.get('land', address.land)

    db.session.commit()

    return jsonify({"message": "Adresse erfolgreich aktualisiert"})

#HTTP-DELETE: Adresse löschen
@api_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@token_auth.login_required
def delete_address(address_id):
    user = token_auth.current_user()
    address = Address.query.filter_by(id=address_id, user_id=user.id).first()

    if not address:
        return jsonify({"error": "Adresse nicht gefunden oder nicht autorisiert"}), 404

    db.session.delete(address)
    db.session.commit()

    return jsonify({"message": "Adresse erfolgreich gelöscht"})
