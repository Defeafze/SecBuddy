"""
Sentry-Integration für SecBuddy.

Was wird erfasst:
  - Unbehandelte Exceptions (Crashes) inkl. Stacktrace
  - Tkinter-interne Exceptions (werden sonst lautlos verschluckt)
  - Sessions: App-Start, Laufzeit, Version, Absturzrate
  - Tool-Nutzung: welches Tool wann wie oft geöffnet wurde (Custom Metrics)

Was wird NICHT erfasst:
  - Nutzereingaben (URLs, Passwörter, E-Mail-Adressen)
  - Dateinamen oder Bildinhalte
"""

import sys
import uuid
import atexit
from pathlib import Path

_initialized = False

# Lesbarer Anzeigename je Seiten-Key (erscheint so im Sentry-Dashboard)
_TOOL_LABELS: dict[str, str] = {
    "home":                 "Startseite",
    "password_generator":   "Passwort-Generator",
    "passphrase_generator": "Passphrasen-Generator",
    "password_strength":    "Passwort-Stärke",
    "password_check":       "Passwort-Check",
    "email_check":          "E-Mail-Check",
    "phishing_check":       "URL & Absender",
    "phone_check":          "Rufnummer-Check",
    "scam_check":           "Text-Scan",
    "qr_check":             "QR-Check",
    "fakeshop_detector":    "Fakeshop-Detector",
    "sender_scanner":       "Absender-Scanner",
    "exif_remover":         "EXIF entfernen",
    "help":                 "Hilfe",
}


def init(dsn: str, version: str) -> None:
    """Sentry initialisieren. Vor dem Erstellen des Tk-Fensters aufrufen."""
    global _initialized
    if _initialized or not dsn:
        return

    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            release=f"secbuddy@{version}",
            environment="production",

            # Sessions: zählt App-Starts, Laufzeit, Absturzrate
            auto_session_tracking=True,

            # IP-Adresse + Gerätename werden mitgesendet (für Geo-Stats)
            send_default_pii=True,

            # Performance-Tracing aus (kein Bedarf, spart Quota)
            traces_sample_rate=0.0,

            # HTTP-Requests aus Breadcrumbs raushalten (Datenschutz)
            before_breadcrumb=_filter_breadcrumb,
        )

        # Anonyme stabile Geräte-ID → "Unique Users" im Dashboard
        sentry_sdk.set_user({"id": _device_id()})

        # Tkinter-Exceptions (GUI-Callbacks) abfangen
        _hook_tkinter()

        # Beim sauberen Beenden Puffer leeren (verhindert verlorene Events)
        atexit.register(sentry_sdk.flush, timeout=3)

        _initialized = True

    except ImportError:
        pass  # sentry-sdk nicht installiert → still ignorieren


def track_tool(page_key: str) -> None:
    """
    Zählt wie oft ein Tool geöffnet wurde.

    Erscheint in Sentry unter Explore → Metrics als Zeitreihe:
      Metric:  secbuddy.tool.opened
      Tag:     tool = "Passwort-Generator"

    So kannst du sehen:
      - Welches Tool heute / diese Woche am häufigsten genutzt wurde
      - Zu welcher Uhrzeit die App am meisten genutzt wird
      - Wie sich Nutzung nach einem Update verändert (per Release-Filter)
    """
    if not _initialized:
        return
    # home + help nicht tracken — nur echte Tools
    if page_key in ("home", "help"):
        return
    try:
        import sentry_sdk.metrics as m
        label = _TOOL_LABELS.get(page_key, page_key)
        m.count("secbuddy.tool.opened", 1, attributes={"tool": label})
    except Exception:
        pass


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _device_id() -> str:
    """Liest oder erstellt eine stabile, anonyme Geräte-ID."""
    id_file = Path.home() / ".secbuddy_device_id"
    try:
        if id_file.exists():
            return id_file.read_text().strip()
        new_id = str(uuid.uuid4())
        id_file.write_text(new_id)
        return new_id
    except OSError:
        return "unknown"


def _hook_tkinter() -> None:
    """
    Überschreibt report_callback_exception: Exceptions in Button-Klicks
    und Event-Handlern landen sonst lautlos in /dev/null.
    """
    import tkinter as tk

    _original = getattr(tk.Tk, "report_callback_exception", None)

    def _handler(self, exc_type, exc_val, exc_tb):
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(exc_val)
        except Exception:
            pass
        if _original:
            _original(self, exc_type, exc_val, exc_tb)
        else:
            sys.stderr.write(f"Exception in Tkinter-Callback: {exc_val}\n")

    tk.Tk.report_callback_exception = _handler


def _filter_breadcrumb(crumb: dict, hint: dict) -> dict | None:
    if crumb.get("category") in ("httplib", "urllib3", "requests"):
        return None
    return crumb
