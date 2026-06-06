import webbrowser
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils import monitoring


class EmailCheckPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="E-Mail-Leak-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="War deine E-Mail-Adresse in einem Datenleck dabei?",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info: Warum wichtig ──────────────────────────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            info, text="Warum ist das wichtig?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line in [
            "Wenn Hacker eine Webseite angreifen, stehlen sie oft Millionen E-Mail-Adressen auf einmal.",
            "Mit deiner Adresse können sie dich gezielt mit täuschend echten Phishing-Mails anschreiben.",
            "Wenn du weißt, wo du betroffen bist, kannst du sofort handeln — bevor jemand anderes es tut.",
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(row, text="•", font=theme.FONT_BODY,
                         text_color=theme.ACCENT, width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=line, font=theme.FONT_SMALL,
                         text_color=theme.TEXT_SECONDARY, anchor="w",
                         justify="left", wraplength=580).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(info, fg_color="transparent", height=10).pack()

        # ── Eingabe + Button ─────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            input_card, text="E-Mail-Adresse eingeben",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._email_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            row, textvariable=self._email_var,
            placeholder_text="deine@email.de",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=42, corner_radius=theme.RADIUS,
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        entry.bind("<Return>", lambda _e: self._open_browser())

        self._btn = ctk.CTkButton(
            row, text="Im Browser prüfen →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._open_browser,
        )
        self._btn.pack(side="left")

        ctk.CTkLabel(
            input_card,
            text="Öffnet haveibeenpwned.com — die weltweit bekannteste Datenleck-Datenbank. Kostenlos, kein Account nötig.",
            font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # ── Info: Was tun wenn betroffen ─────────────────────────────────────
        action = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        action.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            action, text="Was tun, wenn du betroffen bist?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        steps = [
            ("1.", "Passwort sofort ändern",
             "Geh zur betroffenen Webseite und ändere dein Passwort. Nutze das alte nirgendwo mehr."),
            ("2.", "Zwei-Faktor-Schutz aktivieren",
             "Falls die Seite es anbietet: schalte die Zwei-Schritt-Anmeldung ein. Dann reicht ein gestohlenes Passwort allein nicht mehr."),
            ("3.", "Gleiches Passwort woanders ändern",
             "Wenn du dasselbe Passwort auch auf anderen Seiten nutzt — dort sofort auch ändern."),
            ("4.", "Auf Phishing achten",
             "Rechne damit, dass du gezielte Betrugs-Mails bekommst. Klick keine Links aus unbekannten E-Mails."),
            ("5.", "Bei Bankdaten: Bank informieren",
             "Falls Zahlungsdaten betroffen waren, ruf direkt bei deiner Bank an und lass die Karte prüfen."),
        ]

        for num, title, desc in steps:
            row = ctk.CTkFrame(action, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=(4, 2))

            ctk.CTkLabel(
                row, text=num, font=("Segoe UI", 11, "bold"),
                text_color=theme.ACCENT, width=24,
            ).pack(side="left", anchor="n", pady=2)

            text_col = ctk.CTkFrame(row, fg_color="transparent")
            text_col.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                text_col, text=title,
                font=("Segoe UI", 12, "bold"), text_color=theme.TEXT_PRIMARY, anchor="w",
            ).pack(fill="x")
            ctk.CTkLabel(
                text_col, text=desc,
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
                anchor="w", justify="left", wraplength=560,
            ).pack(fill="x", pady=(1, 0))

        ctk.CTkFrame(action, fg_color="transparent", height=14).pack()

        self._help_button(inner, "account").pack(fill="x", pady=(20, 0))

    def _open_browser(self) -> None:
        monitoring.track_action("email_check", "open_hibp")
        email = self._email_var.get().strip()
        url = f"https://haveibeenpwned.com/?q={email}" if email else "https://haveibeenpwned.com"
        webbrowser.open(url)
        self._btn.configure(text="✅  Geöffnet!", fg_color=theme.SUCCESS)
        self.after(2500, lambda: self._btn.configure(
            text="Im Browser prüfen →", fg_color=theme.ACCENT,
        ))
