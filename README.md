# ZA-ARC ➜ Modulon CSV-Konverter

Webanwendung, die den CSV-Export *Tätigkeitsprotokoll aus ZA-ARC* in das Layout der Datei *Fertig für Modulon* überführt. Upload, Umwandlung und Download erfolgen in einem Schritt.

## Features

- Drag & Drop oder Dateiauswahl für ZA-ARC-CSV-Dateien (`;`-Separierung)
- Automatischer Download der Modulon-kompatiblen CSV
- Spaltentransformationen:
  - `Mandant` → konstant `1`
  - `Lfd.-Nr.` → konstant `0`
  - `Name` → Aufteilung in `Nachname` / `Vormane`
  - `Typ` → Mapping (`Ruhe→RZ`, `Arbeit→AR`, `Bereit→BE`, `Lenken→LZ`)
  - `C | M | S` → `C/M/CR` (Format `1/0/0`)
  - Zeitspalten werden auf `HH:MM` normalisiert, `24:00:00` → `00:00`
  - `Hk` → konstant `DTG`
  - Nicht benötigte Modulon-Spalten bleiben leer
- Encoding-Autodetektion (UTF‑8 & Windows-1252)

## Lokale Nutzung

### Voraussetzungen

- Python ≥ 3.11 (alternativ Docker, siehe unten)

### Setup & Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app.main --debug run --port 8000
```

Die Anwendung läuft anschließend unter <http://127.0.0.1:8000>.

## Docker-Deployment

```powershell
docker build -t za-arc-to-modulon .
docker run --rm -p 8000:8000 za-arc-to-modulon
```

In Portainer kann dasselbe Image verwendet werden. Exponieren Sie Port `8000` nach außen.

## Validierung

1. Beispiel-Export aus ZA-ARC hochladen (`Tätikeitsprotokoll aus ZA-ARC.csv`).
2. Ausgabe mit Referenzdatei `Fertig für Modolon.csv` vergleichen.

## Architektur

- **Flask** als leichtgewichtiger Server (API + Templating)
- **Vanilla JavaScript** für Upload & Download-Handling
- Reiner CSV-Workflow (`csv.DictReader`/`csv.writer`), keine Datenbank erforderlich

## Projektstatistik

Das Projekt umfasst insgesamt **562 Zeilen Code** in folgenden Quelldateien:

- `app/converter.py`: 202 Zeilen (Konvertierungslogik)
- `app/static/styles.css`: 140 Zeilen (Styling)
- `app/static/app.js`: 119 Zeilen (Frontend-Logik)
- `app/templates/index.html`: 52 Zeilen (HTML-Template)
- `app/main.py`: 49 Zeilen (Flask-Server)

Zusätzlich **34 Zeilen** Konfigurationsdateien:

- `Dockerfile`: 21 Zeilen
- `docker-compose.yml`: 12 Zeilen
- `requirements.txt`: 1 Zeile

## Weiterentwicklung

- Unterstützung mehrerer Dateien im Batch-Modus
- Ergänzende Validierungsregeln (z. B. Pflichtfelder, zusätzliche Typ-Mappings)
- Authentifizierung oder Upload-Historie, falls Portal-Einsatz geplant ist

## Docker Compose

```yaml
services:
  za-arc-to-modulon:
    build:
      context: https://github.com/Achim-Sommer/ZA-ARCToModulon.git#main
      dockerfile: Dockerfile
    container_name: za-arc-to-modulon
    ports:
      - "9000:8000"
    environment:
      FLASK_RUN_HOST: 0.0.0.0
      FLASK_RUN_PORT: 8000
      FLASK_APP: app.main
    restart: unless-stopped
```
