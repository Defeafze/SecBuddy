"""
fakeshop_detector.py — Fake-Shop-Detector mit drei Prüf-Phasen.

Phase 1 (sofort, lokal):    Heuristische Domain-Analyse
Phase 2 (async, Netzwerk):  WHOIS — Domain-Alter und Registrierungsdauer
Phase 3 (async, Netzwerk):  VirusTotal — 70+ Sicherheits-Engines (optional, API Key)

Phasen 2 und 3 laufen parallel, sobald Phase 1 angezeigt ist.
"""

from urllib.parse import urlparse
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.fakeshop_analyzer import analyze_shop_url, overall_risk, Finding
from app.utils.whois_check import check_domain_age_async
from app.utils.virustotal import check_url_async as vt_check_url_async, VTResult
from app.utils import config
from typing import List, Optional

_SEVERITY_ICON: dict = {
    "high":   "🔴",
    "medium": "🟠",
    "low":    "🟡",
    "info":   "🔵",
}
_SEVERITY_COLOR: dict = {
    "high":   "#ef4444",
    "medium": "#f97316",
    "low":    "#eab308",
    "info":   "#94a3b8",
}


class FakeshopDetectorPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._vt_key: str = config.get("virustotal_key", "")
        # Ein gemeinsamer Generationszähler für alle async-Phasen dieser Seite.
        # Wird beim Start jeder neuen Prüfung erhöht — veraltete Callbacks verwerfen sich selbst.
        self._check_gen: int = 0
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Seitentitel ──────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Fakeshop-Detector",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Prüfe einen Online-Shop auf typische Betrugsmerkmale — bevor du bestellst.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Karte: Was ist ein Fake-Shop? ───────────────────────────────
        info_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info_card.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            info_card, text="Was ist ein Fake-Shop?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line in [
            "Fake-Shops sehen aus wie echte Online-Shops — sie schicken aber entweder gar nichts oder gefälschte Ware.",
            "Sie ahmen bekannte Marken nach, locken mit extremen Rabatten und verschwinden nach kurzer Zeit spurlos.",
            "Besonders gefährlich: Sie stehlen dabei auch deine Zahlungsdaten, Adresse und persönliche Informationen.",
        ]:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(
                row, text="•", font=theme.FONT_BODY,
                text_color=theme.ACCENT, width=14,
            ).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(
                row, text=line, font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY, anchor="w",
                justify="left", wraplength=560,
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(info_card, fg_color="transparent", height=10).pack()

        # ── Info-Karte: Wie funktioniert die Prüfung? ────────────────────────
        method_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        method_card.pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(
            method_card, text="Wie funktioniert die Prüfung?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            method_card,
            text=(
                "① Sofort lokal: Domainname, Verschlüsselung, Marken-Imitation und Betrugs-Muster.\n"
                "② Im Hintergrund: WHOIS — wie lange ist die Domain schon registriert?\n"
                "③ Optional: VirusTotal — über 70 Sicherheits-Engines prüfen die URL (API Key nötig)."
            ),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            justify="left", anchor="w", wraplength=660,
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # ── Eingabe-Bereich ──────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            input_card, text="Shop-Adresse eingeben",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._url_var = ctk.StringVar()
        self._url_entry = ctk.CTkEntry(
            row, textvariable=self._url_var,
            placeholder_text="z. B.  https://adidas-outlet-sale.de   oder   nike-shop2024.com",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=42, corner_radius=theme.RADIUS,
        )
        self._url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._url_entry.bind("<Return>", lambda _e: self._run_check())

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

        # ── VirusTotal Konfiguration (optional) ──────────────────────────────
        self._build_vt_card(inner)

        # ── Ergebnis-Container ───────────────────────────────────────────────
        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "fakeshop").pack(fill="x", pady=(20, 0))

    # ── VirusTotal Konfiguration ──────────────────────────────────────────────

    def _build_vt_card(self, parent: ctk.CTkFrame) -> None:
        """
        Kompakte Konfigurationskarte für den optionalen VirusTotal-API-Key.
        Zeigt Anleitung wenn kein Key gesetzt, sonst nur den Status.
        """
        card = ctk.CTkFrame(parent, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        card.pack(fill="x", pady=(12, 0))

        # Titelzeile mit Status-Label
        title_row = ctk.CTkFrame(card, fg_color="transparent")
        title_row.pack(fill="x", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            title_row, text="🔬  VirusTotal-Prüfung",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(side="left")

        # Badge: "optional" oder "aktiv"
        self._vt_badge = ctk.CTkLabel(
            title_row, text="",
            font=theme.FONT_CAPTION, corner_radius=4,
        )
        self._vt_badge.pack(side="right")

        # Status-Text (wird dynamisch gesetzt)
        self._vt_status_label = ctk.CTkLabel(
            card, text="",
            font=theme.FONT_SMALL, anchor="w",
        )
        self._vt_status_label.pack(anchor="w", padx=18, pady=(0, 6))

        # Kurzanleitung — nur sichtbar wenn kein Key
        self._vt_hint = ctk.CTkLabel(
            card,
            text=(
                "Kostenlosen API Key unter virustotal.com/gui/my-apikey erstellen "
                "(Google-Konto nötig, 500 Anfragen/Tag gratis)."
            ),
            font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED,
            anchor="w", justify="left", wraplength=620,
        )

        # Eingabezeile für Key
        key_row = ctk.CTkFrame(card, fg_color="transparent")
        key_row.pack(fill="x", padx=18, pady=(0, 14))

        self._vt_key_entry = ctk.CTkEntry(
            key_row,
            placeholder_text="VirusTotal API Key einfügen ...",
            show="●",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=36, corner_radius=theme.RADIUS,
        )
        self._vt_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            key_row, text="Speichern", height=36,
            font=theme.FONT_BODY,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._save_vt_key,
        ).pack(side="left")

        self._vt_delete_btn = ctk.CTkButton(
            key_row, text="Entfernen", height=36, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._delete_vt_key,
        )
        self._vt_delete_btn.pack(side="left", padx=(8, 0))

        # Initialen Zustand setzen
        self._update_vt_ui()

    def _update_vt_ui(self) -> None:
        """Passt die VirusTotal-Karte dem aktuellen Key-Status an."""
        if self._vt_key:
            masked = self._vt_key[:4] + "••••••••" + self._vt_key[-4:] if len(self._vt_key) > 8 else "••••••••"
            self._vt_status_label.configure(
                text=f"✅  Konfiguriert: {masked} — wird automatisch mit geprüft.",
                text_color=theme.SUCCESS,
            )
            self._vt_badge.configure(text=" aktiv ", fg_color=theme.SUCCESS, text_color="#052e16")
            self._vt_hint.pack_forget()
            self._vt_delete_btn.pack(side="left", padx=(8, 0))
        else:
            self._vt_status_label.configure(
                text="Optional: Trage deinen VirusTotal API Key ein um 70+ Engines einzubeziehen.",
                text_color=theme.TEXT_MUTED,
            )
            self._vt_badge.configure(text=" optional ", fg_color=theme.BG_MAIN, text_color=theme.TEXT_MUTED)
            self._vt_hint.pack(anchor="w", padx=18, pady=(0, 8), before=self._vt_key_entry.master)
            self._vt_delete_btn.pack_forget()

    def _save_vt_key(self) -> None:
        key = self._vt_key_entry.get().strip()
        if not key:
            return
        config.set("virustotal_key", key)
        self._vt_key = key
        self._vt_key_entry.delete(0, "end")
        self._update_vt_ui()

    def _delete_vt_key(self) -> None:
        config.delete("virustotal_key")
        self._vt_key = ""
        self._update_vt_ui()

    # ── Analyse-Logik ─────────────────────────────────────────────────────────

    def _run_check(self) -> None:
        """
        Startet alle drei Prüf-Phasen.
        Phase 1 läuft sofort, Phasen 2 und 3 parallel im Hintergrund.
        """
        url = self._url_var.get().strip()
        if not url:
            return

        # Neue Generation → laufende Phasen-2/3-Callbacks von vorherigem Check werden verworfen
        self._check_gen += 1
        current_gen = self._check_gen

        self._clear_results()
        domain = self._extract_domain(url)

        # Phase 1: lokale Heuristik (synchron, sofort sichtbar)
        heuristic_findings = analyze_shop_url(url)
        self._show_heuristic_results(heuristic_findings, url)

        # Phase 2: WHOIS (async)
        self._start_whois_phase(domain, current_gen)

        # Phase 3: VirusTotal (async, nur wenn Key konfiguriert)
        if self._vt_key:
            self._start_vt_phase(url, current_gen)

    # ── Phase 1: Heuristik ────────────────────────────────────────────────────

    def _show_heuristic_results(self, findings: List[Finding], url: str) -> None:
        """Baut die sofortige Phase-1-Anzeige auf."""
        label, color, progress = overall_risk(findings)

        risk_card = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
        )
        risk_card.pack(fill="x", pady=(0, 10))

        display_url = url if len(url) <= 80 else url[:77] + "..."
        ctk.CTkLabel(
            risk_card,
            text=f"Analysierte Adresse: {display_url}",
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="w",
        ).pack(anchor="w", padx=18, pady=(12, 4))

        top = ctk.CTkFrame(risk_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkLabel(
            top, text="Gesamteinschätzung:",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            top, text=label,
            font=theme.FONT_SUBHEADING, text_color=color,
        ).pack(side="right")

        bar = ctk.CTkProgressBar(
            risk_card, height=8,
            progress_color=color, fg_color=theme.BORDER, corner_radius=4,
        )
        bar.pack(fill="x", padx=18, pady=(0, 14))
        bar.set(progress)

        warnings = [f for f in findings if f.severity != "info"]
        tips     = [f for f in findings if f.severity == "info"]

        if not warnings:
            ctk.CTkLabel(
                risk_card,
                text="Keine automatisch erkennbaren Warnsignale gefunden.\n"
                     "Prüfe trotzdem die Empfehlungen unten und warte auf WHOIS- und VirusTotal-Ergebnis.",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
                anchor="w", justify="left", wraplength=620,
            ).pack(anchor="w", padx=18, pady=(0, 14))
        else:
            ctk.CTkFrame(risk_card, fg_color="transparent", height=4).pack()

        if warnings:
            ctk.CTkLabel(
                self._result_area, text="Gefundene Warnsignale",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(4, 6))
            for f in warnings:
                self._finding_card(f)

        if tips:
            ctk.CTkLabel(
                self._result_area, text="Was du zusätzlich prüfen solltest",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(12, 6))
            for f in tips:
                self._finding_card(f)

        self._result_area.pack(fill="x", pady=(16, 0))

    # ── Phase 2: WHOIS ────────────────────────────────────────────────────────

    def _start_whois_phase(self, domain: str, gen: int) -> None:
        """Fügt WHOIS-Ladeanzeige ein und startet den WHOIS-Thread."""
        self._whois_header = ctk.CTkLabel(
            self._result_area, text="Domain-Alter (wird geprüft …)",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_MUTED, anchor="w",
        )
        self._whois_header.pack(anchor="w", pady=(12, 6))

        self._whois_placeholder = self._loading_card("⏳  WHOIS-Daten werden abgerufen …")

        def on_done(findings, error):
            self.after(0, lambda: self._on_whois_result(findings, error, gen))

        check_domain_age_async(domain, on_done)

    def _on_whois_result(self, findings, error: Optional[str], gen: int) -> None:
        if gen != self._check_gen:
            return
        self._destroy_if_exists(self._whois_placeholder)
        self._destroy_if_exists(self._whois_header)

        if error:
            lbl = ctk.CTkLabel(
                self._result_area, text="Domain-Alter",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_MUTED, anchor="w",
            )
            lbl.pack(anchor="w", pady=(12, 6))
            err = self._loading_card(f"ℹ️  WHOIS nicht verfügbar: {error}")
            return

        if findings:
            ctk.CTkLabel(
                self._result_area, text="Domain-Alter",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(12, 6))
            for f in findings:
                self._finding_card(f)

    # ── Phase 3: VirusTotal ───────────────────────────────────────────────────

    def _start_vt_phase(self, url: str, gen: int) -> None:
        """Fügt VirusTotal-Ladeanzeige ein und startet den VT-Thread."""
        self._vt_header = ctk.CTkLabel(
            self._result_area, text="VirusTotal (wird geprüft …)",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_MUTED, anchor="w",
        )
        self._vt_header.pack(anchor="w", pady=(12, 6))

        self._vt_placeholder = self._loading_card("🔬  VirusTotal — 70+ Engines werden befragt …")

        def on_done(result: VTResult) -> None:
            self.after(0, lambda: self._on_vt_result(result, gen))

        vt_check_url_async(url, self._vt_key, on_done)

    def _on_vt_result(self, result: VTResult, gen: int) -> None:
        if gen != self._check_gen:
            return
        self._destroy_if_exists(self._vt_placeholder)
        self._destroy_if_exists(self._vt_header)

        # Abschnittsüberschrift
        ctk.CTkLabel(
            self._result_area, text="VirusTotal",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(12, 6))

        if result.error:
            self._loading_card(f"⚠️  {result.error}")
            return

        self._vt_result_card(result)

    def _vt_result_card(self, r: VTResult) -> None:
        """Zeigt das VirusTotal-Ergebnis als farbige Karte mit Statistiken."""
        # Farbe und Einschätzung nach Anzahl malicious Engines
        if r.malicious >= 5:
            color, icon, verdict = theme.DANGER,   "🔴", f"{r.malicious} Engines: Bedrohung erkannt!"
            bg = theme.DANGER_BG
        elif r.malicious >= 1:
            color, icon, verdict = "#f97316", "🟠", f"{r.malicious} Engine{'s' if r.malicious != 1 else ''}: Verdächtig"
            bg = theme.BG_SURFACE
        elif r.suspicious >= 1:
            color, icon, verdict = theme.WARNING, "🟡", f"{r.suspicious} Engine{'s' if r.suspicious != 1 else ''}: Leicht verdächtig"
            bg = theme.BG_SURFACE
        else:
            color, icon, verdict = theme.SUCCESS, "✅", "Keine Bedrohung erkannt"
            bg = theme.SUCCESS_BG

        card = ctk.CTkFrame(
            self._result_area, fg_color=bg,
            corner_radius=theme.RADIUS,
            border_width=1, border_color=color,
        )
        card.pack(fill="x", pady=5)

        # Hauptzeile: Icon + Verdict + Engine-Zahl
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            top, text=f"{icon}  {verdict}",
            font=("Segoe UI", 12, "bold"), text_color=color, anchor="w",
        ).pack(side="left")

        if r.total:
            ctk.CTkLabel(
                top, text=f"{r.total} Engines",
                font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED,
            ).pack(side="right")

        # Fortschrittsbalken: Anteil malicious + suspicious an allen Engines
        if r.total:
            ratio = min((r.malicious + r.suspicious) / r.total, 1.0)
            bar = ctk.CTkProgressBar(
                card, height=6,
                progress_color=color, fg_color=theme.BORDER, corner_radius=3,
            )
            bar.pack(fill="x", padx=16, pady=(0, 8))
            bar.set(max(ratio, 0.01))   # Mindestens 1 % damit Balken sichtbar ist

        # Detailzeile mit allen Zählern
        stats_row = ctk.CTkFrame(card, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(0, 12))

        stats = [
            ("🔴 Bösartig",    r.malicious,  theme.DANGER),
            ("🟠 Verdächtig",  r.suspicious, "#f97316"),
            ("✅ Sicher",      r.harmless,   theme.SUCCESS),
            ("⬜ Kein Befund", r.undetected, theme.TEXT_MUTED),
        ]
        for label, count, clr in stats:
            ctk.CTkLabel(
                stats_row, text=f"{label}: {count}",
                font=theme.FONT_CAPTION, text_color=clr,
            ).pack(side="left", padx=(0, 16))

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def _loading_card(self, text: str) -> ctk.CTkFrame:
        """Erstellt eine dezente Ladekarte und gibt sie zurück (zum späteren Zerstören)."""
        frame = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS,
            border_width=1, border_color=theme.BORDER,
        )
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(
            frame, text=text,
            font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED, anchor="w",
        ).pack(anchor="w", padx=16, pady=14)
        return frame

    def _finding_card(self, f: Finding) -> None:
        """Erstellt eine einzelne Befund-Karte mit farbigem Rahmen."""
        color = _SEVERITY_COLOR[f.severity]
        icon  = _SEVERITY_ICON[f.severity]

        card = ctk.CTkFrame(
            self._result_area,
            fg_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS,
            border_width=1,
            border_color=color,
        )
        card.pack(fill="x", pady=5)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            header, text=f"{icon}  {f.title}",
            font=("Segoe UI", 12, "bold"), text_color=color, anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            card, text=f.detail,
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=620,
        ).pack(anchor="w", padx=16, pady=(0, 12))

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extrahiert den reinen Hostnamen aus einer URL."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return urlparse(url).netloc.split(":")[0]

    @staticmethod
    def _destroy_if_exists(widget) -> None:
        """Zerstört ein Widget nur wenn es noch existiert (verhindert Fehler bei stale Callbacks)."""
        try:
            if widget and widget.winfo_exists():
                widget.destroy()
        except Exception:
            pass

    def _clear(self) -> None:
        self._url_entry.delete(0, "end")
        self._clear_results()

    def _clear_results(self) -> None:
        for widget in self._result_area.winfo_children():
            widget.destroy()
        self._result_area.pack_forget()
