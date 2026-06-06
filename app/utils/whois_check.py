"""
whois_check.py — Asynchrone WHOIS-Abfrage zur Domain-Altersbestimmung.

Läuft in einem Hintergrund-Thread, damit die UI während der Netzwerkanfrage
nicht einfriert. Das Ergebnis wird per Callback als Liste von Findings zurückgegeben.
"""

import threading
import datetime
from typing import Callable, List, Optional, Tuple
from app.utils.fakeshop_analyzer import Finding


def check_domain_age_async(
    domain: str,
    callback: Callable[[List[Finding], Optional[str]], None],
) -> None:
    """
    Fragt WHOIS-Daten für `domain` ab und liefert Findings per Callback.

    callback(findings, fehlertext_oder_None)

    Wird immer auf einem Hintergrund-Thread aufgerufen — der Aufrufer muss
    sicherstellen, dass GUI-Updates über .after(0, ...) in den Haupt-Thread
    delegiert werden.
    """
    def _run() -> None:
        try:
            import whois  # python-whois, nur bei Bedarf importieren
        except ImportError:
            callback([], "python-whois nicht installiert (pip install python-whois).")
            return

        try:
            data = whois.whois(domain)
        except Exception as exc:
            # WHOIS-Server nicht erreichbar, Rate-Limit, unbekannte TLD, etc.
            callback([], f"WHOIS nicht verfügbar: {exc}")
            return

        findings: List[Finding] = []

        # ── Erstellungsdatum ─────────────────────────────────────────────────
        # python-whois gibt manchmal eine Liste zurück (bei mehreren Einträgen).
        # Wir nehmen das früheste Datum, um das echte Registrierungsdatum zu bekommen.
        creation = data.creation_date
        if isinstance(creation, list):
            creation = min(creation)

        if creation is None:
            # Manche TLDs oder Privacy-Shield-Dienste verbergen das Datum.
            findings.append(Finding(
                "low",
                "Domain-Alter: Keine Daten verfügbar",
                "Das Registrierungsdatum dieser Domain ist nicht öffentlich einsehbar. "
                "Einige Domain-Endungen und Privacy-Dienste verstecken diese Informationen.",
            ))
        else:
            # Timezone-aware zu naive datetime konvertieren, damit der Vergleich klappt
            if getattr(creation, "tzinfo", None) is not None:
                creation = creation.replace(tzinfo=None)

            now       = datetime.datetime.now()
            age_days  = (now - creation).days
            age_label = _format_age(age_days)

            if age_days < 90:
                # Unter 3 Monate — extrem verdächtig
                findings.append(Finding(
                    "high",
                    f"Domain ist erst {age_label} alt",
                    "Diese Domain wurde erst vor sehr kurzer Zeit registriert. "
                    "Fake-Shops entstehen kurzfristig und verschwinden schnell wieder — "
                    "eine sehr neue Domain ist ein starkes Warnsignal.",
                ))
            elif age_days < 365:
                # 3–12 Monate
                findings.append(Finding(
                    "medium",
                    f"Domain ist erst {age_label} alt",
                    f"Die Domain existiert erst seit ca. {age_label}. "
                    "Seriöse Shops sind in der Regel deutlich länger online.",
                ))
            elif age_days < 730:
                # 1–2 Jahre
                findings.append(Finding(
                    "low",
                    f"Domain ist ca. {age_label} alt",
                    "Die Domain ist noch relativ jung. Das ist allein kein sicheres Zeichen, "
                    "aber zusammen mit anderen Warnsignalen relevant.",
                ))
            else:
                # Über 2 Jahre — gutes Zeichen
                findings.append(Finding(
                    "info",
                    f"Domain seit ca. {age_label} registriert",
                    "Eine ältere Domain ist ein gutes Zeichen. "
                    "Die meisten Fake-Shops verschwinden innerhalb von ein bis zwei Jahren.",
                ))

            # ── Registrierungsdauer ──────────────────────────────────────────
            # Nur für 1 Jahr registriert = typisch für kurzlebige Fake-Shops.
            # Seriöse Shops wählen oft 2–5 Jahre im Voraus.
            expiry = data.expiration_date
            if isinstance(expiry, list):
                expiry = max(expiry)  # Spätestes Ablaufdatum nehmen
            if expiry is not None:
                if getattr(expiry, "tzinfo", None) is not None:
                    expiry = expiry.replace(tzinfo=None)
                total_years = (expiry - creation).days / 365
                if total_years < 1.1:
                    findings.append(Finding(
                        "low",
                        "Nur für 1 Jahr registriert",
                        "Diese Domain wurde nur für ein Jahr angemeldet. "
                        "Seriöse Shops registrieren ihre Domain meist mehrere Jahre im Voraus — "
                        "ein kurzfristig angemeldeter Shop ist öfter betrügerisch.",
                    ))

        # ── Registrar ────────────────────────────────────────────────────────
        # Nur als Info — kein Warnsignal, aber nützlich zur manuellen Nachprüfung.
        registrar = data.registrar
        if registrar and isinstance(registrar, str) and registrar.strip():
            findings.append(Finding(
                "info",
                f"Registriert bei: {registrar.strip()}",
                "Das ist das Unternehmen, bei dem die Domain angemeldet wurde. "
                "Diese Information allein sagt wenig aus, kann aber bei weiterer Recherche helfen.",
            ))

        callback(findings, None)

    threading.Thread(target=_run, daemon=True).start()


def _format_age(days: int) -> str:
    """Gibt ein lesbares Alter zurück: '45 Tagen', '8 Monaten', '3 Jahren'."""
    if days < 31:
        return f"{days} Tagen"
    if days < 365:
        months = days // 30
        return f"{months} Monat{'en' if months != 1 else ''}"
    years = days // 365
    return f"{years} Jahr{'en' if years != 1 else ''}"
