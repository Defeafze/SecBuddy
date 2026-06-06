"""
sender_scanner.py — E-Mail-Absender-Scanner.

Analysiert eine E-Mail-Adresse bzw. die Absender-Domain auf typische
Phishing- und Fake-Shop-E-Mail-Muster. Alles lokal, kein Netzwerk-Call.
"""

import re
from urllib.parse import urlparse
from typing import List
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.fakeshop_analyzer import Finding, _BRANDS, _RISKY_TLDS, _norm, _root_domain


# Bekannte kostenlose E-Mail-Anbieter.
# Ein seriöses Unternehmen schreibt nie von einer Freemailer-Adresse.
_FREE_PROVIDERS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.de", "hotmail.com",
    "hotmail.de", "outlook.com", "outlook.de", "live.com", "live.de",
    "web.de", "gmx.de", "gmx.net", "gmx.com", "t-online.de", "freenet.de",
    "icloud.com", "me.com", "mail.com", "aol.com", "protonmail.com",
    "proton.me", "tutanota.com", "mailbox.org",
}


def analyze_sender(raw: str) -> List[Finding]:
    """
    Analysiert eine E-Mail-Adresse auf Phishing-Indikatoren.
    Gibt eine Liste von Findings zurück.
    """
    findings: List[Finding] = []
    addr = raw.strip().lower()

    # ── E-Mail-Format-Prüfung ────────────────────────────────────────────────
    if "@" not in addr:
        return [Finding("high", "Kein gültiges E-Mail-Format",
                        "Eine E-Mail-Adresse muss ein '@'-Zeichen enthalten.")]

    local, domain = addr.rsplit("@", 1)
    root = _root_domain(domain)
    root_norm = _norm(root)
    tld = "." + domain.rsplit(".", 1)[-1] if "." in domain else ""

    # ── 1. Freemailer als Unternehmensabsender ────────────────────────────────
    # Ein Paketdienst, eine Bank oder ein Shop schreibt nie von gmail.com.
    if domain in _FREE_PROVIDERS:
        findings.append(Finding(
            "high",
            f"Freemailer-Adresse: @{domain}",
            f"Seriöse Unternehmen, Banken und Shops versenden keine offiziellen E-Mails von "
            f"'{domain}'. Das ist ein starkes Zeichen für einen Betrugsversuch.",
        ))

    # ── 2. Marken-Imitation in der Domain ────────────────────────────────────
    # "support@amazon-hilfe.de" — amazon im Domainnamen, aber falsche Root-Domain
    domain_norm = _norm(domain)
    for brand, legit_roots in _BRANDS:
        brand_clean = brand.replace(" ", "").replace("-", "")
        domain_clean = domain_norm.replace("-", "").replace(".", "")
        if brand_clean in domain_clean:
            if not any(_norm(r) == root_norm for r in legit_roots):
                findings.append(Finding(
                    "high",
                    f"Mögliche Imitation von '{brand.title()}'",
                    f"Die Absender-Domain enthält '{brand.title()}', ist aber nicht die offizielle Domain. "
                    f"Phishing-E-Mails nutzen oft Domains wie '{domain}' um echte Marken nachzuahmen. "
                    f"Die echte Adresse wäre @{legit_roots[0]}.",
                ))
                break

    # ── 3. Verdächtige TLD in der Absender-Domain ────────────────────────────
    if tld in _RISKY_TLDS:
        findings.append(Finding(
            "medium",
            f"Ungewöhnliche Domain-Endung: '{tld}'",
            f"Die Endung '{tld}' ist kostenlos oder sehr günstig — häufig bei kurzlebigen "
            "Phishing-Domains eingesetzt.",
        ))

    # ── 4. Viele Bindestriche in der Domain ──────────────────────────────────
    root_name = root.rsplit(".", 1)[0] if "." in root else root
    hyphens = root_name.count("-")
    if hyphens >= 3:
        findings.append(Finding(
            "high",
            f"Sehr viele Bindestriche in der Domain ({hyphens}×)",
            f"Die Domain '{domain}' hat ungewöhnlich viele Bindestriche — typisch für "
            "schnell registrierte Phishing-Domains.",
        ))
    elif hyphens == 2:
        findings.append(Finding(
            "medium",
            "Mehrere Bindestriche in der Domain",
            f"'{domain}' hat mehrere Bindestriche. Das ist bei Phishing-Domains häufig.",
        ))

    # ── 5. Markenname im lokalen Teil (vor dem @) ─────────────────────────────
    # "paypal@fraud-domain.com" — Markenname im lokalen Teil täuscht
    local_norm = _norm(local)
    for brand, _ in _BRANDS:
        brand_clean = brand.replace(" ", "").replace("-", "")
        if brand_clean in local_norm.replace("-", "").replace(".", ""):
            # Nur melden wenn die Domain nicht zur Marke gehört
            findings.append(Finding(
                "medium",
                f"Markenname im Absender-Namen: '{brand.title()}'",
                f"'{brand.title()}' steht vor dem @, aber die Domain '{domain}' gehört nicht "
                "zu dieser Marke. Phishing-Mails nutzen das, um im Postfach vertrauenswürdig auszusehen.",
            ))
            break

    # ── 6. Zahlen in der Domain ───────────────────────────────────────────────
    if re.search(r"\d{2,}", root_name):
        findings.append(Finding(
            "low",
            "Zahl in der Absender-Domain",
            f"'{domain}' enthält eine Zahl im Domainnamen — bei seriösen Unternehmensadressen "
            "ungewöhnlich.",
        ))

    # ── Tipps ─────────────────────────────────────────────────────────────────
    findings.append(Finding(
        "info",
        "Vollständige Absenderadresse prüfen",
        "Im E-Mail-Programm oft auf den Absender-Namen tippen/klicken — dann sieht man die "
        "echte Adresse hinter dem Anzeige-Namen. 'PayPal Support <fraud@xyz.com>' ist eindeutig Betrug.",
    ))
    findings.append(Finding(
        "info",
        "Niemals auf Links in verdächtigen E-Mails klicken",
        "Seriöse Unternehmen fordern dich nie per E-Mail auf, Passwörter einzugeben oder "
        "dringende Zahlungen zu tätigen. Im Zweifel die offizielle Webseite direkt eintippen.",
    ))

    return findings


# ── Seite ─────────────────────────────────────────────────────────────────────

_SEVERITY_COLOR = {
    "high": "#ef4444", "medium": "#f97316", "low": "#eab308", "info": "#94a3b8",
}
_SEVERITY_ICON = {
    "high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵",
}


class SenderScannerPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Absender-Scanner",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            inner,
            text="Prüfe eine E-Mail-Adresse auf Phishing- und Betrugsmerkmale — bevor du antwortest oder klickst.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Karte ────────────────────────────────────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(20, 0))
        ctk.CTkLabel(
            info, text="Woran erkennt man eine Phishing-E-Mail-Adresse?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))
        for line in [
            "Freemailer statt Firmen-Domain: 'amazon-support@gmail.com' — Amazon nutzt immer @amazon.de.",
            "Markenname in der falschen Domain: 'support@paypal-hilfe.de' statt '@paypal.com'.",
            "Der Anzeige-Name täuscht: Im Postfach steht 'PayPal', die echte Adresse ist aber ganz anders.",
            "Viele Bindestriche oder Zahlen in der Domain: 'support@amazon-service2024.de'.",
        ]:
            r = ctk.CTkFrame(info, fg_color="transparent")
            r.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(r, text="•", font=theme.FONT_BODY,
                         text_color=theme.ACCENT, width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(r, text=line, font=theme.FONT_SMALL,
                         text_color=theme.TEXT_SECONDARY, anchor="w",
                         justify="left", wraplength=560).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(info, fg_color="transparent", height=10).pack()

        # ── Eingabe ───────────────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))
        ctk.CTkLabel(
            input_card, text="Absender-E-Mail-Adresse eingeben",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._addr_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            row, textvariable=self._addr_var,
            placeholder_text="z. B.  support@amazon-hilfe.de   oder   noreply@paypal-secure.xyz",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=42, corner_radius=theme.RADIUS,
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        entry.bind("<Return>", lambda _: self._run_check())

        self._check_btn = ctk.CTkButton(
            row, text="Prüfen  →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._run_check,
        )
        self._check_btn.pack(side="left")

        ctk.CTkButton(
            row, text="Leeren", height=42, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._clear,
        ).pack(side="left", padx=(8, 0))

        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "fakeshop").pack(fill="x", pady=(20, 0))

    def _run_check(self) -> None:
        addr = self._addr_var.get().strip()
        if not addr:
            return
        self._clear_results()
        findings = analyze_sender(addr)
        self._show_results(findings, addr)

    def _show_results(self, findings: List[Finding], addr: str) -> None:
        warnings = [f for f in findings if f.severity != "info"]
        tips     = [f for f in findings if f.severity == "info"]

        overview = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
        )
        overview.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            overview, text=f"Geprüfte Adresse: {addr}",
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="w",
        ).pack(anchor="w", padx=18, pady=(12, 4))

        if warnings:
            ctk.CTkLabel(
                overview,
                text=f"⚠️  {len(warnings)} Warnsignal{'e' if len(warnings) != 1 else ''} gefunden",
                font=theme.FONT_SUBHEADING, text_color=theme.WARNING, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 14))
        else:
            ctk.CTkLabel(
                overview,
                text="Keine bekannten Phishing-Muster in dieser Adresse erkannt.",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 14))

        if warnings:
            ctk.CTkLabel(
                self._result_area, text="Gefundene Warnsignale",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(4, 6))
            for f in warnings:
                self._finding_card(f)

        if tips:
            ctk.CTkLabel(
                self._result_area, text="Was du tun solltest",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(12, 6))
            for f in tips:
                self._finding_card(f)

        self._result_area.pack(fill="x", pady=(16, 0))

    def _finding_card(self, f: Finding) -> None:
        color = _SEVERITY_COLOR[f.severity]
        icon  = _SEVERITY_ICON[f.severity]
        card = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS, border_width=1, border_color=color,
        )
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(
            card, text=f"{icon}  {f.title}",
            font=("Segoe UI", 12, "bold"), text_color=color, anchor="w",
        ).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            card, text=f.detail,
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=620,
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def _clear(self) -> None:
        self._addr_var.set("")
        self._clear_results()

    def _clear_results(self) -> None:
        for w in self._result_area.winfo_children():
            w.destroy()
        self._result_area.pack_forget()
