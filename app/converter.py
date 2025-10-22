from __future__ import annotations

import csv
from dataclasses import dataclass
from io import BytesIO, StringIO
from typing import Iterable, List


TYPE_MAP = {
    "ruhe": "RZ",
    "arbeit": "AR",
    "bereit": "BE",
    "lenken": "LZ",
}

HEADERS: List[str] = [
    "Mandant",
    "Nachname",
    "Vormane",
    "Karte",
    "Tag",
    "Datum ",
    "Typ",
    "Lfd.-Nr.",
    "von",
    "bis",
    "Dauer",
    "Team",
    "Kennzeichen",
    "C/M/CR",
    "Hk",
    "Gruppe 1 ",
    "Gruppe 2",
    "Gruppe 3",
    "Personalnummer",
    "Bemerkung",
]

REQUIRED_COLUMNS = {
    "Name",
    "Karten-Nr.",
    "Zeitraum",
    "Tag",
    "Beginn",
    "Ende",
    "Dauer",
    "Typ",
    "Team",
    "C | M | S",
    "Kennzeichen",
}


@dataclass
class ConversionError(Exception):
    """Raised when the CSV file cannot be converted."""

    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def convert_za_arc_to_modulon(content: bytes) -> bytes:
    """Convert ZA-ARC CSV content into Modulon layout."""

    if not content:
        raise ConversionError("Leere Datei – bitte eine gültige ZA-ARC-CSV hochladen.")

    decoded = _decode_bytes(content)
    reader = csv.DictReader(StringIO(decoded), delimiter=";")

    if not reader.fieldnames:
        raise ConversionError("CSV ohne Kopfzeile – bitte Export aus ZA-ARC verwenden.")

    missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
    if missing:
        raise ConversionError(
            "Fehlende Spalten im Upload: " + ", ".join(sorted(missing))
        )

    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    writer.writerow(HEADERS)

    for row_number, row in enumerate(reader, start=1):
        writer.writerow(_convert_row(row, row_number))

    return output.getvalue().encode("utf-8-sig")


def _convert_row(row: dict[str, str], row_number: int) -> List[str]:
    last_name, first_name = _split_name(row.get("Name", ""))

    try:
        typ_code = _map_typ(row.get("Typ", ""))
        start = _format_time(row.get("Beginn", ""))
        end = _format_time(row.get("Ende", ""))
        duration = _format_duration(row.get("Dauer", ""))
    except ValueError as exc:  # pragma: no cover - guards against unexpected data formats
        raise ConversionError(
            f"Zeitformatfehler in Zeile {row_number}: {exc}"
        ) from exc

    cms = _format_cms(row.get("C | M | S", ""))

    return [
        "1",  # Mandant
        last_name,
        first_name,
        row.get("Karten-Nr.", "").strip(),
        row.get("Tag", "").strip(),
        row.get("Zeitraum", "").strip(),
        typ_code,
        "0",  # Lfd.-Nr.
        start,
        end,
        duration,
        row.get("Team", "").strip(),
        row.get("Kennzeichen", "").strip(),
        cms,
        "DTG",  # Hk
        "",  # Gruppe 1
        "",  # Gruppe 2
        "",  # Gruppe 3
        "",  # Personalnummer
        "",  # Bemerkung
    ]


def _map_typ(value: str) -> str:
    if not value:
        return ""
    normalised = value.strip().lower()
    if normalised in TYPE_MAP:
        return TYPE_MAP[normalised]
    return normalised[:2].upper()


def _split_name(full_name: str) -> tuple[str, str]:
    if not full_name:
        return "", ""
    parts = full_name.split(",", 1)
    if len(parts) == 2:
        last, first = parts[0].strip(), parts[1].strip()
    else:
        tokens = full_name.split()
        if not tokens:
            return "", ""
        last, first = tokens[0], " ".join(tokens[1:])
    return last, first


def _format_time(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    parts = value.split(":")
    if len(parts) < 2:
        raise ValueError(f"Ungültige Uhrzeit '{value}'")
    hours, minutes = parts[0], parts[1]
    return f"{int(hours) % 24:02d}:{int(minutes) % 60:02d}"


def _format_duration(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    parts = value.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours, minutes = parts
        seconds = "0"
    else:
        raise ValueError(f"Ungültige Dauer '{value}'")

    total_minutes = int(hours) * 60 + int(minutes)
    try:
        total_minutes += int(seconds) // 60
    except ValueError:
        seconds = seconds.strip()
        if seconds:
            raise

    hours_mod = (total_minutes // 60) % 24
    minutes_mod = total_minutes % 60
    return f"{hours_mod:02d}:{minutes_mod:02d}"


def _format_cms(value: str) -> str:
    value = (value or "").replace(" ", "")
    return value.replace("|", "/")


def _decode_bytes(content: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ConversionError("Zeichencodierung nicht erkannt – bitte UTF-8 oder CP1252 verwenden.")
