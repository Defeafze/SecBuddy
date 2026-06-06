"""
app.py — Hauptfenster mit Hover-Sidebar.

Die Sidebar besteht aus Gruppen (PASSWÖRTER, ACCOUNT, PHISHING, FAKESHOP).
Hover über eine Gruppe klappt die Unterseiten auf; die aktive Gruppe bleibt
dauerhaft geöffnet bis eine andere Gruppe navigiert wird.
"""

import sys
import pathlib
from typing import Optional
import customtkinter as ctk
from PIL import Image as PilImage
from app import theme
from app import config
from app.utils import monitoring, updater

# Im PyInstaller-Bundle liegen Datendateien unter sys._MEIPASS
_BASE   = pathlib.Path(sys._MEIPASS) if getattr(sys, "frozen", False) else pathlib.Path(__file__).parent.parent
_ASSETS = _BASE / "assets"
from app.pages.password_check        import PasswordCheckPage
from app.pages.password_generator    import PasswordGeneratorPage
from app.pages.passphrase_generator  import PassphraseGeneratorPage
from app.pages.password_strength     import PasswordStrengthPage
from app.pages.email_check           import EmailCheckPage
from app.pages.phishing_check        import PhishingCheckPage
from app.pages.phone_check           import PhoneCheckPage
from app.pages.scam_check            import ScamCheckPage
from app.pages.qr_check              import QRCheckPage
from app.pages.fakeshop_detector     import FakeshopDetectorPage
from app.pages.sender_scanner        import SenderScannerPage
from app.pages.exif_remover          import ExifRemoverPage
from app.pages.home_page             import HomePage
from app.pages.help_page             import HelpPage


# Sidebar-Gruppen-Definition:
# (icon, label, help_tab_id, [(sub_icon, sub_label, page_key), ...])
_GROUPS = [
    ("🔑", "Passwörter", "passwort", [
        ("🎲", "Generator",       "password_generator"),
        ("🔤", "Passphrasen",     "passphrase_generator"),
        ("💪", "Stärke-Check",    "password_strength"),
    ]),
    ("👤", "Account", "account", [
        ("🔑", "Passwort-Check",  "password_check"),
        ("📋", "E-Mail-Check",    "email_check"),
    ]),
    ("🎣", "Phishing", "phishing", [
        ("🔗", "URL & Absender",  "phishing_check"),
        ("📞", "Rufnummer-Check", "phone_check"),
        ("📝", "Text-Scan",       "scam_check"),
        ("📷", "QR-Check",        "qr_check"),
    ]),
    ("🛒", "Fakeshop", "fakeshop", [
        ("🛒", "Fakeshop-Detector", "fakeshop_detector"),
        ("✉️",  "Absender-Scanner",  "sender_scanner"),
    ]),
    ("🔒", "Datenschutz", "datenschutz", [
        ("🖼️", "EXIF entfernen",   "exif_remover"),
    ]),
]


class SecBuddyApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SecBuddy")
        self.geometry("960x640")
        self.minsize(840, 560)
        self.configure(fg_color=theme.BG_MAIN)

        # Taskleisten- und Titelleisten-Icon
        _ico = _ASSETS / "icon.ico"
        if _ico.exists():
            self.iconbitmap(str(_ico))

        self._pages: dict        = {}
        self._nav_buttons: dict  = {}   # page_key → CTkButton
        self._group_meta: list   = []   # Dicts mit expand/collapse/keys pro Gruppe

        self._build_sidebar()
        self._build_content()
        self._register_pages()

        # Startseite anzeigen
        self.show_page("home")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> None:
        sb = ctk.CTkFrame(
            self, width=theme.SIDEBAR_WIDTH,
            fg_color=theme.BG_SIDEBAR, corner_radius=0,
        )
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Logo — klickbar zum Navigieren zur Startseite
        logo = ctk.CTkFrame(sb, fg_color="transparent", cursor="hand2")
        logo.pack(fill="x", padx=18, pady=(16, 0))

        logo_row = ctk.CTkFrame(logo, fg_color="transparent")
        logo_row.pack(fill="x")

        _logo_png = _ASSETS / "logo.png"
        if _logo_png.exists():
            _ctk_img = ctk.CTkImage(
                light_image=PilImage.open(_logo_png),
                dark_image=PilImage.open(_logo_png),
                size=(36, 36),
            )
            img_lbl = ctk.CTkLabel(logo_row, image=_ctk_img, text="")
            img_lbl.pack(side="left", padx=(0, 8))
            img_lbl.bind("<Button-1>", lambda _e: self.show_page("home"))

        title_lbl = ctk.CTkLabel(
            logo_row, text="SecBuddy",
            font=theme.FONT_TITLE, text_color=theme.ACCENT, anchor="w",
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        sub_lbl = ctk.CTkLabel(
            logo, text="Dein Sicherheits-Assistent",
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="w",
        )
        sub_lbl.pack(fill="x", pady=(2, 0))

        # Klick auf Logo öffnet Startseite
        for w in (logo, logo_row, title_lbl, sub_lbl):
            w.bind("<Button-1>", lambda _e: self.show_page("home"))

        ctk.CTkFrame(sb, height=1, fg_color=theme.BORDER).pack(fill="x", padx=16, pady=16)

        # Hover-Gruppen
        for icon, label, help_tab, items in _GROUPS:
            self._make_group(sb, icon, label, items)

        # Hilfe-Button unten
        ctk.CTkFrame(sb, height=1, fg_color=theme.BORDER).pack(
            side="bottom", fill="x", padx=16, pady=0,
        )
        btn = ctk.CTkButton(
            sb, text="❓  Hilfe",
            font=theme.FONT_BODY,
            anchor="w",
            fg_color="transparent",
            text_color=theme.TEXT_SECONDARY,
            hover_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS,
            height=40,
            command=lambda: self.show_page("help"),
        )
        btn.pack(side="bottom", fill="x", padx=10, pady=(4, 14))
        self._nav_buttons["help"] = btn

    def _make_group(
        self,
        parent: ctk.CTkFrame,
        icon: str,
        label: str,
        items: list,
    ) -> None:
        """
        Erstellt eine aufklappbare Sidebar-Gruppe mit Hover-Mechanismus.

        Logik:
        - Hover auf äußerem Frame → expand (klappt Unterseiten auf)
        - Maus verlässt Frame → collapse nach 200 ms (sofern nicht aktive Gruppe)
        - Aktive Gruppe (_permanent=True) bleibt offen bis andere Gruppe aktiv wird
        """
        keys = {item[2] for item in items}

        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(fill="x", pady=2)

        # ── Gruppen-Header (kein Button — nur visuelle Zeile) ─────────────────
        header = ctk.CTkFrame(outer, fg_color="transparent", cursor="hand2")
        header.pack(fill="x", padx=10)

        icon_lbl = ctk.CTkLabel(
            header, text=icon,
            font=("Segoe UI", 15), text_color=theme.TEXT_MUTED, width=26,
        )
        icon_lbl.pack(side="left", padx=(8, 4), pady=10)

        text_lbl = ctk.CTkLabel(
            header, text=label,
            font=("Segoe UI", 11, "bold"), text_color=theme.TEXT_MUTED, anchor="w",
        )
        text_lbl.pack(side="left", fill="x", expand=True)

        arrow_lbl = ctk.CTkLabel(
            header, text="›",
            font=("Segoe UI", 14), text_color=theme.TEXT_MUTED, width=20,
        )
        arrow_lbl.pack(side="right", padx=6)

        # ── Unterseiten-Frame (zunächst versteckt) ────────────────────────────
        sub = ctk.CTkFrame(outer, fg_color="transparent")

        for sub_icon, sub_label, sub_key in items:
            btn = ctk.CTkButton(
                sub,
                text=f"  {sub_icon}  {sub_label}",
                font=theme.FONT_SMALL,
                anchor="w",
                fg_color="transparent",
                text_color=theme.TEXT_SECONDARY,
                hover_color=theme.BG_SURFACE,
                corner_radius=theme.RADIUS,
                height=36,
                command=lambda k=sub_key: self.show_page(k),
            )
            btn.pack(fill="x", padx=(14, 10), pady=1)
            self._nav_buttons[sub_key] = btn

        # ── Expand / Collapse ─────────────────────────────────────────────────
        _permanent = [False]   # True = aktive Gruppe, bleibt offen ohne Hover

        def expand(permanent: bool = False) -> None:
            if permanent:
                _permanent[0] = True
            arrow_lbl.configure(text="▾")
            text_lbl.configure(
                text_color=theme.ACCENT if permanent else theme.TEXT_PRIMARY,
            )
            icon_lbl.configure(
                text_color=theme.ACCENT if permanent else theme.TEXT_PRIMARY,
            )
            sub.pack(fill="x")

        def collapse(force: bool = False) -> None:
            if force:
                _permanent[0] = False
            if not _permanent[0]:
                arrow_lbl.configure(text="›")
                text_lbl.configure(text_color=theme.TEXT_MUTED)
                icon_lbl.configure(text_color=theme.TEXT_MUTED)
                sub.pack_forget()

        def check_collapse() -> None:
            """Prüft ob die Maus noch im Gruppenbereich ist; collapsiert sonst."""
            if _permanent[0]:
                return
            try:
                px, py = outer.winfo_pointerx(), outer.winfo_pointery()
                rx = outer.winfo_rootx()
                ry = outer.winfo_rooty()
                rw = outer.winfo_width()
                rh = outer.winfo_height()
                if rx <= px <= rx + rw and ry <= py <= ry + rh:
                    return  # Maus noch drin
            except Exception:
                pass
            collapse()

        # Hover-Bindings auf alle Widgets im äußeren Frame
        def _bind(widget: ctk.CTkBaseClass) -> None:
            widget.bind("<Enter>", lambda _e: expand())
            widget.bind("<Leave>", lambda _e: outer.after(200, check_collapse))
            for child in widget.winfo_children():
                _bind(child)

        _bind(outer)

        # Meta-Daten für show_page() speichern
        self._group_meta.append({
            "keys":    keys,
            "expand":  expand,
            "collapse": collapse,
        })

    # ── Content-Bereich ───────────────────────────────────────────────────────

    def _build_content(self) -> None:
        self._content = ctk.CTkFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        self._content.pack(side="right", fill="both", expand=True)

    def _register_pages(self) -> None:
        page_map = [
            ("home",                  HomePage),
            ("password_generator",    PasswordGeneratorPage),
            ("passphrase_generator",  PassphraseGeneratorPage),
            ("password_strength",     PasswordStrengthPage),
            ("password_check",        PasswordCheckPage),
            ("email_check",           EmailCheckPage),
            ("phishing_check",        PhishingCheckPage),
            ("phone_check",           PhoneCheckPage),
            ("scam_check",            ScamCheckPage),
            ("qr_check",              QRCheckPage),
            ("fakeshop_detector",     FakeshopDetectorPage),
            ("sender_scanner",        SenderScannerPage),
            ("exif_remover",          ExifRemoverPage),
            ("help",                  HelpPage),
        ]
        for key, PageClass in page_map:
            page = PageClass(self._content)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            page.place_forget()
            self._pages[key] = page

        # Alle Seiten erhalten die Navigate-Funktion für Help-Buttons
        for page in self._pages.values():
            if hasattr(page, "set_navigate"):
                page.set_navigate(self.show_page)

        # Update-Check im Hintergrund starten
        home = self._pages["home"]
        updater.check(
            owner=config.GITHUB_OWNER,
            repo=config.GITHUB_REPO,
            current_version=config.APP_VERSION,
            on_update=lambda v, url, notes: self.after(0, lambda: home.notify_update(v, url, notes)),
        )

    # ── Navigation ────────────────────────────────────────────────────────────

    def show_page(self, key: str, help_tab: Optional[str] = None) -> None:
        """
        Zeigt die Seite mit dem gegebenen Key an.

        help_tab: Wenn gesetzt und key=="help", wird der entsprechende Tab
                  in der Hilfe-Seite vorausgewählt.
        """
        # Tool-Nutzung tracken (erscheint in Sentry unter Metrics)
        monitoring.track_tool(key)

        # Alle Seiten ausblenden, gewünschte einblenden
        for page in self._pages.values():
            page.place_forget()
        self._pages[key].place(relx=0, rely=0, relwidth=1, relheight=1)

        # Bei Navigation zur Hilfe: Tab vorauswählen
        if key == "help" and help_tab:
            help_page = self._pages["help"]
            if hasattr(help_page, "show_with_category"):
                help_page.show_with_category(help_tab)

        # Nav-Button-Highlighting: aktive Seite hervorheben
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(fg_color=theme.BG_SURFACE, text_color=theme.TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=theme.TEXT_SECONDARY)

        # Gruppen-Zustand: aktive Gruppe permanent offen, alle anderen schließen
        for meta in self._group_meta:
            if key in meta["keys"]:
                meta["expand"](permanent=True)
            else:
                meta["collapse"](force=True)
