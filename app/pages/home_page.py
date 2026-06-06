"""
home_page.py — Startseite / Dashboard von SecBuddy.

Zeigt alle Tool-Gruppen als Karten, einen rotierenden Sicherheitstipp
und einen kurzen Überblick über die App.
"""

import webbrowser
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage


# Sicherheitstipps, die auf der Startseite rotieren
_TIPS = [
    ("🔑", "Ein Passwort pro Konto",
     "Nutze für jeden Account ein eigenes Passwort. Ein Passwort-Manager macht das einfach — "
     "du merkst dir nur noch ein einziges Masterpasswort."),
    ("🔐", "Zwei-Faktor-Authentifizierung aktivieren",
     "Mit 2FA reicht ein gestohlenes Passwort allein nicht mehr aus. "
     "Aktiviere es überall — besonders bei E-Mail und Banking."),
    ("🎣", "Links niemals blind anklicken",
     "Klicke nie auf Links in unerwarteten Mails oder SMS. "
     "Tippe Adressen immer selbst in den Browser — das ist der sicherste Weg."),
    ("🛒", "Shop-URLs vor dem Kauf prüfen",
     "Viele Fake-Shops sehen täuschend echt aus. "
     "Prüfe die Adresse mit dem Fakeshop-Detector bevor du Zahlungsdaten eingibst."),
    ("⚠️",  "Dringlichkeit = Warnsignal",
     "'Sofort handeln!' und 'Konto gesperrt!' sollen Panik auslösen. "
     "Seriöse Unternehmen setzen dich nie unter Zeitdruck — immer erst prüfen."),
    ("📞", "Unbekannte Auslandsnummern nicht zurückrufen",
     "Einmal anklingeln aus einem unbekannten Land? Das ist oft Wangiri-Betrug. "
     "Nicht zurückrufen — die Nummer zuerst mit dem Rufnummer-Check prüfen."),
    ("🔄", "Updates nicht aufschieben",
     "Betriebssystem- und App-Updates schließen bekannte Sicherheitslücken. "
     "Je länger du wartest, desto größer das Risiko."),
    ("✉️",  "Absender-Adresse immer prüfen",
     "Der Anzeige-Name 'Amazon' kann täuschen — dahinter steckt vielleicht 'fraud@xyz.com'. "
     "Klapp die Absenderzeile im E-Mail-Programm immer auf."),
]

# Tool-Gruppen für die Dashboard-Karten
_TOOL_GROUPS = [
    {
        "icon":  "🔑",
        "label": "Passwörter",
        "desc":  "Erstelle sichere Passwörter und prüfe ihre Stärke.",
        "color": "#3b82f6",
        "tools": [
            ("🎲", "Passwort-Generator",    "password_generator",
             "Zufälliges, sicheres Passwort auf Knopfdruck"),
            ("🔤", "Passphrasen-Generator", "passphrase_generator",
             "Sicheres Passwort aus Wörtern — leicht zu merken"),
            ("💪", "Passwort-Stärke-Check", "password_strength",
             "Prüfe wie stark dein Passwort wirklich ist"),
        ],
    },
    {
        "icon":  "👤",
        "label": "Account",
        "desc":  "Prüfe ob deine Daten in Datenlecks aufgetaucht sind.",
        "color": "#8b5cf6",
        "tools": [
            ("🔑", "Passwort-Check",   "password_check",
             "War dein Passwort in einem Datenleck?"),
            ("📋", "E-Mail-Check",     "email_check",
             "Welche Dienste wurden bei dir gehackt?"),
        ],
    },
    {
        "icon":  "🎣",
        "label": "Phishing",
        "desc":  "Erkenne gefährliche Links, Nachrichten und Anrufe.",
        "color": "#f97316",
        "tools": [
            ("🔗", "URL & Absender-Check", "phishing_check",
             "Google Safe Browsing — Milliarden bekannter Bedrohungen"),
            ("📞", "Rufnummer-Check",      "phone_check",
             "Premium-Nummern und Wangiri-Betrug erkennen"),
            ("📝", "Phishing-Text-Scan",   "scam_check",
             "Nachrichten auf Betrugsmerkmale analysieren"),
            ("📷", "QR-Check",             "qr_check",
             "QR-Code-URLs auf Phishing prüfen bevor du klickst"),
        ],
    },
    {
        "icon":  "🛒",
        "label": "Fakeshop",
        "desc":  "Prüfe Shops und E-Mails auf Betrugsmerkmale.",
        "color": "#22c55e",
        "tools": [
            ("🛒", "Fakeshop-Detector",  "fakeshop_detector",
             "Domain-Analyse + WHOIS + VirusTotal"),
            ("✉️",  "Absender-Scanner",   "sender_scanner",
             "E-Mail-Adressen auf Phishing-Muster prüfen"),
        ],
    },
    {
        "icon":  "🔒",
        "label": "Datenschutz",
        "desc":  "Schütze deine Privatsphäre beim Teilen von Dateien.",
        "color": "#06b6d4",
        "tools": [
            ("🖼️", "EXIF-Daten entfernen", "exif_remover",
             "GPS-Standort, Kamera und Zeitstempel aus Fotos löschen"),
        ],
    },
]


class HomePage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._tip_index   = 0
        self._update_url  = ""
        self._build()
        self._start_tip_rotation()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Haftungsausschluss ───────────────────────────────────────────────
        disclaimer = ctk.CTkFrame(
            inner,
            fg_color="#1c0a09",
            corner_radius=theme.RADIUS,
            border_width=2, border_color=theme.DANGER,
        )
        disclaimer.pack(fill="x", pady=(0, 20))

        disc_inner = ctk.CTkFrame(disclaimer, fg_color="transparent")
        disc_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            disc_inner,
            text="⚠️  WICHTIGER HINWEIS — Kein Ersatz für professionelle Sicherheitsberatung",
            font=("Segoe UI", 13, "bold"), text_color=theme.DANGER, anchor="w",
        ).pack(fill="x")

        ctk.CTkFrame(disc_inner, height=1, fg_color="#7f1d1d").pack(fill="x", pady=(8, 10))

        ctk.CTkLabel(
            disc_inner,
            text=(
             """    SecBuddy arbeitet mit heuristischen Algorithmen und öffentlichen Datenbanken. 
                Das Tool kann Fehler machen — sowohl False Positives (harmlose Inhalte als gefährlich markiert) 
                als auch False Negatives (echte Bedrohungen nicht erkannt). """
                
            ),
            font=theme.FONT_SMALL, text_color="#fca5a5",
            anchor="w", justify="left", wraplength=720,
        ).pack(fill="x")

        # ── Update-Banner (anfangs versteckt) ────────────────────────────────
        self._update_banner = ctk.CTkFrame(
            inner,
            fg_color="#0c2340",
            corner_radius=theme.RADIUS,
            border_width=1, border_color=theme.ACCENT,
        )
        # Wird erst durch notify_update() eingeblendet

        banner_row = ctk.CTkFrame(self._update_banner, fg_color="transparent")
        banner_row.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            banner_row, text="🔔",
            font=("Segoe UI", 14), text_color=theme.ACCENT, width=24,
        ).pack(side="left")

        self._banner_text = ctk.CTkLabel(
            banner_row,
            text="",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        )
        self._banner_text.pack(side="left", padx=(8, 0), fill="x", expand=True)

        self._banner_btn = ctk.CTkButton(
            banner_row, text="Jetzt herunterladen  →", height=34, width=200,
            font=theme.FONT_BODY,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._open_release,
        )
        self._banner_btn.pack(side="right")

        # ── Hero-Bereich ─────────────────────────────────────────────────────
        self._hero_frame = hero = ctk.CTkFrame(
            inner,
            fg_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS,
        )
        hero.pack(fill="x")

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=28, pady=24)

        ctk.CTkLabel(
            hero_inner, text="🛡️  SecBuddy",
            font=("Segoe UI", 28, "bold"), text_color=theme.ACCENT, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            hero_inner,
            text="Dein persönlicher Sicherheits-Assistent",
            font=("Segoe UI", 14), text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x", pady=(2, 10))

        ctk.CTkFrame(hero_inner, height=1, fg_color=theme.BORDER).pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            hero_inner,
            text=(
                "SecBuddy hilft dir, dich im Netz zu schützen — ohne Fachwissen, ohne Kosten, "
                "ohne Registrierung.\n"
                "Alle Tools sind kostenlos. Die meisten laufen vollständig lokal auf deinem Gerät."
            ),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            justify="left", anchor="w", wraplength=640,
        ).pack(fill="x")

        # Statistik-Zeile
        stats_row = ctk.CTkFrame(hero_inner, fg_color="transparent")
        stats_row.pack(fill="x", pady=(16, 0))

        stats = [
            ("12", "Tools"),
            ("5",  "Kategorien"),
            ("100 %", "kostenlos"),
            ("🔒", "datenschutzfreundlich"),
        ]
        for value, label in stats:
            chip = ctk.CTkFrame(stats_row, fg_color=theme.BG_MAIN, corner_radius=6)
            chip.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(
                chip, text=f"  {value}  ",
                font=("Segoe UI", 12, "bold"), text_color=theme.ACCENT,
            ).pack(side="left")
            ctk.CTkLabel(
                chip, text=f"{label}  ",
                font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED,
            ).pack(side="left")

        # ── Tool-Karten Überschrift ───────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Alle Tools",
            font=theme.FONT_HEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", pady=(28, 8))

        # ── Tool-Gruppen-Grid (2 Spalten) ────────────────────────────────────
        # Reihe 1: Passwörter + Account
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))
        self._group_card(row1, _TOOL_GROUPS[0])
        ctk.CTkFrame(row1, width=12, fg_color="transparent").pack(side="left")
        self._group_card(row1, _TOOL_GROUPS[1])

        # Reihe 2: Phishing + Fakeshop
        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 12))
        self._group_card(row2, _TOOL_GROUPS[2])
        ctk.CTkFrame(row2, width=12, fg_color="transparent").pack(side="left")
        self._group_card(row2, _TOOL_GROUPS[3])

        # Reihe 3: Datenschutz (halbbreit links)
        row3 = ctk.CTkFrame(inner, fg_color="transparent")
        row3.pack(fill="x")
        self._group_card(row3, _TOOL_GROUPS[4])
        # Platzhalter rechts damit die Karte nicht streckt
        ctk.CTkFrame(row3, width=12, fg_color="transparent").pack(side="left")
        ctk.CTkFrame(row3, fg_color="transparent").pack(side="left", fill="both", expand=True)

        # ── Rotierender Sicherheitstipp ──────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Sicherheitstipp",
            font=theme.FONT_HEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", pady=(28, 8))

        tip_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        tip_card.pack(fill="x")

        tip_inner = ctk.CTkFrame(tip_card, fg_color="transparent")
        tip_inner.pack(fill="x", padx=22, pady=18)

        tip_top = ctk.CTkFrame(tip_inner, fg_color="transparent")
        tip_top.pack(fill="x")

        self._tip_icon = ctk.CTkLabel(
            tip_top, text="",
            font=("Segoe UI", 20), text_color=theme.ACCENT, width=32,
        )
        self._tip_icon.pack(side="left", padx=(0, 8))

        self._tip_title = ctk.CTkLabel(
            tip_top, text="",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        )
        self._tip_title.pack(side="left", fill="x", expand=True)

        # Tipp-Navigation (Punkte)
        nav_row = ctk.CTkFrame(tip_top, fg_color="transparent")
        nav_row.pack(side="right")
        ctk.CTkButton(
            nav_row, text="‹", width=28, height=28,
            font=("Segoe UI", 14), fg_color=theme.BG_MAIN,
            hover_color=theme.BORDER, text_color=theme.TEXT_SECONDARY,
            corner_radius=6,
            command=self._prev_tip,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            nav_row, text="›", width=28, height=28,
            font=("Segoe UI", 14), fg_color=theme.BG_MAIN,
            hover_color=theme.BORDER, text_color=theme.TEXT_SECONDARY,
            corner_radius=6,
            command=self._next_tip,
        ).pack(side="left", padx=2)

        self._tip_body = ctk.CTkLabel(
            tip_inner, text="",
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=640,
        )
        self._tip_body.pack(anchor="w", pady=(8, 0))

        self._tip_counter = ctk.CTkLabel(
            tip_inner, text="",
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="e",
        )
        self._tip_counter.pack(fill="x", pady=(6, 0))

        # Initialen Tipp anzeigen
        self._show_tip()

    # ── Gruppen-Karte ─────────────────────────────────────────────────────────

    def _group_card(self, parent: ctk.CTkFrame, group: dict) -> None:
        """Erstellt eine Gruppen-Karte mit Tool-Zeilen für das Dashboard-Grid."""
        card = ctk.CTkFrame(parent, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        card.pack(side="left", fill="both", expand=True)

        # Gruppen-Header mit farbigem Akzent-Balken links
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=0, pady=(0, 0))

        accent_bar = ctk.CTkFrame(header, width=4, fg_color=group["color"], corner_radius=2)
        accent_bar.pack(side="left", fill="y", padx=(14, 0), pady=14)

        header_text = ctk.CTkFrame(header, fg_color="transparent")
        header_text.pack(side="left", fill="x", expand=True, padx=10, pady=14)

        ctk.CTkLabel(
            header_text,
            text=f"{group['icon']}  {group['label']}",
            font=("Segoe UI", 13, "bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            header_text, text=group["desc"],
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="w",
        ).pack(fill="x")

        ctk.CTkFrame(card, height=1, fg_color=theme.BORDER).pack(fill="x", padx=14)

        # Tool-Zeilen
        for tool_icon, tool_name, page_key, tool_desc in group["tools"]:
            self._tool_row(card, tool_icon, tool_name, page_key, tool_desc)

        # Unterer Abstand
        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _tool_row(
        self,
        parent: ctk.CTkFrame,
        icon: str,
        name: str,
        page_key: str,
        desc: str,
    ) -> None:
        """Einzelne klickbare Tool-Zeile innerhalb einer Gruppen-Karte."""
        row = ctk.CTkFrame(parent, fg_color="transparent", cursor="hand2")
        row.pack(fill="x", padx=14, pady=3)

        ctk.CTkLabel(
            row, text=icon,
            font=("Segoe UI", 16), text_color=theme.ACCENT, width=28,
        ).pack(side="left", pady=6)

        mid = ctk.CTkFrame(row, fg_color="transparent")
        mid.pack(side="left", fill="x", expand=True, padx=(6, 0))

        ctk.CTkLabel(
            mid, text=name,
            font=theme.FONT_SMALL, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            mid, text=desc,
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="w",
        ).pack(fill="x")

        btn = ctk.CTkButton(
            row, text="→", width=30, height=30,
            font=("Segoe UI", 13),
            fg_color="transparent", hover_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=6,
            command=lambda k=page_key: self._navigate and self._navigate(k),
        )
        btn.pack(side="right")

        # Hover-Highlight für die gesamte Zeile
        def _enter(_e):
            row.configure(fg_color=theme.BORDER)
        def _leave(_e):
            row.configure(fg_color="transparent")

        for widget in (row, mid, btn):
            widget.bind("<Enter>", _enter)
            widget.bind("<Leave>", _leave)
        for child in mid.winfo_children():
            child.bind("<Enter>", _enter)
            child.bind("<Leave>", _leave)

        # Klick auf die gesamte Zeile navigiert zur Seite
        for widget in (row, mid):
            widget.bind("<Button-1>", lambda _e, k=page_key: self._navigate and self._navigate(k))
        for child in mid.winfo_children():
            child.bind("<Button-1>", lambda _e, k=page_key: self._navigate and self._navigate(k))

    # ── Tipp-Rotation ─────────────────────────────────────────────────────────

    def _show_tip(self) -> None:
        icon, title, body = _TIPS[self._tip_index]
        self._tip_icon.configure(text=icon)
        self._tip_title.configure(text=title)
        self._tip_body.configure(text=body)
        self._tip_counter.configure(
            text=f"{self._tip_index + 1} / {len(_TIPS)}",
        )

    def _next_tip(self) -> None:
        self._tip_index = (self._tip_index + 1) % len(_TIPS)
        self._show_tip()

    def _prev_tip(self) -> None:
        self._tip_index = (self._tip_index - 1) % len(_TIPS)
        self._show_tip()

    def _start_tip_rotation(self) -> None:
        """Rotiert automatisch alle 8 Sekunden zum nächsten Tipp."""
        self._next_tip()
        self.after(8000, self._start_tip_rotation)

    # ── Update-Banner ─────────────────────────────────────────────────────────

    def notify_update(self, version: str, url: str, notes: str) -> None:
        """
        Wird vom Updater aufgerufen wenn eine neue Version verfügbar ist.
        Muss im Main-Thread laufen — aus Background-Threads via after(0, ...) aufrufen.
        """
        self._update_url = url
        self._banner_text.configure(
            text=f"Update verfügbar: SecBuddy v{version}",
        )
        self._update_banner.pack(fill="x", pady=(0, 16), before=self._hero_frame)

    def _open_release(self) -> None:
        if self._update_url:
            webbrowser.open(self._update_url)
