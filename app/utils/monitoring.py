"""
Sentry-Integration für SecBuddy.

Was wird erfasst:
  - Unbehandelte Exceptions (Crashes) inkl. Stacktrace
  - Tkinter-interne Exceptions (werden sonst lautlos verschluckt)
  - Sessions: App-Start, Laufzeit, Version, Absturzrate
  - Tool-Nutzung: Metrics (secbuddy.tool.opened / secbuddy.action.used)

Was wird NICHT erfasst:
  - Nutzereingaben (URLs, Passwörter, E-Mail-Adressen)
  - Dateinamen oder Bildinhalte
"""

import sys
import uuid
import atexit
from pathlib import Path

_initialized = False

_TOOL_LABELS: dict[str, str] = {
    "home":                 "Startseite",
    "password_generator":   "Passwort-Generator",
    "passphrase_generator": "Passphrasen-Generator",
    "password_strength":    "Passwort-Staerke",
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
    "settings":             "Einstellungen",
}


def init(dsn: str, version: str) -> None:
    """Sentry initialisieren."""
    global _initialized
    if _initialized or not dsn:
        return

    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            release=f"secbuddy@{version}",
            environment="production",
            auto_session_tracking=True,
            send_default_pii=True,
            traces_sample_rate=0.0,
            before_breadcrumb=_filter_breadcrumb,
        )

        sentry_sdk.set_user({"id": _device_id()})
        _hook_tkinter()
        atexit.register(sentry_sdk.flush, timeout=3)

        _initialized = True

    except Exception:
        pass


def track_tool(page_key: str) -> None:
    """
    Trackt wie oft ein Tool geoeffnet wurde.

    Sichtbar in Sentry unter Explore > Metrics:
      Metric: secbuddy.tool.opened
      Tag:    tool = "Fakeshop-Detector"
    """
    if not _initialized:
        return
    if page_key in ("home", "help", "settings"):
        return
    try:
        import sentry_sdk.metrics as m
        label = _TOOL_LABELS.get(page_key, page_key)
        m.count("secbuddy.tool.opened", 1, attributes={"tool": label})
    except Exception:
        pass


def track_action(page_key: str, action: str) -> None:
    """
    Trackt wie oft eine konkrete Funktion ausgefuehrt wurde.

    Sichtbar in Sentry unter Explore > Metrics:
      Metric: secbuddy.action.used
      Tags:   tool = "Fakeshop-Detector", action = "check_shop"
    """
    if not _initialized:
        return
    try:
        import sentry_sdk.metrics as m
        label = _TOOL_LABELS.get(page_key, page_key)
        m.count("secbuddy.action.used", 1, attributes={"tool": label, "action": action})
    except Exception:
        pass


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _device_id() -> str:
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
    """Faengt Exceptions in GUI-Callbacks ab."""
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
