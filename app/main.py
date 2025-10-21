from __future__ import annotations

import io
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file

from .converter import ConversionError, convert_zaak_to_modulon

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", build_time=datetime.utcnow())


@app.post("/convert")
def convert():
    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({"error": "Bitte eine CSV-Datei auswählen."}), 400

    file_bytes = uploaded_file.read()
    try:
        converted = convert_zaak_to_modulon(file_bytes)
    except ConversionError as exc:
        return jsonify({"error": str(exc)}), 400

    output = io.BytesIO(converted)
    output.seek(0)

    download_name = _build_download_name(uploaded_file.filename)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=download_name,
    )


def _build_download_name(filename: str) -> str:
    stem = filename.rsplit(".", 1)[0]
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{stem}-fertig-fuer-modulon-{timestamp}.csv"


if __name__ == "__main__":
    app.run(debug=True)
