"""
whois_check.py — WHOIS-Abfrage via Raw-Socket (kein pip install nötig).

Verbindet sich direkt über TCP Port 43 mit dem zuständigen WHOIS-Server
und parst Erstellungsdatum, Ablaufdatum und Registrant-Infos via Regex.
"""

import re
import socket
import threading
import datetime
from typing import Callable, List, Optional
from app.utils.fakeshop_analyzer import Finding


_TIMEOUT = 6  # Sekunden pro Socket-Verbindung

# Bekannte WHOIS-Server pro TLD (kein IANA-Lookup nötig)
_TLD_SERVERS = {
    "com":     "whois.verisign-grs.com",
    "net":     "whois.verisign-grs.com",
    "org":     "whois.pir.org",
    "de":      "whois.denic.de",
    "eu":      "whois.eu",
    "at":      "whois.nic.at",
    "ch":      "whois.nic.ch",
    "uk":      "whois.nic.uk",
    "co.uk":   "whois.nic.uk",
    "co":      "whois.nic.co",
    "fr":      "whois.nic.fr",
    "nl":      "whois.sidn.nl",
    "io":      "whois.nic.io",
    "info":    "whois.afilias.net",
    "biz":     "whois.biz",
    "xyz":     "whois.nic.xyz",
    "top":     "whois.nic.top",
    "online":  "whois.nic.online",
    "site":    "whois.nic.site",
    "shop":    "whois.nic.shop",
    "club":    "whois.nic.club",
    "live":    "whois.nic.live",
    "store":   "whois.nic.store",
    "pw":      "whois.nic.pw",
    "cc":      "whois.nic.cc",
    "click":   "whois.uniregistry.net",
    "in":      "whois.registry.in",
    "us":      "whois.nic.us",
    "ca":      "whois.cira.ca",
    "es":      "whois.nic.es",
    "it":      "whois.nic.it",
    "pl":      "whois.dns.pl",
    "ru":      "whois.tcinet.ru",
    "au":      "whois.auda.org.au",
    "tk":      "whois.dot.tk",
    "ml":      "whois.dot.ml",
    "ga":      "whois.dot.ga",
    "cf":      "whois.dot.cf",
    "gq":      "whois.dot.gq",
    "icu":     "whois.nic.icu",
    "win":     "whois.nic.win",
}

_CREATION_RE = re.compile(
    r"(?:creation date|created(?:\s+on)?|registered(?:\s+on)?|"
    r"registration time|domain registration date|registered)"
    r"[:\s]+([0-9T:\.\-\/Z+ ]+)",
    re.IGNORECASE,
)
_EXPIRY_RE = re.compile(
    r"(?:expir(?:y|ation|es)(?:\s+date)?|registry expiry date|paid-till|renewal date)"
    r"[:\s]+([0-9T:\.\-\/Z+ ]+)",
    re.IGNORECASE,
)
_ORG_RE = re.compile(
    r"(?:organisation|registrant\s+org(?:anization)?|^org)[:\s]+(.+)",
    re.IGNORECASE | re.MULTILINE,
)
_REGISTRAR_RE = re.compile(
    r"^registrar[:\s]+(.+)",
    re.IGNORECASE | re.MULTILINE,
)
_PRIVACY_NOISE = (
    "withheld", "redacted", "privacy", "protected",
    "not disclosed", "whoisguard", "contact privacy", "data masked",
)
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


# ── Öffentliche API ───────────────────────────────────────────────────────────

def check_domain_age_async(
    domain: str,
    callback: Callable[[List[Finding], Optional[str]], None],
) -> None:
    """
    Fragt WHOIS-Daten für `domain` ab und liefert Findings per Callback.
    callback(findings, fehlertext_oder_None)
    Läuft immer auf einem Hintergrund-Thread.
    """
    threading.Thread(target=_run, args=(domain, callback), daemon=True).start()


# ── Interne Logik ─────────────────────────────────────────────────────────────

def _run(domain: str, callback: Callable) -> None:
    tld    = _get_tld(domain)
    server = _TLD_SERVERS.get(tld) or _iana_lookup(tld)
    if not server:
        callback([], f"Kein WHOIS-Server für '.{tld}' bekannt.")
        return

    raw = _query(server, domain)
    if not raw:
        # Manche Server brauchen ein Präfix; Verisign akzeptiert "=domain"
        raw = _query(server, f"={domain}")
    if not raw:
        callback([], "WHOIS-Server hat nicht geantwortet.")
        return

    findings: List[Finding] = []

    # ── Erstellungsdatum ─────────────────────────────────────────────────────
    creation = _find_date(raw, _CREATION_RE)

    if creation is None:
        # DENIC (.de) veröffentlicht das Erstellungsdatum nicht — nur Hinweis
        if tld == "de":
            findings.append(Finding(
                "info",
                "Domain-Alter nicht einsehbar (.de / DENIC-Datenschutz)",
                "DENIC veröffentlicht das Erstellungsdatum für .de-Domains grundsätzlich nicht. "
                "Prüfe das Alter alternativ über sitelike.org oder domaintools.com.",
            ))
        else:
            findings.append(Finding(
                "low",
                "Erstellungsdatum nicht einsehbar",
                "Das Registrierungsdatum dieser Domain ist nicht öffentlich. "
                "Manche TLDs oder Privacy-Dienste verstecken diese Information.",
            ))
    else:
        now      = datetime.datetime.now()
        age_days = max((now - creation).days, 0)
        age_lbl  = _format_age(age_days)

        if age_days < 90:
            findings.append(Finding(
                "high",
                f"Domain ist erst {age_lbl} alt",
                "Diese Domain wurde erst vor sehr kurzer Zeit registriert. "
                "Fake-Shops entstehen kurzfristig und verschwinden schnell — "
                "eine sehr neue Domain ist ein starkes Warnsignal.",
            ))
        elif age_days < 365:
            findings.append(Finding(
                "medium",
                f"Domain ist erst {age_lbl} alt",
                f"Die Domain existiert erst seit ca. {age_lbl}. "
                "Seriöse Shops sind in der Regel deutlich länger online.",
            ))
        elif age_days < 730:
            findings.append(Finding(
                "low",
                f"Domain ist ca. {age_lbl} alt",
                "Die Domain ist noch relativ jung. Allein kein sicheres Zeichen, "
                "aber zusammen mit anderen Warnsignalen relevant.",
            ))
        else:
            findings.append(Finding(
                "info",
                f"Domain seit ca. {age_lbl} registriert",
                "Eine ältere Domain ist ein gutes Zeichen. "
                "Die meisten Fake-Shops verschwinden innerhalb von ein bis zwei Jahren.",
            ))

        # Nur 1 Jahr registriert?
        expiry = _find_date(raw, _EXPIRY_RE)
        if expiry is not None:
            total_years = (expiry - creation).days / 365
            if total_years < 1.1:
                findings.append(Finding(
                    "low",
                    "Nur für 1 Jahr registriert",
                    "Diese Domain wurde nur für ein Jahr angemeldet. "
                    "Seriöse Shops registrieren ihre Domain meist mehrere Jahre im Voraus.",
                ))

    # ── Registrant-Organisation ──────────────────────────────────────────────
    org = _first_match(raw, _ORG_RE)
    if org and not any(p in org.lower() for p in _PRIVACY_NOISE):
        findings.append(Finding(
            "info",
            f"Registriert auf: {org[:80]}",
            "Der Domain-Inhaber ist im WHOIS eingetragen. "
            "Prüfe diesen Namen im Handelsregister (handelsregister.de) oder bei Google.",
        ))
    else:
        findings.append(Finding(
            "low",
            "Domain-Inhaber verborgen (Privacy-Shield)",
            "Der Registrant hat seine Identität mit einem Privacy-Dienst versteckt. "
            "Allein kein Betrugszeichen, erschwert aber die Rückverfolgung.",
        ))

    # ── Registrar ────────────────────────────────────────────────────────────
    registrar = _first_match(raw, _REGISTRAR_RE)
    if registrar:
        findings.append(Finding(
            "info",
            f"Domain-Registrar: {registrar[:80]}",
            "Das Unternehmen, bei dem die Domain angemeldet wurde. "
            "Nützlich für weitere manuelle Recherche.",
        ))

    callback(findings, None)


# ── Socket-Hilfsfunktionen ────────────────────────────────────────────────────

def _query(server: str, domain: str) -> str:
    """Stellt eine WHOIS-Abfrage via TCP Port 43 und gibt die rohe Antwort zurück."""
    try:
        with socket.create_connection((server, 43), timeout=_TIMEOUT) as s:
            s.sendall((domain + "\r\n").encode("utf-8", errors="replace"))
            chunks = []
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk.decode("utf-8", errors="replace"))
            return "".join(chunks)
    except Exception:
        return ""


def _iana_lookup(tld: str) -> Optional[str]:
    """Fragt whois.iana.org nach dem zuständigen WHOIS-Server für eine unbekannte TLD."""
    resp = _query("whois.iana.org", tld)
    for line in resp.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("whois:"):
            server = stripped.split(":", 1)[1].strip()
            return server if server else None
    return None


def _get_tld(domain: str) -> str:
    """Gibt die TLD eines Domain-Namens zurück, z. B. 'de' aus 'shop.example.de'."""
    parts = domain.lower().rstrip(".").split(".")
    # Zweistufige TLDs (co.uk, co.at, …) erkennen
    if len(parts) >= 3:
        two = ".".join(parts[-2:])
        if two in _TLD_SERVERS:
            return two
    return parts[-1] if parts else ""


# ── Parsing-Hilfsfunktionen ───────────────────────────────────────────────────

def _find_date(raw: str, pattern: re.Pattern) -> Optional[datetime.datetime]:
    """Sucht das erste Datum im WHOIS-Text und parst es."""
    m = pattern.search(raw)
    if not m:
        return None
    return _parse_date(m.group(1).strip())


def _parse_date(raw: str) -> Optional[datetime.datetime]:
    """Parst ein Datum in verschiedenen WHOIS-Formaten."""
    if not raw:
        return None
    raw = raw.split()[0].rstrip(".")
    # Timezone-Suffix entfernen: +02:00 / +0200 (Stunden 00–14, nie Jahreszahlen)
    clean = re.sub(r"[+-](?:0\d|1[0-4]):?\d{2}$", "", raw).rstrip("Z").strip()

    # (Format, erwartete Datenlänge) — len(fmt) != Datenlänge wegen %Y/%m/%d etc.
    for fmt, length in [
        ("%Y-%m-%dT%H:%M:%S", 19),
        ("%Y-%m-%d",          10),
        ("%Y/%m/%d",          10),
        ("%Y%m%d",             8),
        ("%d.%m.%Y",          10),
    ]:
        try:
            return datetime.datetime.strptime(clean[:length], fmt)
        except (ValueError, IndexError):
            continue

    # "15-Jan-2023"
    m = re.match(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})", clean)
    if m:
        day, mon, year = m.groups()
        mo = _MONTH_MAP.get(mon.lower())
        if mo:
            try:
                return datetime.datetime(int(year), mo, int(day))
            except ValueError:
                pass
    return None


def _first_match(raw: str, pattern: re.Pattern) -> str:
    """Gibt den ersten nicht-leeren Treffer einer Gruppe zurück."""
    m = pattern.search(raw)
    if not m:
        return ""
    val = m.group(1).strip()
    # Überlange oder offensichtlich ungültige Werte ignorieren
    return val if val and len(val) < 120 else ""


def _format_age(days: int) -> str:
    if days < 31:
        return f"{days} Tagen"
    if days < 365:
        months = days // 30
        return f"{months} Monat{'en' if months != 1 else ''}"
    years = days // 365
    return f"{years} Jahr{'en' if years != 1 else ''}"
