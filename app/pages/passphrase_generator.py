import secrets
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils import monitoring

_WORDS = sorted(set([
    "Abend", "Achse", "Ahorn", "Amsel", "Anker", "Apfel", "Atlas", "Aula", "Axt",
    "Basis", "Baum", "Becher", "Berg", "Birne", "Boden", "Boot", "Brief", "Brot",
    "Brücke", "Burg", "Clown", "Couch", "Dachs", "Dampf", "Depot", "Docht", "Donau",
    "Dorf", "Draht", "Ebene", "Eiche", "Eimer", "Eis", "Elch", "Erle", "Ernte",
    "Esel", "Fackel", "Falke", "Farbe", "Fasan", "Feder", "Fels", "Feuer", "Fisch",
    "Flöte", "Frost", "Frucht", "Fuchs", "Gabel", "Geist", "Gemse", "Gipfel",
    "Gras", "Grube", "Hafen", "Hafer", "Haken", "Hauch", "Herbst", "Hecht", "Hemd",
    "Hirsch", "Hund", "Igel", "Ikone", "Iltis", "Insel", "Jacke", "Jagd", "Jaguar",
    "Kamin", "Kamel", "Karte", "Katze", "Kegel", "Kelch", "Kessel", "Kiefer",
    "Kiste", "Knochen", "Knopf", "Kreis", "Kreuz", "Krone", "Krug", "Lamm",
    "Lampe", "Laser", "Laub", "Laube", "Lauch", "Lawine", "Leder", "Licht",
    "Linde", "Luchs", "Mango", "Maske", "Mauer", "Meise", "Moos", "Mühle",
    "Muschel", "Nagel", "Nacht", "Narbe", "Nebel", "Nest", "Nixe", "Nuss",
    "Obst", "Ochse", "Ofen", "Opal", "Orden", "Otter", "Palme", "Panda", "Papst",
    "Perle", "Pfad", "Pfeil", "Pferd", "Pilz", "Pinsel", "Probe", "Quarz",
    "Qualle", "Regen", "Rinde", "Roggen", "Rose", "Röhre", "Rüssel", "Säge",
    "Salat", "Salz", "Sand", "Schal", "Schloss", "Schuh", "Schwan", "Seife",
    "Sirup", "Socke", "Specht", "Stahl", "Stall", "Stern", "Stroh", "Taube",
    "Teich", "Tempel", "Tiger", "Tinte", "Tisch", "Topf", "Torf", "Turm",
    "Ufer", "Ulme", "Umweg", "Vasen", "Vektor", "Venus", "Vogel", "Waben",
    "Wachs", "Wald", "Wanze", "Welle", "Wiese", "Wimpel", "Wolke", "Wurm",
    "Yacht", "Yucca", "Zaun", "Zebra", "Zeder", "Zange", "Ziel", "Ziege", "Zirkel", "Zwerg",
]))

_SEPS = [
    ("-",  "Bindestrich  (Wort-Wort)"),
    (" ",  "Leerzeichen  (Wort Wort)"),
    (".",  "Punkt  (Wort.Wort)"),
    ("_",  "Unterstrich  (Wort_Wort)"),
]


class PassphraseGeneratorPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._sep_var = None
        self._build()
        self._generate()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Passphrasen-Generator",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Erstelle ein leicht merkbares Passwort aus echten Wörtern — aber trotzdem sicher.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Card ────────────────────────────────────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            info, text="Was ist eine Passphrase?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line, color in [
            ('Statt "X#9kL!2m" einfach "Apfel-Tiger-Mauer-27" — länger, sicherer, merkbar.', theme.TEXT_SECONDARY),
            ("4 zufällige Wörter = ~50 Bits Entropie. Das dauert Millionen Jahre zum Knacken.", theme.TEXT_SECONDARY),
            ("Alles läuft lokal — die Passphrase verlässt niemals dein Gerät.", theme.SUCCESS),
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(row, text="•", font=theme.FONT_BODY,
                         text_color=theme.ACCENT, width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=line, font=theme.FONT_SMALL,
                         text_color=color, anchor="w", justify="left",
                         wraplength=580).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(info, fg_color="transparent", height=10).pack()

        # ── Einstellungen ────────────────────────────────────────────────────
        settings = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        settings.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            settings, text="Einstellungen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 10))

        # Anzahl Wörter
        word_row = ctk.CTkFrame(settings, fg_color="transparent")
        word_row.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkLabel(word_row, text="Wörter:",
                     font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY).pack(side="left")

        self._word_count_var = ctk.IntVar(value=4)
        self._word_count_label = ctk.CTkLabel(
            word_row, text="4",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, width=34,
        )
        self._word_count_label.pack(side="right")

        ctk.CTkSlider(
            word_row, from_=3, to=6, variable=self._word_count_var, number_of_steps=3,
            button_color=theme.ACCENT, button_hover_color=theme.ACCENT_HOVER,
            progress_color=theme.ACCENT, fg_color=theme.BORDER,
            command=lambda v: self._word_count_label.configure(text=str(int(v))),
        ).pack(side="left", fill="x", expand=True, padx=(12, 8))

        # Trennzeichen
        sep_row = ctk.CTkFrame(settings, fg_color="transparent")
        sep_row.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkLabel(sep_row, text="Trennzeichen:",
                     font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY).pack(side="left")

        self._sep_var = ctk.StringVar(value="-")
        self._sep_display_var = ctk.StringVar(value=_SEPS[0][1])
        ctk.CTkOptionMenu(
            sep_row,
            variable=self._sep_display_var,
            values=[s[1] for s in _SEPS],
            fg_color=theme.BG_MAIN, button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_HOVER, text_color=theme.TEXT_PRIMARY,
            font=theme.FONT_BODY, corner_radius=theme.RADIUS,
            command=self._on_sep_change,
            width=240,
        ).pack(side="right")

        # Optionen
        opt_frame = ctk.CTkFrame(settings, fg_color="transparent")
        opt_frame.pack(fill="x", padx=18, pady=(0, 6))

        self._capitalize_var = ctk.BooleanVar(value=True)
        self._add_number_var  = ctk.BooleanVar(value=True)

        for label, var in [
            ("Ersten Buchstaben groß schreiben", self._capitalize_var),
            ("Zahl anhängen  (z. B. -42)", self._add_number_var),
        ]:
            ctk.CTkCheckBox(
                opt_frame, text=label, variable=var,
                font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY,
                fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                border_color=theme.BORDER,
            ).pack(anchor="w", pady=4)

        ctk.CTkButton(
            settings, text="Neue Passphrase generieren", height=44,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._generate,
        ).pack(fill="x", padx=18, pady=(10, 16))

        # ── Ergebnis ─────────────────────────────────────────────────────────
        result = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        result.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(result, text="Deine Passphrase",
                     font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
                     ).pack(anchor="w", padx=18, pady=(14, 8))

        pw_row = ctk.CTkFrame(result, fg_color="transparent")
        pw_row.pack(fill="x", padx=18)

        self._pp_display = ctk.CTkEntry(
            pw_row, font=("Courier New", 14, "bold"),
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY, height=48, corner_radius=theme.RADIUS,
            state="readonly",
        )
        self._pp_display.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._copy_btn = ctk.CTkButton(
            pw_row, text="📋  Kopieren", width=130, height=48,
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SECONDARY, corner_radius=theme.RADIUS,
            command=self._copy,
        )
        self._copy_btn.pack(side="left")

        ctk.CTkFrame(result, fg_color="transparent", height=14).pack()

        self._help_button(inner, "passwort").pack(fill="x", pady=(20, 0))

    def _on_sep_change(self, display: str) -> None:
        for sep, label in _SEPS:
            if label == display:
                self._sep_var.set(sep)
                break
        self._generate()

    def _generate(self) -> None:
        if self._sep_var is None:
            return
        monitoring.track_action("passphrase_generator", "generate")
        count = int(self._word_count_var.get())
        sep   = self._sep_var.get()

        words = [secrets.choice(_WORDS) for _ in range(count)]

        if self._capitalize_var.get():
            words = [w.capitalize() for w in words]

        phrase = sep.join(words)

        if self._add_number_var.get():
            phrase += sep + str(secrets.randbelow(90) + 10)

        self._pp_display.configure(state="normal")
        self._pp_display.delete(0, "end")
        self._pp_display.insert(0, phrase)
        self._pp_display.configure(state="readonly")

        self._copy_btn.configure(text="📋  Kopieren", text_color=theme.TEXT_SECONDARY)

    def _copy(self) -> None:
        pp = self._pp_display.get()
        if not pp:
            return
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(pp)
        self._copy_btn.configure(text="✅  Kopiert!", text_color=theme.SUCCESS)
        self.after(2000, lambda: self._copy_btn.configure(
            text="📋  Kopieren", text_color=theme.TEXT_SECONDARY,
        ))
