"""
impressum_check.py — Prüft ob ein Online-Shop gesetzliche Pflichtseiten hat.

Pflichtseiten nach deutschem Recht:
  - Impressum         (§ 5 TMG)
  - Datenschutz       (DSGVO Art. 13/14)
  - AGB               (empfohlen / marktüblich)
  - Widerrufsbelehrung (§ 355 BGB, B2C-Shops)

Läuft im Hintergrund-Thread (Timeout 8 s pro Request).
"""

import re
import threading
from typing import Callable, List, Optional
from urllib.parse import urljoin
from app.utils.fakeshop_analyzer import Finding


_TIMEOUT = 8
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SecBuddy-SafetyCheck/1.0)"}

# Jeder Eintrag: (key, regex-patterns-in-html, severity, titel, detail)
_REQUIRED_PAGES = [
    (
        "impressum",
        [r"impressum"],
        "high",
        "Kein Impressum gefunden",
        (
            "In Deutschland ist ein Impressum für alle gewerblichen Webseiten Pflicht (§ 5 TMG). "
            "Fehlt ein Link dazu auf der Startseite, verbirgt der Betreiber möglicherweise "
            "seine Identität — ein klares Warnsignal."
        ),
    ),
    (
        "datenschutz",
        [r"datenschutz", r"privacy[\s_-]?policy"],
        "high",
        "Keine Datenschutzerklärung gefunden",
        (
            "Seit der DSGVO 2018 ist eine Datenschutzerklärung für jeden Online-Shop Pflicht. "
            "Fehlt der Link auf der Startseite, nimmt der Betreiber es mit dem Datenschutz "
            "und dem Gesetz nicht ernst."
        ),
    ),
    (
        "agb",
        [r"\bagb\b", r"allgemeine.geschäftsbedingung", r"terms[\s_-]?(and[\s_-])?conditions"],
        "medium",
        "Keine AGB gefunden",
        (
            "Allgemeine Geschäftsbedingungen definieren deine Rechte als Käufer. "
            "Fehlen sie, gibt es keine klare Grundlage bei Problemen mit deiner Bestellung."
        ),
    ),
    (
        "widerruf",
        [r"widerruf"],
        "medium",
        "Keine Widerrufsbelehrung gefunden",
        (
            "Online-Shops müssen über das gesetzliche 14-tägige Widerrufsrecht informieren (§ 355 BGB). "
            "Fehlt dieser Hinweis, könnte der Shop versuchen, Rückgaben und Erstattungen zu verweigern."
        ),
    ),
]

# Regex-Patterns für deutsche Rechtsformen im Impressumstext
_COMPANY_PATTERNS = [
    r"([A-ZÄÖÜ][^<\n]{2,60}?\s+GmbH(?:\s*&\s*Co\.?\s*KG)?)",
    r"([A-ZÄÖÜ][^<\n]{2,60}?\s+AG\b)",
    r"([A-ZÄÖÜ][^<\n]{2,60}?\s+UG\s*\(haftungsbeschränkt\))",
    r"([A-ZÄÖÜ][^<\n]{2,60}?\s+e\.?\s*K\.?\b)",
    r"([A-ZÄÖÜ][^<\n]{2,60}?\s+OHG\b)",
    r"([A-ZÄÖÜ][^<\n]{2,60}?\s+KG\b)",
    r"(?i)inhaber[:\s]+([^\n<,]{4,60})",
]

# Privacy-Shield-Phrasen, die keinen echten Firmennamen darstellen
_PRIVACY_NOISE = re.compile(
    r"(withheld|redacted|privacy|protected|not disclosed|data protected)",
    re.IGNORECASE,
)


def check_legal_pages_async(
    url: str,
    callback: Callable[[List[Finding], Optional[str]], None],
) -> None:
    """
    Prüft die Startseite der URL auf gesetzliche Pflichtseiten.
    Folgt anschließend dem Impressum-Link und sucht nach einem Firmennamen.
    Ergebnis per Callback: callback(findings, fehler_oder_None).
    """
    threading.Thread(target=_run, args=(url, callback), daemon=True).start()


def _run(url: str, callback: Callable) -> None:
    try:
        import requests
    except ImportError:
        callback([], "requests nicht installiert.")
        return

    # ── Startseite abrufen ────────────────────────────────────────────────────
    try:
        resp = requests.get(url, timeout=_TIMEOUT, headers=_HEADERS,
                            allow_redirects=True, verify=False)
        html_lower = resp.text.lower()
        html_orig  = resp.text
    except Exception as exc:
        callback([], f"Seite nicht erreichbar: {exc}")
        return

    findings: List[Finding] = []
    missing: List[str] = []

    # ── Pflichtseiten prüfen ─────────────────────────────────────────────────
    for key, patterns, severity, title, detail in _REQUIRED_PAGES:
        found = any(re.search(p, html_lower) for p in patterns)
        if found:
            pass  # Gefunden — kein negatives Finding
        else:
            findings.append(Finding(severity, title, detail))
            missing.append(key)

    found_count = len(_REQUIRED_PAGES) - len(missing)
    if not missing:
        findings.append(Finding(
            "info",
            "Alle Pflichtseiten vorhanden (Impressum, Datenschutz, AGB, Widerruf)",
            "Alle gesetzlich vorgeschriebenen Seiten wurden auf der Startseite verlinkt — "
            "das ist ein gutes Zeichen. Prüfe trotzdem den Inhalt des Impressums manuell.",
        ))
    elif found_count > 0:
        pass  # Einzelne Warnungen wurden schon hinzugefügt

    # ── Firmennamen aus dem Impressum extrahieren ─────────────────────────────
    impressum_url = _find_impressum_url(html_lower, html_orig, url)
    if impressum_url:
        company = _extract_company(impressum_url)
        if company:
            findings.append(Finding(
                "info",
                f"Firma im Impressum: {company}",
                "Im Impressum wurde ein Unternehmensname gefunden. "
                "Prüfe diesen Namen im Handelsregister (handelsregister.de) oder bei Google, "
                "um sicherzustellen, dass das Unternehmen wirklich existiert.",
            ))
        else:
            findings.append(Finding(
                "low",
                "Kein Unternehmensname im Impressum erkannt",
                "Das Impressum enthält keinen eindeutigen Firmennamen (GmbH, AG, UG, usw.). "
                "Lies den Impressumstext manuell durch — fehlen Firmierung und vollständige "
                "Adresse, ist das ein deutliches Warnsignal.",
            ))

    callback(findings, None)


def _find_impressum_url(html_lower: str, html_orig: str, base_url: str) -> Optional[str]:
    """Sucht den href-Wert eines Impressum-Links in der Startseite."""
    # Suche im Original-HTML nach href, der "impressum" enthält
    match = re.search(
        r'href=["\']([^"\']*impressum[^"\']*)["\']',
        html_orig,
        re.IGNORECASE,
    )
    if not match:
        return None
    href = match.group(1).strip()
    if href.startswith("http"):
        return href
    return urljoin(base_url, href)


def _extract_company(impressum_url: str) -> Optional[str]:
    """Fetcht die Impressum-Seite und extrahiert den Firmennamen."""
    try:
        import requests
        resp = requests.get(impressum_url, timeout=_TIMEOUT, headers=_HEADERS,
                            allow_redirects=True, verify=False)
        text = resp.text
    except Exception:
        return None

    # Rohen Text aus HTML extrahieren (Tags entfernen)
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"\s+", " ", plain)

    for pattern in _COMPANY_PATTERNS:
        match = re.search(pattern, plain)
        if match:
            name = match.group(1).strip()
            # Privacy-Shield-Phrasen herausfiltern
            if _PRIVACY_NOISE.search(name):
                continue
            # Zu lange Treffer kürzen
            return name[:80] + "…" if len(name) > 80 else name

    return None
