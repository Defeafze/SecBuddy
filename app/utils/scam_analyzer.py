import re
from urllib.parse import urlparse
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Finding:
    severity: str   # "high" | "medium" | "low" | "info"
    title: str
    detail: str


# ── Konstanten ────────────────────────────────────────────────────────────────

_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "ow.ly", "goo.gl", "short.io",
    "rb.gy", "is.gd", "buff.ly", "ift.tt", "j.mp", "cutt.ly",
    "tiny.cc", "rebrand.ly", "shorturl.at", "lnkd.in",
}

_RISKY_TLDS = {
    ".xyz", ".top", ".click", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".pw", ".cc", ".club", ".online", ".site", ".website", ".live",
    ".download", ".stream", ".racing", ".review", ".trade", ".date",
    ".cricket", ".party", ".faith", ".win", ".loan", ".men", ".bid", ".work",
}

# Marken, die häufig imitiert werden
_BRANDS = [
    ("paypal",          ["paypal.com", "paypal.de"]),
    ("amazon",          ["amazon.de", "amazon.com"]),
    ("ebay",            ["ebay.de", "ebay.com"]),
    ("netflix",         ["netflix.com"]),
    ("apple",           ["apple.com"]),
    ("microsoft",       ["microsoft.com"]),
    ("google",          ["google.com", "google.de"]),
    ("facebook",        ["facebook.com"]),
    ("instagram",       ["instagram.com"]),
    ("dhl",             ["dhl.de", "dhl.com"]),
    ("hermes",          ["myhermes.de", "hermesworld.com"]),
    ("dpd",             ["dpd.de", "dpd.com"]),
    ("ups",             ["ups.com"]),
    ("fedex",           ["fedex.com"]),
    ("sparkasse",       ["sparkasse.de"]),
    ("volksbank",       ["volksbank.de"]),
    ("dkb",             ["dkb.de"]),
    ("ing",             ["ing.de"]),
    ("postbank",        ["postbank.de"]),
    ("commerzbank",     ["commerzbank.de"]),
    ("deutschebank",    ["db.com", "deutsche-bank.de"]),
]

# Zeichen, die andere Zeichen imitieren
_LOOKALIKES = str.maketrans("01345@!", "oieasai")

_URGENCY_PATTERNS = [
    r"sofort", r"dringend", r"unverzüglich", r"innerhalb von \d+",
    r"heute noch", r"jetzt handeln", r"umgehend", r"letzter tag",
    r"läuft ab", r"abläuft", r"frist", r"nur noch \d+",
]
_THREAT_PATTERNS = [
    r"konto (wurde |ist |wird )?gesperrt",
    r"konto (wurde |ist |wird )?blockiert",
    r"polizei", r"strafanzeige", r"gericht", r"klage",
    r"verhaftet", r"illegal", r"inkasso", r"mahnbescheid",
]
_PRIZE_PATTERNS = [
    r"(sie haben|du hast) gewonnen",
    r"gewinnbenachrichtigung", r"lotterie", r"ausgelost",
    r"\d+ (millionen|tausend) euro", r"sonderpreis",
]
_DATA_PATTERNS = [
    r"(ihre?|deine?) (zugangsdaten|passwort|pin|tan|iban|kreditkarte)",
    r"konto bestätigen", r"identität (bestätigen|verifizieren)",
    r"daten (aktualisieren|bestätigen|eingeben)",
    r"klicken sie (auf den link|hier)", r"link folgen",
]
_PACKAGE_PATTERNS = [
    r"(ihr?|dein) paket (konnte|kann) nicht",
    r"sendung (konnte|kann) nicht (zugestellt|geliefert)",
    r"zollgebühr", r"versandkosten (ausstehend|offen|fällig)",
    r"nachnahmebetrag",
]


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    return text.lower().translate(_LOOKALIKES)


def _root_domain(host: str) -> str:
    parts = host.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def _find_any(patterns: List[str], text: str) -> Optional[str]:
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0)
    return None


def _extract_urls(text: str) -> List[str]:
    return re.findall(r'https?://\S+|www\.\S+', text, re.IGNORECASE)


# ── URL-Analyse ───────────────────────────────────────────────────────────────

def analyze_url(raw_url: str) -> List[Finding]:
    findings: List[Finding] = []
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        return [Finding("high", "Ungültiger Link", "Dieser Link hat ein unlesbares Format.")]

    host = parsed.netloc.lower().split(":")[0]
    path = parsed.path.lower() + ("?" + parsed.query.lower() if parsed.query else "")
    root = _root_domain(host)
    root_norm = _norm(root)

    # IP statt Domain
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        findings.append(Finding(
            "high", "IP-Adresse statt Webseitenname",
            "Seriöse Webseiten haben immer einen Namen wie 'bank.de', keine rohe Zahlenkombination."
        ))
        return findings  # Weitere Checks ergeben hier wenig Sinn

    # URL-Kürzel
    if root in _SHORTENERS:
        findings.append(Finding(
            "medium", "Versteckter Link (Kurz-URL)",
            f"'{host}' ist ein Link-Kürzungsdienst — das eigentliche Ziel ist unsichtbar und lässt sich nicht prüfen."
        ))

    # Verdächtige TLD
    tld = "." + host.rsplit(".", 1)[-1]
    if tld in _RISKY_TLDS:
        findings.append(Finding(
            "medium", f"Ungewöhnliche Endung '{tld}'",
            "Diese Domain-Endung wird sehr häufig für Phishing genutzt, weil sie billig oder kostenlos zu haben ist."
        ))

    # Marken-Imitation: Brand im Host, aber Root-Domain ist eine andere
    host_norm = _norm(host)
    for brand, legit_roots in _BRANDS:
        if brand in host_norm:
            if not any(_norm(r) == root_norm for r in legit_roots):
                findings.append(Finding(
                    "high", f"Mögliche Nachahmung von '{brand.title()}'",
                    f"Der Link enthält '{brand}', aber die eigentliche Domain ist '{root}'. "
                    "Betrüger setzen bekannte Namen in Links, um Vertrauen zu wecken."
                ))
                break

    # Markenname im Pfad, aber nicht in der Domain
    path_norm = _norm(path)
    for brand, legit_roots in _BRANDS:
        if brand in path_norm and brand not in root_norm:
            findings.append(Finding(
                "high", f"'{brand.title()}' im Pfad, nicht in der Domain",
                f"Der Begriff '{brand}' steht im Pfad des Links, aber die Domain ist '{root}'. "
                "Klassische Phishing-Taktik: der echte Firmenname taucht erst nach dem '/' auf."
            ))
            break

    # Viele Subdomains (z. B. login.paypal.com.evil.ru)
    if len(host.split(".")) >= 4:
        findings.append(Finding(
            "medium", "Verschachtelter Domainname",
            f"'{host}' hat ungewöhnlich viele Ebenen. Betrüger verstecken so oft einen bekannten Namen vor dem echten Ziel."
        ))

    # Kein HTTPS
    if parsed.scheme == "http":
        findings.append(Finding(
            "low", "Keine Verschlüsselung (HTTP)",
            "Seriöse Seiten nutzen fast immer HTTPS. Bei Seiten, wo du Daten eingibst, ist HTTP ein Warnsignal."
        ))

    # Ungewöhnlicher Port
    port_match = re.search(r":(\d+)$", parsed.netloc)
    if port_match and port_match.group(1) not in ("80", "443"):
        findings.append(Finding(
            "medium", f"Ungewöhnlicher Port :{port_match.group(1)}",
            "Normale Webseiten laufen auf Standardports. Ein anderer Port kann auf eine getarnte Seite hinweisen."
        ))

    # Sehr langer Link
    if len(raw_url) > 200:
        findings.append(Finding(
            "low", "Ungewöhnlich langer Link",
            "Sehr lange Links sollen oft das eigentliche Ziel in einem Wust aus Zeichen verstecken."
        ))

    return findings


# ── Text-Analyse ──────────────────────────────────────────────────────────────

def analyze_text(text: str) -> List[Finding]:
    findings: List[Finding] = []
    text_lower = text.lower()

    # Enthaltene URLs analysieren
    urls = _extract_urls(text)
    url_findings: List[Finding] = []
    for url in urls[:3]:
        url_findings.extend(analyze_url(url))
    if url_findings:
        findings.extend(url_findings)
    elif urls:
        findings.append(Finding(
            "low", f"{len(urls)} Link(s) in der Nachricht",
            "Die Nachricht enthält Links — prüfe sie sorgfältig, bevor du klickst."
        ))

    m = _find_any(_THREAT_PATTERNS, text_lower)
    if m:
        findings.append(Finding(
            "high", "Drohungen / Einschüchterung",
            f'Formulierungen wie "{m}" sollen Panik auslösen. Das ist ein klassisches Betrugs-Muster.'
        ))

    m = _find_any(_PRIZE_PATTERNS, text_lower)
    if m:
        findings.append(Finding(
            "high", "Gewinnversprechen",
            f'Niemand verschenkt spontan Geld oder Preise. "{m}" — solche Nachrichten sind fast immer Betrug.'
        ))

    m = _find_any(_DATA_PATTERNS, text_lower)
    if m:
        findings.append(Finding(
            "high", "Aufforderung zur Dateneingabe",
            "Kein seriöses Unternehmen fragt per SMS oder E-Mail nach Passwort, PIN oder TAN."
        ))

    m = _find_any(_URGENCY_PATTERNS, text_lower)
    if m:
        findings.append(Finding(
            "medium", "Künstlicher Zeitdruck",
            f'"{m}" soll dich zu schnellen, unüberlegten Aktionen verleiten. Nimm dir die Zeit zu prüfen.'
        ))

    m = _find_any(_PACKAGE_PATTERNS, text_lower)
    if m:
        findings.append(Finding(
            "medium", "Paket-Betrugsmasche",
            "Nachrichten über nicht zustellbare Pakete gehören zu den häufigsten Betrugsmaschen. "
            "Prüfe dein Paket direkt auf der offiziellen Website des Paketdienstes — nie über den Link in der Nachricht."
        ))

    return findings


# ── Gesamtrisiko ──────────────────────────────────────────────────────────────

def overall_risk(findings: List[Finding]):
    """Returns (label, color, progress 0.0–1.0)."""
    if not findings:
        return "Nichts Verdächtiges gefunden", "#22c55e", 0.08

    high   = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")

    if high >= 2:
        return "Sehr hohes Risiko",  "#ef4444", 1.0
    if high == 1:
        return "Hohes Risiko",       "#f97316", 0.75
    if medium >= 2:
        return "Mittleres Risiko",   "#f59e0b", 0.50
    if medium == 1:
        return "Geringes Risiko",    "#eab308", 0.30
    return     "Kaum Risiko",        "#22c55e", 0.12
