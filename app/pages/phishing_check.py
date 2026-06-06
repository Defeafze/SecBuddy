"""
phishing_check.py — Phishing & URL-Check via Google Safe Browsing API.

Zwei Phasen:
  - API-Key-Verwaltung: Nutzer trägt seinen Google-API-Key einmalig ein.
  - URL-Prüfung: Asynchrone Abfrage gegen Googles Bedrohungsdatenbank.

Wichtig: Die geprüfte URL wird an Google-Server gesendet.
Das wird dem Nutzer transparent mitgeteilt.
"""

import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils import config
from app.utils.safe_browsing import check_url_async, SafeBrowsingResult


class PhishingCheckPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        # API-Key aus persistenter Konfiguration laden
        self._api_key: str = config.get("google_safe_browsing_key", "")
        # Generationszähler: verhindert, dass alte Callbacks neue Ergebnisse überschreiben
        self._check_gen: int = 0
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Seitentitel ──────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Phishing & URL-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Prüfe einen Link gegen Googles Bedrohungsdatenbank mit Milliarden bekannter Phishing- und Malware-Seiten.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Datenschutz-Hinweis ───────────────────────────────────────────────
        # Dieser Check sendet die URL an Google — das muss der Nutzer wissen.
        privacy_card = ctk.CTkFrame(
            inner, fg_color="#1c1a09", corner_radius=theme.RADIUS,
            border_width=1, border_color="#854d0e",
        )
        privacy_card.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(
            privacy_card, text="ℹ️  Hinweis: Die URL wird an Google gesendet",
            font=theme.FONT_SUBHEADING, text_color="#fbbf24", anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            privacy_card,
            text=(
                "Anders als die anderen SecBuddy-Tools läuft dieser Check nicht lokal. "
                "Die eingegebene URL wird zur Prüfung an die Google Safe Browsing API übermittelt. "
                "Gib hier keine sensiblen URLs ein (z. B. interne Firmen-Links mit Zugangsdaten in der Adresse)."
            ),
            font=theme.FONT_SMALL, text_color="#fde68a",
            anchor="w", justify="left", wraplength=640,
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # ── API-Key Karte ────────────────────────────────────────────────────
        self._build_api_key_card(inner)

        # ── Info-Karte: Was ist Safe Browsing? ───────────────────────────────
        info_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info_card.pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(
            info_card, text="Was ist Google Safe Browsing?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line in [
            "Google pflegt eine ständig aktualisierte Liste mit Milliarden bekannter Phishing-, Malware- und Betrugsseiten.",
            "Browser wie Chrome und Firefox nutzen dieselbe Datenbank, um dich vor gefährlichen Seiten zu warnen.",
            "Die API prüft URLs in Echtzeit — ein 'sauber' bedeutet, dass die URL nicht in der Datenbank steht.",
            "Achtung: Sehr neue Phishing-Seiten werden möglicherweise noch nicht erkannt.",
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

        # ── URL-Eingabe ──────────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            input_card, text="Link eingeben und prüfen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._url_var = ctk.StringVar()
        self._url_entry = ctk.CTkEntry(
            row, textvariable=self._url_var,
            placeholder_text="z. B.  https://suspicious-site.com   oder  paypal-login.xyz",
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

        # ── Ergebnis-Container ───────────────────────────────────────────────
        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "phishing").pack(fill="x", pady=(20, 0))

        # Initialen UI-Zustand setzen (Key vorhanden oder nicht?)
        self._update_ui_state()

    # ── API-Key Verwaltung ────────────────────────────────────────────────────

    def _build_api_key_card(self, parent: ctk.CTkFrame) -> None:
        """
        Baut die API-Key-Karte auf.
        Enthält Statusanzeige, Setup-Anleitung (ein-/ausblendbar) und Eingabefeld.
        """
        card = ctk.CTkFrame(parent, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        card.pack(fill="x", pady=(16, 0))

        # Titelzeile
        ctk.CTkLabel(
            card, text="🔑  Google Safe Browsing API Key",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        # Status-Label: dynamisch, wird in _update_ui_state aktualisiert
        self._key_status_label = ctk.CTkLabel(
            card, text="",
            font=theme.FONT_SMALL, anchor="w",
        )
        self._key_status_label.pack(anchor="w", padx=18, pady=(0, 8))

        # ── Setup-Anleitung ──────────────────────────────────────────────────
        # Wird nur eingeblendet, wenn noch kein Key konfiguriert ist.
        self._setup_hints = ctk.CTkFrame(card, fg_color="transparent")

        ctk.CTkLabel(
            self._setup_hints,
            text="So bekommst du deinen kostenlosen API Key (dauert ca. 2 Minuten):",
            font=("Segoe UI", 11, "bold"), text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 6))

        steps = [
            ('1.', 'Gehe zu console.cloud.google.com und melde dich mit einem Google-Konto an.'),
            ('2.', 'Klicke oben auf "Projekt auswählen" → "Neues Projekt" → Namen eingeben → "Erstellen".'),
            ('3.', 'Oben links auf das Menü (☰) → "APIs & Dienste" → "Bibliothek".'),
            ('4.', 'Suche nach "Safe Browsing API" → öffnen → "Aktivieren" klicken.'),
            ('5.', '"APIs & Dienste" → "Anmeldedaten" → "+ Anmeldedaten erstellen" → "API-Schlüssel".'),
            ('6.', 'Den angezeigten Key kopieren und unten einfügen.'),
        ]
        for num, text in steps:
            row = ctk.CTkFrame(self._setup_hints, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(
                row, text=num,
                font=("Segoe UI", 11, "bold"), text_color=theme.ACCENT, width=22,
            ).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(
                row, text=text, font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY, anchor="w",
                justify="left", wraplength=570,
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(self._setup_hints, fg_color="transparent", height=8).pack()

        # ── Key-Eingabezeile ─────────────────────────────────────────────────
        key_row = ctk.CTkFrame(card, fg_color="transparent")
        key_row.pack(fill="x", padx=18, pady=(0, 16))

        self._key_entry = ctk.CTkEntry(
            key_row,
            placeholder_text="API Key hier einfügen ...",
            show="●",          # Key versteckt anzeigen
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=38, corner_radius=theme.RADIUS,
        )
        self._key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Sichtbarkeit des Keys umschalten (Augensymbol)
        self._key_visible = False
        ctk.CTkButton(
            key_row, text="👁", width=38, height=38,
            font=("Segoe UI", 15),
            fg_color=theme.BG_MAIN, hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SECONDARY, corner_radius=theme.RADIUS,
            command=self._toggle_key_visibility,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            key_row, text="Speichern", height=38,
            font=theme.FONT_BODY,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._save_key,
        ).pack(side="left")

        # Key löschen — nur sichtbar wenn ein Key vorhanden
        self._delete_key_btn = ctk.CTkButton(
            key_row, text="Entfernen", height=38, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._delete_key,
        )
        self._delete_key_btn.pack(side="left", padx=(8, 0))

    def _update_ui_state(self) -> None:
        """
        Passt alle UI-Elemente an den aktuellen Zustand (Key vorhanden oder nicht) an.
        Wird einmal beim Starten und nach jedem Key-Speichern/Löschen aufgerufen.
        """
        if self._api_key:
            # Key vorhanden: Anleitung ausblenden, Status grün, Button aktiv
            self._setup_hints.pack_forget()
            masked = self._api_key[:4] + "••••••••" + self._api_key[-4:] if len(self._api_key) > 8 else "••••••••••••"
            self._key_status_label.configure(
                text=f"✅  Konfiguriert: {masked}",
                text_color=theme.SUCCESS,
            )
            self._delete_key_btn.pack(side="left", padx=(8, 0))
            self._check_btn.configure(state="normal", text="Prüfen  →")
        else:
            # Kein Key: Anleitung einblenden, Status gelb, Button gesperrt
            self._setup_hints.pack(fill="x", before=self._key_entry.master)
            self._key_status_label.configure(
                text="⚠️  Noch kein API Key eingerichtet — folge der Anleitung unten.",
                text_color=theme.WARNING,
            )
            self._delete_key_btn.pack_forget()
            self._check_btn.configure(state="disabled", text="API Key fehlt")

    def _save_key(self) -> None:
        """Speichert den eingegebenen API Key persistent und aktualisiert den UI-Zustand."""
        key = self._key_entry.get().strip()
        if not key:
            return
        config.set("google_safe_browsing_key", key)
        self._api_key = key
        self._key_entry.delete(0, "end")
        self._key_entry.configure(show="●")
        self._key_visible = False
        self._update_ui_state()

    def _delete_key(self) -> None:
        """Entfernt den API Key aus der Konfiguration."""
        config.delete("google_safe_browsing_key")
        self._api_key = ""
        self._update_ui_state()

    def _toggle_key_visibility(self) -> None:
        """Schaltet das Key-Eingabefeld zwischen sichtbar und versteckt."""
        self._key_visible = not self._key_visible
        self._key_entry.configure(show="" if self._key_visible else "●")

    # ── URL-Prüfung ──────────────────────────────────────────────────────────

    def _run_check(self) -> None:
        """Startet die asynchrone URL-Prüfung gegen Safe Browsing."""
        url = self._url_var.get().strip()
        if not url or not self._api_key:
            return

        self._check_gen += 1
        current_gen = self._check_gen

        # UI in Ladezustand
        self._check_btn.configure(state="disabled", text="Prüfe …")
        self._clear_results()

        def on_done(result: SafeBrowsingResult) -> None:
            # Callback kommt aus Hintergrund-Thread — via .after() in den GUI-Thread
            self.after(0, lambda: self._on_result(result, current_gen))

        check_url_async(url, self._api_key, on_done)

    def _on_result(self, result: SafeBrowsingResult, gen: int) -> None:
        """Verarbeitet das Ergebnis der Safe-Browsing-Prüfung und zeigt es an."""
        # Veralteten Callback (von vorheriger Prüfung) ignorieren
        if gen != self._check_gen:
            return

        self._check_btn.configure(state="normal", text="Prüfen  →")

        if result.error:
            self._show_error(result.error)
        elif result.is_safe:
            self._show_safe()
        else:
            self._show_threats(result.matches)

    def _show_safe(self) -> None:
        """Grüne Ergebniskarte: URL nicht in der Bedrohungsdatenbank."""
        card = ctk.CTkFrame(
            self._result_area, fg_color=theme.SUCCESS_BG, corner_radius=theme.RADIUS,
        )
        card.pack(fill="x")

        ctk.CTkLabel(
            card, text="✅  Nicht als Bedrohung bekannt",
            font=theme.FONT_HEADING, text_color=theme.SUCCESS, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            card,
            text=(
                "Diese URL ist nicht in Googles Bedrohungsdatenbank gelistet.\n"
                "Das bedeutet nicht automatisch, dass die Seite sicher ist — sehr neue "
                "Phishing-Seiten werden möglicherweise noch nicht erkannt. Im Zweifel lieber "
                "nicht klicken und den Betrugs-Check nutzen."
            ),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=640,
        ).pack(anchor="w", padx=18, pady=(0, 14))

        self._result_area.pack(fill="x", pady=(16, 0))

    def _show_threats(self, matches) -> None:
        """Rote Ergebniskarte mit allen gefundenen Bedrohungen."""
        # Übersichts-Karte
        overview = ctk.CTkFrame(
            self._result_area, fg_color=theme.DANGER_BG, corner_radius=theme.RADIUS,
        )
        overview.pack(fill="x", pady=(0, 10))

        count = len(matches)
        ctk.CTkLabel(
            overview, text=f"🚨  {count} Bedrohung{'en' if count != 1 else ''} gefunden!",
            font=theme.FONT_HEADING, text_color=theme.DANGER, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            overview,
            text=(
                "Diese URL ist in Googles Datenbank als gefährlich gelistet. "
                "Öffne sie auf keinen Fall und gib dort keine Daten ein."
            ),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # Eine Karte pro Bedrohungstyp
        ctk.CTkLabel(
            self._result_area, text="Gefundene Bedrohungen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(4, 6))

        for match in matches:
            threat_card = ctk.CTkFrame(
                self._result_area, fg_color=theme.BG_SURFACE,
                corner_radius=theme.RADIUS,
                border_width=1, border_color=theme.DANGER,
            )
            threat_card.pack(fill="x", pady=5)

            ctk.CTkLabel(
                threat_card, text=f"{match.icon}  {match.title}",
                font=("Segoe UI", 12, "bold"), text_color=theme.DANGER, anchor="w",
            ).pack(anchor="w", padx=16, pady=(12, 4))

            ctk.CTkLabel(
                threat_card, text=match.detail,
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
                anchor="w", justify="left", wraplength=620,
            ).pack(anchor="w", padx=16, pady=(0, 12))

        self._result_area.pack(fill="x", pady=(16, 0))

    def _show_error(self, message: str) -> None:
        """Orange Fehlerkarte bei Verbindungsproblemen oder ungültigem Key."""
        card = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
        )
        card.pack(fill="x")

        ctk.CTkLabel(
            card, text="⚠️  Fehler bei der Prüfung",
            font=theme.FONT_HEADING, text_color=theme.WARNING, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            card, text=message,
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        self._result_area.pack(fill="x", pady=(16, 0))

    # ── Hilfsmethoden ────────────────────────────────────────────────────────

    def _clear(self) -> None:
        self._url_entry.delete(0, "end")
        self._clear_results()

    def _clear_results(self) -> None:
        for widget in self._result_area.winfo_children():
            widget.destroy()
        self._result_area.pack_forget()
