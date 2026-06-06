"""
phone_check.py — Rufnummern-Check.

Prüft eine Telefonnummer heuristisch auf bekannte Betrugs- und
Premium-Rufnummer-Muster (Schwerpunkt Deutschland/Europa).
Alle Checks laufen lokal — keine Daten werden gesendet.
"""

import re
import webbrowser
from typing import List, Tuple
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils import monitoring


# ── Daten ─────────────────────────────────────────────────────────────────────

# Deutsche Premium- und Sonderrufnummern:
# (Regex-Prefix, Icon, Titel, Erklärung, Schweregrad)
_DE_PREMIUM: List[Tuple[str, str, str, str, str]] = [
    (
        r"^0?900",
        "🔴", "Premium-Rufnummer (0900)",
        "0900-Nummern können bis zu 3 € pro Minute kosten. Sie werden häufig bei Telefonbetrug, "
        "gefälschten Gewinnspielen und Abofallen eingesetzt.",
        "high",
    ),
    (
        r"^0?137",
        "🟠", "Massenverkehrs-Dienst (0137)",
        "0137-Nummern sind Mehrwertdienste mit erhöhten Kosten — typisch bei TV-Votings und "
        "Gewinnspielen. Bei unbekanntem Anruf: sofort auflegen.",
        "medium",
    ),
    (
        r"^0?1801|^0?1802|^0?1803|^0?1804|^0?1805|^0?1806|^0?1807",
        "🟡", "Service-Rufnummer (0180x)",
        "0180-Nummern verursachen Sonderkosten. Sie sind nicht kostenlos, auch wenn Werbung "
        "das manchmal andeutet.",
        "low",
    ),
    (
        r"^0?800",
        "🔵", "Kostenfreie Rufnummer (0800)",
        "0800-Nummern sind für den Anrufer kostenlos. Sie werden aber auch von Betrügern genutzt, "
        "die als seriöser Kundendienst auftreten.",
        "info",
    ),
]

# Internationale Vorwahlen, die häufig für Wangiri-Betrug genutzt werden.
# Wangiri = einmal anklingeln lassen, damit man zurückruft (teure Gebühren).
_WANGIRI_CODES: List[Tuple[str, str]] = [
    ("+232", "Sierra Leone"),
    ("+231", "Liberia"),
    ("+216", "Tunesien"),
    ("+675", "Papua-Neuguinea"),
    ("+243", "DR Kongo"),
    ("+222", "Mauretanien"),
    ("+242", "Republik Kongo"),
    ("+267", "Botswana"),
    ("+255", "Tansania"),
    ("+228", "Togo"),
    ("+269", "Komoren"),
    ("+373", "Moldau"),
    ("+963", "Syrien"),
    ("+1473", "Grenada (häufig Wangiri)"),
    ("+1242", "Bahamas (häufig Wangiri)"),
    ("+1284", "Britische Jungferninseln (häufig Wangiri)"),
    ("+1649", "Turks- und Caicosinseln"),
]

_SEVERITY_COLOR = {
    "high":   "#ef4444",
    "medium": "#f97316",
    "low":    "#eab308",
    "info":   "#94a3b8",
}


# ── Analyse ───────────────────────────────────────────────────────────────────

def _normalize(raw: str) -> str:
    """Entfernt Leerzeichen, Klammern und Bindestriche für einheitliche Prüfung."""
    return re.sub(r"[\s\-().\/]", "", raw)


def analyze_number(raw: str) -> List[dict]:
    """
    Analysiert eine Telefonnummer auf Betrugs- und Premiummuster.
    Gibt eine Liste von Befund-Dicts zurück.
    """
    findings = []
    num = _normalize(raw)

    # ── Deutsche Premium- und Sondernummern ─────────────────────────────────
    for pattern, icon, title, detail, severity in _DE_PREMIUM:
        if re.match(pattern, num):
            findings.append({
                "icon": icon, "title": title, "detail": detail, "severity": severity,
            })
            break  # Nur ein Treffer pro Nummer

    # ── Wangiri-Betrug: bekannte internationale Vorwahlen ────────────────────
    for code, country in _WANGIRI_CODES:
        clean_code = code.replace("+", "")
        # Normalisierte Nummer beginnt mit +CC oder 00CC
        if num.startswith("+" + clean_code) or num.startswith("00" + clean_code):
            findings.append({
                "icon":     "🟠",
                "title":    f"Bekannte Wangiri-Vorwahl: {code} ({country})",
                "detail":   (
                    f"Nummern aus {country} ({code}) werden häufig beim Wangiri-Betrug eingesetzt: "
                    "einmal anklingeln, auf Rückruf warten — der dann teuer abgerechnet wird. "
                    "Ruf diese Nummer nicht zurück, wenn du den Anrufer nicht kennst."
                ),
                "severity": "high",
            })
            break

    # ── Empfehlungen (immer) ─────────────────────────────────────────────────
    findings.append({
        "icon":     "🔵",
        "title":    "Auf Tellows.de nachschlagen",
        "detail":   (
            "Tellows.de ist eine Community-Datenbank für verdächtige Rufnummern. "
            "Klicke auf 'Tellows öffnen' um zu sehen, ob andere Nutzer diese Nummer als Betrug gemeldet haben."
        ),
        "severity": "info",
        "tellows":  True,
    })
    findings.append({
        "icon":     "🔵",
        "title":    "Niemals auf unbekannte Nummern zurückrufen",
        "detail":   (
            "Besonders bei einmaligem Anklingeln aus dem Ausland: Nicht zurückrufen. "
            "Im Zweifel die Nummer googeln — echte Unternehmen hinterlassen immer Informationen."
        ),
        "severity": "info",
    })

    return findings


# ── Seite ─────────────────────────────────────────────────────────────────────

class PhoneCheckPage(BasePage):
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
            inner, text="Rufnummer-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            inner,
            text="Prüfe eine Telefonnummer auf bekannte Betrugs- und Premium-Muster.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Karte ────────────────────────────────────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(20, 0))
        ctk.CTkLabel(
            info, text="Typische Telefonbetrugs-Maschen",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))
        for line in [
            "Wangiri: Einmal anklingeln — der Rückruf wird teuer abgerechnet (oft aus unbekannten Ländern).",
            "Falsche Behörden: Angebliche Polizei, Finanzamt oder Microsoft-Support fordern Zahlung oder Daten.",
            "Gewinnbenachrichtigungen: Du hast gewonnen — musst aber erst eine Gebühr zahlen.",
            "Premium-Nummern: Absichtlich verlängerte Gespräche um Kosten zu maximieren.",
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
            input_card, text="Rufnummer eingeben",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._num_var = ctk.StringVar()
        self._num_entry = ctk.CTkEntry(
            row, textvariable=self._num_var,
            placeholder_text="z. B.  0900 123456   oder   +1242 555 0100",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=42, corner_radius=theme.RADIUS,
        )
        self._num_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._num_entry.bind("<Return>", lambda _: self._run_check())

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

        # ── Ergebnis-Bereich ──────────────────────────────────────────────────
        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        # ── Hilfe-Button ──────────────────────────────────────────────────────
        self._help_button(inner, "phishing").pack(fill="x", pady=(20, 0))

    def _run_check(self) -> None:
        num = self._num_var.get().strip()
        if not num:
            return
        monitoring.track_action("phone_check", "check_number")
        self._clear_results()
        self._last_num = num
        findings = analyze_number(num)
        self._show_results(findings, num)

    def _show_results(self, findings: List[dict], num: str) -> None:
        # Warnsignale vs. Info-Tipps trennen
        warnings = [f for f in findings if f["severity"] != "info"]
        tips     = [f for f in findings if f["severity"] == "info"]

        # Übersichts-Karte
        overview = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
        )
        overview.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            overview,
            text=f"Geprüfte Nummer: {num}",
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
                text="Keine bekannten Betrugs- oder Premium-Muster erkannt.",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 14))

        if warnings:
            ctk.CTkLabel(
                self._result_area, text="Warnsignale",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(4, 6))
            for f in warnings:
                self._finding_card(f)

        if tips:
            ctk.CTkLabel(
                self._result_area, text="Empfehlungen",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(12, 6))
            for f in tips:
                self._finding_card(f)

        self._result_area.pack(fill="x", pady=(16, 0))

    def _finding_card(self, f: dict) -> None:
        color = _SEVERITY_COLOR.get(f["severity"], "#94a3b8")
        card = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS, border_width=1, border_color=color,
        )
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(
            card, text=f"{f['icon']}  {f['title']}",
            font=("Segoe UI", 12, "bold"), text_color=color, anchor="w",
        ).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            card, text=f["detail"],
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=620,
        ).pack(anchor="w", padx=16, pady=(0, 8))
        if f.get("tellows"):
            num_clean = re.sub(r"[\s\-().\/]", "", getattr(self, "_last_num", ""))
            ctk.CTkButton(
                card, text="Tellows öffnen  →", height=32, width=170,
                font=theme.FONT_SMALL,
                fg_color="transparent", hover_color=theme.BG_MAIN,
                border_width=1, border_color=theme.ACCENT,
                text_color=theme.ACCENT, corner_radius=theme.RADIUS,
                command=lambda n=num_clean: webbrowser.open(f"https://www.tellows.de/num/{n}"),
            ).pack(anchor="w", padx=16, pady=(0, 12))
        else:
            ctk.CTkFrame(card, fg_color="transparent", height=4).pack()

    def _clear(self) -> None:
        self._num_entry.delete(0, "end")
        self._clear_results()

    def _clear_results(self) -> None:
        for w in self._result_area.winfo_children():
            w.destroy()
        self._result_area.pack_forget()
