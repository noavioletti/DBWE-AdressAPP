#Python Funktionen aus Modulen importieren
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash
from .models import User, Address
from . import db, login_manager
from .forms import EditAddressForm
from datetime import datetime, timedelta

#Blueprint mit Name main erstellen und in Variable speichern für modulare Struktur in Flask und App in verschiedene Teile zu unterteilen
main_bp = Blueprint('main', __name__)

#Account Login Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#definieren Startseite mit index.html mit Blueprint Route
@main_bp.route('/')
def index():
    return render_template('index.html')

#Account anlegen
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Variabeln setzen für Account anlege Daten in DB mit reqest.form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            #Flash Meldung setzen und erstellen von Account verweigern wenn Username oder Email bereits in Verwendung ist
            flash('Benutzername oder Email existieren bereits.', 'danger')
            return redirect(url_for('main.register'))

        #Account wird angelegt und DB Commit ausgeführt bei erfolgreicher Überprüfung
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Erfolgreich registriert. Du kannst dich nun anmelden.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

#Login Account
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Variabeln setzen für Account Passwort Daten in DB mit reqest.form
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:            
            if user.lock_until and user.lock_until > datetime.utcnow():
                #Überprüfen, ob der Account gesperrt ist
                flash('Account ist vorübergehend gesperrt.', 'danger')
                return redirect(url_for('main.login'))

            if user.check_password(password):
                #Zurücksetzen bei erfolgreichem Login
                user.failed_attempts = 0  
                #Sperre aufheben
                user.lock_until = None  
                db.session.commit()
                login_user(user)
                return redirect(url_for('main.dashboard'))
            else:
                #Zähler +1 wenn Login Attem Failed
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    #wenn Attemp Variabel höher gleich als 5 ist wird Account gepserrt
                    user.lock_until = datetime.utcnow() + timedelta(minutes=15)
                    flash('Zu viele fehlgeschlagene versuche. Account ist für 15 Minuten gesperrt.', 'danger')
                else:
                    flash('falscher Benutzername oder Kennwort', 'danger')

                db.session.commit()
        else:
            flash('falscher Benutzername oder Kennwort.', 'danger')

        return redirect(url_for('main.login'))

    return render_template('login.html')
#Account Einstellungen
@main_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account_settings():
    return render_template('account.html', user=current_user)

#Account Daten ändern
@main_bp.route('/update_account', methods=['POST'])
@login_required
def update_account():
    #Variabeln setzen für Account Daten in DB mit reqest.form
    new_username = request.form['username']
    new_email = request.form['email']

    #Prüfen, ob der Username oder die EMail bereits existiert
    existing_user = User.query.filter((User.username == new_username) | (User.email == new_email)).first()
    if existing_user and existing_user.id != current_user.id:
        #Benutzername oder EMail existiert bereits, Flash Meldung setzen
        flash('Benutzername oder Email wird bereits verwendet.', 'danger')
        return redirect(url_for('main.account_settings'))

    #Änderungen speichern
    current_user.username = new_username
    current_user.email = new_email
    db.session.commit()

    flash('Account Informationen wurden erfolgreich geändert!', 'success')
    return redirect(url_for('main.account_settings'))

#Passwort ändern
@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    #Variabeln setzen für speichern von Passwort in DB mit reqest.form
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if not current_user.check_password(old_password):
        #Aktuelles Passwort stimmt nicht Flash Meldung setzen
        flash('Aktuelles Passwort ist nicht korrekt.', 'danger')
        return redirect(url_for('main.account_settings'))

    if new_password != confirm_password:
        #Passwort stimmt nicht überein Flash Meldung entsprechend setzen
        flash('Neues Passwort stimmt nicht überein.', 'danger')
        return redirect(url_for('main.account_settings'))

    #Neues Passwort in DB setzen für aktuellen User
    current_user.set_password(new_password)
    db.session.commit()
    flash('Passwort wurde erfolgreich geändert!', 'success')
    return redirect(url_for('main.account_settings'))

#Benutzerkonto löschen
@main_bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    user = current_user
    #Lösche alle zugehörigen Adressen des Benutzers
    Address.query.filter_by(user_id=user.id).delete()
    #Lösche User
    db.session.delete(user)
    db.session.commit()
    flash('Dein Account wurde gelöscht.', 'success')
    return redirect(url_for('main.index'))

#Logout Account
@main_bp.route('/logout')
@login_required
def logout():
    #Benutzer abmelden
    logout_user()
    return redirect(url_for('main.index'))

#Dashboard
@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    #Query Variabel setzen für was alles in Suche angezeigt werden soll
    query = request.args.get('query', '')
    if query:
        #Adressen anzeigen was in Suche angegeben wurde
        addresses = Address.query.filter(
            (Address.vorname.ilike(f'%{query}%')) |
            (Address.nachname.ilike(f'%{query}%')) |
            (Address.telefonnummer_privat.ilike(f'%{query}%')) |
            (Address.telefonnummer_geschaeftlich.ilike(f'%{query}%')) |
            (Address.email.ilike(f'%{query}%')) |
            (Address.strasse.ilike(f'%{query}%')) |
            (Address.plz.ilike(f'%{query}%')) |
            (Address.ort.ilike(f'%{query}%')) |
            (Address.land.ilike(f'%{query}%'))
        ).filter_by(user_id=current_user.id).all()
    else:
        #Alle Adressen vom User anzeigen
        addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', addresses=addresses, query=query)
    
#Adresse erstellen
@main_bp.route('/add_address', methods=['GET', 'POST'])
@login_required
def add_address():
    if request.method == 'POST':
        #Variabeln setzen für speichern von Werten in DB mit reqest.form
        vorname = request.form['vorname']
        nachname = request.form['nachname']
        telefonnummer_privat = request.form['telefonnummer_privat']
        telefonnummer_geschaeftlich = request.form['telefonnummer_geschaeftlich']
        email = request.form['email']
        strasse = request.form['strasse']
        plz = request.form['plz']
        ort = request.form['ort']
        land = request.form['land']
        
        #Variabel setzen, für anschliessender Commit
        new_address = Address(vorname=vorname, nachname=nachname, telefonnummer_privat=telefonnummer_privat, telefonnummer_geschaeftlich=telefonnummer_geschaeftlich, email=email, strasse=strasse, plz=plz, ort=ort, land=land, user_id=current_user.id)
        db.session.add(new_address)
        db.session.commit()
        flash('Adresse wurde erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('add_address.html')

#Adresse bearbeiten
@main_bp.route('/edit_address/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id != current_user.id:
        #ist User ID nicht gleich mit aktueller User ID wird Flash Meldugn gesetzt, dass keine Berechtigungen zur Bearbeitung von Adressen vorhanden sind.
        flash('Keine Berechtigung für die Bearbeitung der Adresse.', 'danger')
        return redirect(url_for('main.dashboard'))
    #Existierende Adressedaten verknüpfen mit form importiert aus forms.py class EditAdress
    form = EditAddressForm(obj=address)  
    if form.validate_on_submit():
        #Update Adresse mit form data und Flash Meldugn setzen, dass Adresse erfoglreich aktuallisiert wurde
        form.populate_obj(address)  
        db.session.commit()
        flash('Adresse wurde erfolgreich aktualisiert!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_address.html', form=form)

#Adresse löschen
@main_bp.route('/delete_address/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    #Adresse suchen und vergleichen, ob Current User aktuelle Berechtigungen zur Adresse hat
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    if address:
        #ist Bedingung korrekt wird Adresse gelöscht und Flash Message wird gesetzt, dass Adresse erfolgreich gelöscht wurde
        db.session.delete(address)
        db.session.commit()
        flash('Adresse wurde erfolgreich gelöscht!', 'success')
    else:
        #ist Bedingung nicht korrekt wird Flash Meldung gesetzt, dass Adresse nicht gefunden, oder dass keine Berechtigungen vorhanden sind für den Vorgang
        flash('Adresse wurde nicht gefunden oder keine Berechtigungen.', 'danger')
    return redirect(url_for('main.dashboard'))