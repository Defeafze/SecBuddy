"""
virustotal.py — Asynchrone URL-Prüfung via VirusTotal API v3.

Ablauf:
  1. Versuche einen gecachten Report abzurufen (GET /urls/{id}).
  2. Falls kein Cache (404): URL einreichen (POST /urls) und auf Ergebnis warten.
  3. Polling bis max. 3 × 5 s = 15 s; danach Timeout-Meldung.

Kostenloses Kontingent: 4 Anfragen/Minute, 500 Anfragen/Tag.
"""

import base64
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class VTResult:
    """Zusammengefasstes Ergebnis einer VirusTotal-URL-Prüfung."""
    malicious:   int = 0   # Anzahl Engines, die die URL als bösartig eingestuft haben
    suspicious:  int = 0   # Anzahl Engines mit Verdachtseinstufung
    harmless:    int = 0   # Anzahl Engines, die die URL als sicher einstufen
    undetected:  int = 0   # Anzahl Engines ohne Befund
    total:       int = 0   # Gesamtanzahl beteiligter Engines
    error: Optional[str] = None   # Fehlermeldung, falls Check nicht möglich


_BASE = "https://www.virustotal.com/api/v3"

# Maximale Polling-Versuche und Pause zwischen ihnen (in Sekunden)
_MAX_POLLS   = 3
_POLL_SLEEP  = 5


def _url_id(url: str) -> str:
    """
    Berechnet die VirusTotal-URL-ID: URL-safe Base64 ohne Padding.
    Das ist der Schlüssel, unter dem VT gecachte Reports speichert.
    """
    return base64.urlsafe_b64encode(url.encode()).rstrip(b"=").decode()


def _parse_stats(stats: dict) -> VTResult:
    """Wandelt ein VT-Stats-Dict in ein VTResult um."""
    return VTResult(
        malicious=stats.get("malicious",  0),
        suspicious=stats.get("suspicious", 0),
        harmless=stats.get("harmless",   0),
        undetected=stats.get("undetected", 0),
        total=sum(stats.values()),
    )


def check_url_async(
    url: str,
    api_key: str,
    callback: Callable[[VTResult], None],
) -> None:
    """
    Prüft `url` asynchron mit VirusTotal.
    Ruft `callback(result)` im Hintergrund-Thread auf — GUI-Updates via .after(0, ...).
    """
    def _run() -> None:
        import requests
        # URL normalisieren (Schema für VT-ID-Berechnung benötigt)
        target = url.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        headers = {"x-apikey": api_key, "Accept": "application/json"}

        # ── Phase A: gecachten Report abrufen ────────────────────────────────
        try:
            cached = requests.get(
                f"{_BASE}/urls/{_url_id(target)}",
                headers=headers,
                timeout=10,
            )
        except requests.Timeout:
            callback(VTResult(error="Zeitüberschreitung beim Abruf."))
            return
        except requests.ConnectionError:
            callback(VTResult(error="Keine Verbindung — Internetverbindung prüfen."))
            return
        except Exception as exc:
            callback(VTResult(error=str(exc)))
            return

        if cached.status_code == 401:
            callback(VTResult(error="VirusTotal API Key ungültig oder abgelaufen."))
            return
        if cached.status_code == 429:
            callback(VTResult(error="Rate-Limit erreicht (4 Anfragen/Minute). Kurz warten und erneut versuchen."))
            return

        if cached.status_code == 200:
            # Cache-Treffer: letzten Report zurückgeben
            try:
                stats = cached.json()["data"]["attributes"]["last_analysis_stats"]
                callback(_parse_stats(stats))
            except Exception as exc:
                callback(VTResult(error=f"Antwort nicht lesbar: {exc}"))
            return

        # ── Phase B: URL zum Scan einreichen (kein Cache-Treffer) ────────────
        try:
            submit = requests.post(
                f"{_BASE}/urls",
                headers=headers,
                data={"url": target},   # VT erwartet Form-Data, kein JSON
                timeout=10,
            )
        except Exception as exc:
            callback(VTResult(error=f"Einreichen fehlgeschlagen: {exc}"))
            return

        if submit.status_code != 200:
            callback(VTResult(error=f"Einreichen fehlgeschlagen (HTTP {submit.status_code})."))
            return

        try:
            analysis_id = submit.json()["data"]["id"]
        except Exception:
            callback(VTResult(error="Analyse-ID nicht lesbar."))
            return

        # ── Phase C: Polling bis Scan abgeschlossen ───────────────────────────
        for attempt in range(_MAX_POLLS):
            time.sleep(_POLL_SLEEP)
            try:
                poll = requests.get(
                    f"{_BASE}/analyses/{analysis_id}",
                    headers=headers,
                    timeout=10,
                )
            except Exception as exc:
                callback(VTResult(error=f"Polling-Fehler: {exc}"))
                return

            if poll.status_code != 200:
                continue

            try:
                attrs = poll.json()["data"]["attributes"]
            except Exception:
                continue

            if attrs.get("status") == "completed":
                callback(_parse_stats(attrs["stats"]))
                return

        # Nach _MAX_POLLS immer noch nicht fertig
        callback(VTResult(error="Scan läuft noch — bitte in wenigen Minuten erneut prüfen."))

    threading.Thread(target=_run, daemon=True).start()
