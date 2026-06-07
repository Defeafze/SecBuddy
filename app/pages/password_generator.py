import secrets
import string
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.strength import calculate_strength
from app.utils import monitoring

_SPECIAL = "!@#$%^&*()-_=+[]{}|;:,.<>?"


class PasswordGeneratorPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._build()
        self._generate()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Passwort-Generator",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner, text="Erstelle ein zufälliges, sicheres Passwort — in einer Sekunde.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Card ────────────────────────────────────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            info, text="Was macht ein Passwort sicher?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line, color in [
            ("Länge schlägt alles.  Je länger, desto schwerer zu knacken.", theme.TEXT_SECONDARY),
            ("Abwechslung hilft.  Groß, Klein, Zahlen, Sonderzeichen zusammen.", theme.TEXT_SECONDARY),
            ("Niemals wiederverwenden.  Ein Passwort pro Konto — immer.", theme.WARNING),
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(
                row, text="•", font=theme.FONT_BODY,
                text_color=theme.ACCENT, width=14,
            ).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(
                row, text=line, font=theme.FONT_SMALL,
                text_color=color, anchor="w", justify="left",
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(info, fg_color="transparent", height=10).pack()

        # ── Einstellungen ────────────────────────────────────────────────────
        settings = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        settings.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            settings, text="Einstellungen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 10))

        # Länge
        len_row = ctk.CTkFrame(settings, fg_color="transparent")
        len_row.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkLabel(
            len_row, text="Länge:",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY,
        ).pack(side="left")

        self._len_var = ctk.IntVar(value=20)
        self._len_label = ctk.CTkLabel(
            len_row, text="20",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, width=34,
        )
        self._len_label.pack(side="right")

        ctk.CTkSlider(
            len_row,
            from_=8, to=32, variable=self._len_var, number_of_steps=24,
            button_color=theme.ACCENT, button_hover_color=theme.ACCENT_HOVER,
            progress_color=theme.ACCENT, fg_color=theme.BORDER,
            command=lambda v: self._len_label.configure(text=str(int(v))),
        ).pack(side="left", fill="x", expand=True, padx=(12, 8))

        # Checkboxen
        chk_frame = ctk.CTkFrame(settings, fg_color="transparent")
        chk_frame.pack(fill="x", padx=18, pady=(0, 6))

        self._upper_var   = ctk.BooleanVar(value=True)
        self._digit_var   = ctk.BooleanVar(value=True)
        self._special_var = ctk.BooleanVar(value=True)

        for label, var in [
            ("Großbuchstaben  (A – Z)", self._upper_var),
            ("Zahlen  (0 – 9)",         self._digit_var),
            ("Sonderzeichen  (! @ # …)", self._special_var),
        ]:
            ctk.CTkCheckBox(
                chk_frame, text=label, variable=var,
                font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY,
                fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                border_color=theme.BORDER,
            ).pack(anchor="w", pady=4)

        ctk.CTkButton(
            settings, text="Neues Passwort generieren", height=44,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._generate,
        ).pack(fill="x", padx=18, pady=(10, 16))

        # ── Ergebnis ─────────────────────────────────────────────────────────
        result = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        result.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            result, text="Dein Passwort",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        pw_row = ctk.CTkFrame(result, fg_color="transparent")
        pw_row.pack(fill="x", padx=18)

        self._pw_display = ctk.CTkEntry(
            pw_row, font=("Courier New", 15, "bold"),
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=48, corner_radius=theme.RADIUS,
            state="readonly",
        )
        self._pw_display.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._copy_btn = ctk.CTkButton(
            pw_row, text="📋  Kopieren", width=130, height=48,
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SECONDARY, corner_radius=theme.RADIUS,
            command=self._copy,
        )
        self._copy_btn.pack(side="left")

        # Stärke-Anzeige
        bar_row = ctk.CTkFrame(result, fg_color="transparent")
        bar_row.pack(fill="x", padx=18, pady=(12, 14))

        ctk.CTkLabel(
            bar_row, text="Stärke:",
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
        ).pack(side="left")

        self._strength_bar = ctk.CTkProgressBar(
            bar_row, height=10,
            progress_color=theme.SUCCESS, fg_color=theme.BORDER, corner_radius=5,
        )
        self._strength_bar.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self._strength_bar.set(0)

        self._strength_label = ctk.CTkLabel(
            bar_row, text="", width=90,
            font=theme.FONT_SMALL, text_color=theme.SUCCESS,
        )
        self._strength_label.pack(side="left")

    def _generate(self) -> None:
        monitoring.track_action("password_generator", "generate")
        length = self._len_var.get()

        pool = list(string.ascii_lowercase)
        guaranteed: list[str] = []

        if self._upper_var.get():
            pool += list(string.ascii_uppercase)
            guaranteed.append(secrets.choice(string.ascii_uppercase))
        if self._digit_var.get():
            pool += list(string.digits)
            guaranteed.append(secrets.choice(string.digits))
        if self._special_var.get():
            pool += list(_SPECIAL)
            guaranteed.append(secrets.choice(_SPECIAL))

        remaining = [secrets.choice(pool) for _ in range(length - len(guaranteed))]
        chars = guaranteed + remaining
        secrets.SystemRandom().shuffle(chars)
        pw = "".join(chars)

        self._pw_display.configure(state="normal")
        self._pw_display.delete(0, "end")
        self._pw_display.insert(0, pw)
        self._pw_display.configure(state="readonly")

        score, label, color, entropy = calculate_strength(pw)
        self._strength_bar.configure(progress_color=color)
        self._strength_bar.set(min(entropy / 128, 1.0))
        self._strength_label.configure(text=label, text_color=color)

        self._copy_btn.configure(text="📋  Kopieren", text_color=theme.TEXT_SECONDARY)

    def _copy(self) -> None:
        pw = self._pw_display.get()
        if not pw:
            return
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(pw)
        self._copy_btn.configure(text="✅  Kopiert!", text_color=theme.SUCCESS)
        self.after(2000, lambda: self._copy_btn.configure(
            text="📋  Kopieren", text_color=theme.TEXT_SECONDARY,
        ))
