#Python Funktionen aus Modulen importieren
from app import create_app

#Funktion create_app abrufen und alles in app Variable speichern
app = create_app()

#prüfen ob Script direkt ausgeführt wird
if __name__ == '__main__':
    #app starten mit definieren von subent für zugriff von alle, port und debug-level aktivieren
    app.run(host='0.0.0.0', port=5000, debug=True)