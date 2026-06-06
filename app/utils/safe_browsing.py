"""
safe_browsing.py — Asynchrone Abfrage der Google Safe Browsing API v4.

Prüft eine URL gegen Googles Datenbank mit Milliarden bekannter Bedrohungen.
Die URL wird dabei an Google-Server gesendet — das ist für diesen Check bewusst so.

Dokumentation: https://developers.google.com/safe-browsing/v4/lookup-api
"""

import threading
from typing import Callable, List, Optional
from dataclasses import dataclass, field


# ── Bedrohungstypen auf deutsch ───────────────────────────────────────────────

# Mapping von Google-internem Typ → (Icon, Deutscher Titel, Erklärung für Nutzer)
THREAT_LABELS: dict = {
    "MALWARE": (
        "🦠",
        "Malware",
        "Diese Seite ist dafür bekannt, Schadsoftware zu verbreiten. "
        "Schadsoftware kann deinen Computer oder dein Handy infizieren und beschädigen.",
    ),
    "SOCIAL_ENGINEERING": (
        "🎣",
        "Phishing / Social Engineering",
        "Diese Seite versucht, dich zu täuschen — z. B. als gefälschte Bank- oder "
        "Login-Seite. Gib hier niemals Passwörter, PINs oder andere Daten ein.",
    ),
    "UNWANTED_SOFTWARE": (
        "⚠️",
        "Unerwünschte Software",
        "Diese Seite verbreitet Software, die ohne dein volles Wissen installiert wird. "
        "Solche Programme sind oft schwer wieder zu entfernen.",
    ),
    "POTENTIALLY_HARMFUL_APPLICATION": (
        "⚠️",
        "Potenziell schädliche App",
        "Diese Seite bietet Apps an, die schädliches Verhalten zeigen können.",
    ),
}


@dataclass
class ThreatMatch:
    """Repräsentiert eine einzelne Bedrohung, die für die geprüfte URL gefunden wurde."""
    threat_type: str          # z. B. "SOCIAL_ENGINEERING"
    platform_type: str        # z. B. "ANY_PLATFORM"
    icon:  str  = field(default="⚠️")
    title: str  = field(default="Bedrohung")
    detail: str = field(default="")

    def __post_init__(self) -> None:
        if self.threat_type in THREAT_LABELS:
            self.icon, self.title, self.detail = THREAT_LABELS[self.threat_type]


@dataclass
class SafeBrowsingResult:
    """Gesamtergebnis einer Safe-Browsing-Prüfung."""
    is_safe: bool
    matches: List[ThreatMatch] = field(default_factory=list)
    error:   Optional[str]     = None


# ── API-Abfrage ───────────────────────────────────────────────────────────────

_API_ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

# Alle Bedrohungstypen, die wir abfragen wollen
_THREAT_TYPES = [
    "MALWARE",
    "SOCIAL_ENGINEERING",
    "UNWANTED_SOFTWARE",
    "POTENTIALLY_HARMFUL_APPLICATION",
]


def check_url_async(
    url: str,
    api_key: str,
    callback: Callable[[SafeBrowsingResult], None],
) -> None:
    """
    Prüft `url` asynchron gegen die Google Safe Browsing API.
    Ruft `callback(result)` im Hintergrund-Thread auf — GUI-Updates
    müssen über .after(0, ...) in den Haupt-Thread delegiert werden.
    """
    def _run() -> None:
        import requests
        # URL normalisieren: Schema hinzufügen wenn nötig
        target = url.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        payload = {
            "client": {
                "clientId":      "secbuddy",
                "clientVersion": "1.0",
            },
            "threatInfo": {
                "threatTypes":      _THREAT_TYPES,
                "platformTypes":    ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries":    [{"url": target}],
            },
        }

        try:
            resp = requests.post(
                _API_ENDPOINT,
                params={"key": api_key},
                json=payload,
                timeout=10,
            )

            # Fehlerhafte API-Keys liefern 400 oder 403
            if resp.status_code == 400:
                callback(SafeBrowsingResult(False, error="Ungültige Anfrage — prüfe den API Key."))
                return
            if resp.status_code == 403:
                callback(SafeBrowsingResult(False, error="API Key ungültig oder nicht für Safe Browsing freigeschaltet."))
                return

            resp.raise_for_status()
            data = resp.json()

            # Leere Antwort = keine Bedrohung gefunden
            raw_matches = data.get("matches", [])
            if not raw_matches:
                callback(SafeBrowsingResult(is_safe=True))
                return

            # Gefundene Bedrohungen in ThreatMatch-Objekte umwandeln
            matches = [
                ThreatMatch(
                    threat_type=m.get("threatType", "UNKNOWN"),
                    platform_type=m.get("platformType", ""),
                )
                for m in raw_matches
            ]
            callback(SafeBrowsingResult(is_safe=False, matches=matches))

        except requests.Timeout:
            callback(SafeBrowsingResult(False, error="Zeitüberschreitung — Internetverbindung prüfen."))
        except requests.ConnectionError:
            callback(SafeBrowsingResult(False, error="Keine Verbindung — Internetverbindung prüfen."))
        except Exception as exc:
            callback(SafeBrowsingResult(False, error=f"Unerwarteter Fehler: {exc}"))

    threading.Thread(target=_run, daemon=True).start()
