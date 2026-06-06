"""
config.py — Persistente App-Einstellungen (API-Keys, Nutzeroptionen).

Speicherort: %APPDATA%/SecBuddy/config.json  (Windows)
             ~/.config/SecBuddy/config.json   (Fallback für andere Systeme)

Format: einfaches JSON-Dictionary. Keine sensiblen Daten werden unverschlüsselt
gespeichert — API-Keys liegen im Klartext, was bei lokalen Desktop-Apps üblich ist.
"""

import json
import os
from pathlib import Path


def _config_path() -> Path:
    """Gibt den Pfad zur config.json zurück, passend zum Betriebssystem."""
    appdata = os.environ.get("APPDATA")          # Windows: C:\Users\...\AppData\Roaming
    if appdata:
        return Path(appdata) / "SecBuddy" / "config.json"
    return Path.home() / ".config" / "SecBuddy" / "config.json"


def _load() -> dict:
    """Liest die config.json ein. Gibt ein leeres Dict zurück wenn die Datei fehlt."""
    path = _config_path()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    """Schreibt das Dict als JSON in die config.json. Erstellt Verzeichnisse bei Bedarf."""
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get(key: str, default=None):
    """Liest einen Wert aus der Konfiguration."""
    return _load().get(key, default)


def set(key: str, value) -> None:
    """Setzt einen Wert und speichert ihn sofort."""
    data = _load()
    data[key] = value
    _save(data)


def delete(key: str) -> None:
    """Entfernt einen Schlüssel aus der Konfiguration."""
    data = _load()
    data.pop(key, None)
    _save(data)
