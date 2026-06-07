"""
fakeshop_analyzer.py — Heuristische Fake-Shop-Erkennung.

Alle Prüfungen laufen vollständig lokal, ohne externe APIs.
Das bedeutet: Keine Daten verlassen das Gerät. Das Ergebnis ist ein
Hinweis, keine Garantie — sowohl False Positives als auch False Negatives
sind möglich.
"""

import re
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Finding:
    """Ein einzelner Befund mit Schweregrad, Titel und Erklärung für den Nutzer."""
    severity: str   # "high" | "medium" | "low" | "info"
    title: str
    detail: str


# ── Datenbasis ────────────────────────────────────────────────────────────────

# TLDs, die bei Fake-Shops überproportional häufig vorkommen, weil sie
# kostenlos oder für wenige Cent registrierbar sind.
_RISKY_TLDS = {
    ".xyz", ".top", ".click", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".pw", ".cc", ".club", ".online", ".site", ".website", ".live",
    ".download", ".stream", ".racing", ".review", ".trade", ".date",
    ".cricket", ".party", ".faith", ".win", ".loan", ".men", ".bid", ".icu",
}

# Bekannte Marken, die von Fake-Shops am häufigsten nachgeahmt werden.
# Pro Marke sind die einzigen legitimen Root-Domains aufgeführt.
_BRANDS: List[Tuple[str, List[str]]] = [
    ("adidas",        ["adidas.de",       "adidas.com"]),
    ("nike",          ["nike.de",          "nike.com"]),
    ("puma",          ["puma.de",          "puma.com"]),
    ("zara",          ["zara.de",          "zara.com",        "zara.es"]),
    ("primark",       ["primark.de",       "primark.com"]),
    ("amazon",        ["amazon.de",        "amazon.com"]),
    ("ebay",          ["ebay.de",          "ebay.com"]),
    ("zalando",       ["zalando.de",       "zalando.com"]),
    ("aboutyou",      ["aboutyou.de",      "aboutyou.com"]),
    ("otto",          ["otto.de"]),
    ("mediamarkt",    ["mediamarkt.de",    "mediamarkt.com"]),
    ("saturn",        ["saturn.de"]),
    ("apple",         ["apple.com"]),
    ("samsung",       ["samsung.de",       "samsung.com"]),
    ("sony",          ["sony.de",          "sony.com"]),
    ("hugoboss",      ["hugoboss.de",      "hugoboss.com"]),
    ("gucci",         ["gucci.com"]),
    ("rolex",         ["rolex.com"]),
    ("louisvuitton",  ["louisvuitton.com"]),
    ("lidl",          ["lidl.de",          "lidl.com"]),
    ("aldi",          ["aldi.de",          "aldi.com",        "aldi-sued.de", "aldi-nord.de"]),
    ("ikea",          ["ikea.de",          "ikea.com"]),
    ("dm",            ["dm.de"]),
    ("rossmann",      ["rossmann.de"]),
    ("paypal",        ["paypal.de",        "paypal.com"]),
    ("rewe",          ["rewe.de"]),
    ("edeka",         ["edeka.de"]),
]

# Wörter, die echte Markenseiten nie im Root-Domainnamen haben,
# aber bei Fake-Shops in Kombination mit Markennamen auftauchen.
# "adidas-outlet.de", "nike-sale-shop.com" — klassische Fake-Shop-Muster.
_FAKESHOP_KEYWORDS = {
    "outlet", "sale", "clearance", "discount", "angebot", "rabatt",
    "guenstig", "billig", "cheap", "wholesale", "factory",
    "official", "original", "authentic", "deals",
    "2023", "2024", "2025",  # Jahreszahlen signalisieren oft "frischer" Fake-Shop
}

# Homoglyphen: Zeichen, die in Domain-Namen andere Zeichen imitieren.
# "0" statt "o", "1" statt "i" usw.
_LOOKALIKES = str.maketrans("01345@!", "oieasai")


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    """Kleinbuchstaben + Homoglyphen ersetzen für Vergleiche."""
    return text.lower().translate(_LOOKALIKES)


def _root_domain(host: str) -> str:
    """
    Extrahiert die Root-Domain aus einem Hostnamen.
    Beispiel: 'shop.adidas-outlet.de' → 'adidas-outlet.de'
    """
    parts = host.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def _root_name(host: str) -> str:
    """
    Gibt den Domain-Namen ohne TLD zurück.
    Beispiel: 'adidas-outlet.de' → 'adidas-outlet'
    """
    parts = host.lower().split(".")
    return parts[-2] if len(parts) >= 2 else host


# ── Hauptanalysefunktion ──────────────────────────────────────────────────────

def analyze_shop_url(raw_url: str) -> List[Finding]:
    """
    Analysiert eine Shop-URL heuristisch auf Fake-Shop-Merkmale.
    Gibt eine Liste von Findings zurück (high/medium/low = Warnsignale, info = Tipps).
    """
    findings: List[Finding] = []
    url = raw_url.strip()

    # Schema ergänzen, damit urlparse die Domain korrekt erkennt
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        return [Finding("high", "Ungültige URL", "Diese Adresse kann nicht als Link erkannt werden.")]

    # Host ohne Port extrahieren, z. B. "adidas-outlet.de" aus "adidas-outlet.de:8080"
    host = parsed.netloc.lower().split(":")[0]
    if not host:
        return [Finding("high", "Kein Domainname erkannt", "Bitte gib eine vollständige Web-Adresse ein.")]

    root      = _root_domain(host)   # "adidas-outlet.de"
    root_norm = _norm(root)          # nach Homoglyphen-Normalisierung
    root_name = _root_name(host)     # "adidas-outlet"
    host_norm = _norm(host)          # ganzer Host normalisiert

    # ── 1. IP-Adresse statt Domainname ───────────────────────────────────────
    # Kein seriöser Online-Shop ist über eine rohe IP-Adresse erreichbar.
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        findings.append(Finding(
            "high",
            "IP-Adresse statt Shop-Adresse",
            "Dieser Link führt zu einer Zahlenkombination statt zu einem echten Domainnamen. "
            "Kein seriöser Online-Shop macht das — das ist ein sehr starkes Warnsignal.",
        ))
        # Weitere Domain-Checks ergeben bei IPs keinen Sinn
        _append_tips(findings)
        return findings

    # ── 2. Kein HTTPS ─────────────────────────────────────────────────────────
    # HTTPS ist für jeden Shop, der Zahlungsdaten verarbeitet, Pflicht.
    # HTTP bedeutet: Deine Daten werden unverschlüsselt übertragen.
    if parsed.scheme == "http":
        findings.append(Finding(
            "high",
            "Keine Verschlüsselung (HTTP statt HTTPS)",
            "Jeder seriöse Online-Shop verschlüsselt seine Verbindung mit HTTPS. "
            "Auf einer HTTP-Seite solltest du niemals Zahlungsdaten eingeben.",
        ))

    # ── 3. Verdächtige TLD ────────────────────────────────────────────────────
    # Diese Domain-Endungen sind kostenlos oder für Cent-Beträge zu registrieren
    # und werden deshalb überproportional häufig für kurzlebige Fake-Shops genutzt.
    tld = "." + host.rsplit(".", 1)[-1]
    if tld in _RISKY_TLDS:
        findings.append(Finding(
            "medium",
            f"Ungewöhnliche Domain-Endung '{tld}'",
            f"Die Endung '{tld}' ist kostenlos oder sehr billig zu registrieren "
            "und wird häufig für kurzlebige Fake-Shops genutzt. "
            "Seriöse deutsche Shops nutzen meist '.de', '.com' oder '.eu'.",
        ))

    # ── 4. Marken-Imitation ───────────────────────────────────────────────────
    # Prüfen ob ein bekannter Markenname in der Domain vorkommt,
    # die Root-Domain aber nicht zur echten Marke gehört.
    # Beispiel: "adidas-outlet.de" enthält "adidas", ist aber nicht "adidas.de".
    for brand, legit_roots in _BRANDS:
        # Markenname ohne Sonderzeichen für robusten Vergleich
        brand_clean = brand.replace(" ", "").replace("-", "")
        host_clean  = host_norm.replace("-", "").replace(".", "")

        if brand_clean in host_clean:
            # Ist die Root-Domain tatsächlich die offizielle Marken-Domain?
            if not any(_norm(r) == root_norm for r in legit_roots):
                findings.append(Finding(
                    "high",
                    f"Mögliche Marken-Imitation: '{brand.title()}'",
                    f"Die Adresse enthält den Markennamen '{brand.title()}', "
                    f"gehört aber nicht zur offiziellen Seite. "
                    "Betrüger setzen bekannte Markennamen in ihre Domain-Adresse, um Vertrauen zu wecken. "
                    f"Die echte Adresse der Marke ist: {legit_roots[0]}",
                ))
                # Nur einen Marken-Treffer pro URL melden — mehrfache Treffer
                # kommen bei kurzen Domains kaum vor und würden verwirren.
                break

    # ── 5. Viele Bindestriche im Domainnamen ─────────────────────────────────
    # Echte Shops haben einfache, einprägsame Domains.
    # "adidas-outlet-sale-shop-2024.de" — viele Bindestriche sind ein typisches
    # Fake-Shop-Muster, weil die einfachen Domains längst vergeben sind.
    hyphen_count = root_name.count("-")
    if hyphen_count >= 3:
        findings.append(Finding(
            "high",
            f"Sehr viele Bindestriche im Domainnamen ({hyphen_count}×)",
            "Seriöse Shops haben einfache, klare Adressen. "
            f"Domains mit vielen Bindestrichen wie '{root}' sind ein typisches Merkmal von Fake-Shops.",
        ))
    elif hyphen_count == 2:
        findings.append(Finding(
            "medium",
            "Mehrere Bindestriche im Domainnamen",
            f"'{root}' enthält mehrere Bindestriche. "
            "Das kommt bei Fake-Shops häufig vor, wenn Betrüger einen bekannten Namen imitieren wollen.",
        ))

    # ── 6. Typische Fake-Shop-Schlüsselwörter in der Domain ──────────────────
    # Wörter wie "outlet", "sale", "original", "authentic" in der Domain
    # sind ein starkes Signal — echte Marken nutzen das nie in ihrer Domain.
    domain_parts = set(re.split(r"[-.]", root_name.lower()))
    matched = domain_parts & _FAKESHOP_KEYWORDS

    # "outlet", "original" etc. sind stärkere Signale als z. B. "sale"
    strong = matched & {"outlet", "original", "authentic", "official", "wholesale", "factory"}
    if strong or len(matched) >= 2:
        word = next(iter(strong or matched))
        findings.append(Finding(
            "medium",
            f"Typisches Fake-Shop-Schlüsselwort in der Adresse: '{word}'",
            f"Das Wort '{word}' in der Domain-Adresse ist ein häufiges Fake-Shop-Merkmal. "
            "Echte Marken-Outlets laufen immer über die offizielle Marken-Website — nie über eigene Domains.",
        ))

    # ── 7. Jahreszahl oder Zahlen im Domainnamen ─────────────────────────────
    # "nike2024.de", "adidas123.com" — echte Shops brauchen keine Zahlen im Namen.
    # Zahlen entstehen, wenn der echte Name schon vergeben ist.
    if re.search(r"\d{2,}", root_name):
        findings.append(Finding(
            "low",
            "Zahl im Domainnamen",
            f"'{root}' enthält eine Zahl im Domainnamen. "
            "Seriöse Shops haben das kaum — es deutet oft darauf hin, dass der eigentliche Name schon vergeben war.",
        ))

    # ── 8. Zu viele Subdomain-Ebenen ─────────────────────────────────────────
    # "login.adidas.shop.de.com" — Betrüger verschachteln echte Markennamen
    # in Subdomains, damit der Link echter wirkt.
    subdomain_depth = len(host.split("."))
    if subdomain_depth >= 4:
        findings.append(Finding(
            "medium",
            "Verschachtelter Domainname",
            f"'{host}' hat {subdomain_depth} Domain-Ebenen statt der üblichen zwei. "
            "Betrüger verstecken so oft einen bekannten Markennamen vor der echten Ziel-Domain.",
        ))

    # ── 9. Ungewöhnlicher Port ────────────────────────────────────────────────
    # Alle seriösen Shops laufen auf Port 443 (HTTPS) oder 80 (HTTP).
    port_match = re.search(r":(\d+)$", parsed.netloc)
    if port_match and port_match.group(1) not in ("80", "443"):
        findings.append(Finding(
            "medium",
            f"Ungewöhnlicher Port :{port_match.group(1)}",
            "Seriöse Online-Shops laufen immer auf den Standardports. "
            "Ein anderer Port ist ein klares Warnsignal.",
        ))

    # ── 10. Sehr langer Link ─────────────────────────────────────────────────
    # Überlange URLs sollen das eigentliche Ziel im Zeichensalat verstecken.
    if len(raw_url) > 150:
        findings.append(Finding(
            "low",
            "Ungewöhnlich langer Link",
            "Sehr lange Shop-Adressen sollen oft das eigentliche Ziel in einem "
            "Wust aus Zeichen verbergen.",
        ))

    # ── Info-Tipps: Was der Nutzer manuell prüfen sollte ─────────────────────
    # Diese Tipps erscheinen immer — sie ergänzen die automatische Analyse.
    _append_tips(findings)

    return findings


def _append_tips(findings: List[Finding]) -> None:
    """Hängt die Standard-Prüftipps an die Findings-Liste an."""
    findings.append(Finding(
        "info",
        "Bewertungen prüfen",
        "Suche den Shop-Namen auf Trustpilot.com oder bei Google mit dem Zusatz 'Erfahrungen' oder 'Betrug'. "
        "Viele 5-Sterne-Bewertungen bei wenigen Stimmen oder immer ähnlich klingende Texte sind oft gefälscht.",
    ))
    findings.append(Finding(
        "info",
        "Zahlungsmethoden prüfen",
        "Seriöse Shops bieten PayPal, Kreditkarte oder Kauf auf Rechnung an. "
        "Wenn nur Vorkasse per Überweisung oder Kryptowährung möglich ist, sei sehr vorsichtig — "
        "bei Betrug gibt es kein Geld zurück.",
    ))


# ── Gesamtrisiko ──────────────────────────────────────────────────────────────

def overall_risk(findings: List[Finding]) -> Tuple[str, str, float]:
    """
    Berechnet ein Gesamtrisiko aus den Findings.
    Info-Findings zählen nicht zur Risikoberechnung, da sie immer angehängt werden.
    Gibt (Anzeigetext, Farbe, Fortschrittswert 0.0–1.0) zurück.
    """
    # Info-Findings herausfiltern — sie würden das Risiko immer aufblasen
    risk_findings = [f for f in findings if f.severity != "info"]

    if not risk_findings:
        return "Keine Warnsignale gefunden", "#22c55e", 0.08

    high   = sum(1 for f in risk_findings if f.severity == "high")
    medium = sum(1 for f in risk_findings if f.severity == "medium")

    if high >= 2:
        return "Sehr hohes Risiko — wahrscheinlich Fake-Shop", "#ef4444", 1.0
    if high == 1:
        return "Hohes Risiko",                                  "#f97316", 0.75
    if medium >= 2:
        return "Mittleres Risiko",                              "#f59e0b", 0.50
    if medium == 1:
        return "Geringes Risiko",                               "#eab308", 0.30
    return     "Kaum Auffälligkeiten",                          "#22c55e", 0.12
