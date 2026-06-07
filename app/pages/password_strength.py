"""
password_strength.py — Passwort-Stärke-Check.

Analysiert ein eingegebenes Passwort live auf Stärke-Kriterien.
Alles läuft lokal — das Passwort verlässt niemals das Gerät.
"""

import string
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.strength import calculate_strength
from app.utils import monitoring


# Farben für die Kriterien-Checkboxen
_OK  = theme.SUCCESS
_FAIL = theme.TEXT_MUTED


class PasswordStrengthPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._shown = False
        self._tracked = False
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ───��──────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Passwort-Stärke-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            inner,
            text="Sieh sofort, wie stark dein Passwort wirklich ist — und was du verbessern kannst.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Datenschutz-Hinweis ──────────────────────────────────────────────
        priv = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        priv.pack(fill="x", pady=(20, 0))
        ctk.CTkLabel(
            priv,
            text="🔒  Dein Passwort verlässt niemals dein Gerät. Die Analyse läuft vollständig lokal.",
            font=theme.FONT_SMALL, text_color=theme.SUCCESS, anchor="w",
        ).pack(anchor="w", padx=18, pady=12)

        # ── Eingabe ─────────────────────────────────��────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))
        ctk.CTkLabel(
            input_card, text="Passwort eingeben",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._pw_var = ctk.StringVar()
        self._pw_entry = ctk.CTkEntry(
            row, textvariable=self._pw_var,
            placeholder_text="Passwort hier eingeben …",
            show="●",
            font=("Courier New", 13),
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=44, corner_radius=theme.RADIUS,
        )
        self._pw_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row, text="👁", width=44, height=44,
            font=("Segoe UI", 16),
            fg_color=theme.BG_MAIN, hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SECONDARY, corner_radius=theme.RADIUS,
            command=self._toggle_show,
        ).pack(side="left")

        # Jede Tastatureingabe triggert die Live-Analyse
        self._pw_var.trace_add("write", lambda *_: self._analyze())

        # ── Stärke-Anzeige ─────────���─────────────────────────���───────────────
        strength_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        strength_card.pack(fill="x", pady=(16, 0))

        top = ctk.CTkFrame(strength_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(
            top, text="Stärke:",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(side="left")
        self._entropy_label = ctk.CTkLabel(
            top, text="",
            font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED,
        )
        self._entropy_label.pack(side="right")
        self._strength_label = ctk.CTkLabel(
            top, text="—",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_MUTED,
        )
        self._strength_label.pack(side="right", padx=(0, 16))

        self._strength_bar = ctk.CTkProgressBar(
            strength_card, height=10,
            progress_color=theme.TEXT_MUTED, fg_color=theme.BORDER, corner_radius=5,
        )
        self._strength_bar.pack(fill="x", padx=18, pady=(0, 16))
        self._strength_bar.set(0)

        # ── Kriterien-Checkliste ─���───────────────────────────────────────────
        crit_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        crit_card.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(
            crit_card, text="Kriterien",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        # Jedes Kriterium: (Label, Funktionsname zum Prüfen)
        criteria = [
            ("Mindestens 8 Zeichen",                 "_crit_len8"),
            ("Mindestens 12 Zeichen (empfohlen)",     "_crit_len12"),
            ("Mindestens 16 Zeichen (sehr sicher)",   "_crit_len16"),
            ("Kleinbuchstaben (a – z)",               "_crit_lower"),
            ("Großbuchstaben (A – Z)",                "_crit_upper"),
            ("Zahlen (0 – 9)",                        "_crit_digit"),
            ("Sonderzeichen (! @ # $ …)",             "_crit_special"),
        ]

        self._crit_labels = {}
        for label, key in criteria:
            row = ctk.CTkFrame(crit_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=3)
            # Checkbox-Icon (wird live aktualisiert)
            icon_lbl = ctk.CTkLabel(row, text="○", font=theme.FONT_BODY,
                                    text_color=_FAIL, width=22)
            icon_lbl.pack(side="left", anchor="n", pady=1)
            text_lbl = ctk.CTkLabel(row, text=label, font=theme.FONT_SMALL,
                                    text_color=_FAIL, anchor="w")
            text_lbl.pack(side="left", fill="x", expand=True)
            self._crit_labels[key] = (icon_lbl, text_lbl)

        ctk.CTkFrame(crit_card, fg_color="transparent", height=10).pack()

        # ── Tipps ────��───────────────────────────────────────────────────────
        tips_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        tips_card.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(
            tips_card, text="Tipps für ein starkes Passwort",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))
        for tip in [
            "Länge ist das Wichtigste — 16+ Zeichen sind besser als kurze komplexe Passwörter.",
            "Nutze den Passwort-Generator für ein vollständig zufälliges, starkes Passwort.",
            "Verwende niemals dasselbe Passwort für mehrere Konten.",
            "Ein Passwort-Manager merkt sie alle — du brauchst dir nur ein Masterpasswort.",
        ]:
            r = ctk.CTkFrame(tips_card, fg_color="transparent")
            r.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(r, text="•", font=theme.FONT_BODY,
                         text_color=theme.ACCENT, width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(r, text=tip, font=theme.FONT_SMALL,
                         text_color=theme.TEXT_SECONDARY, anchor="w",
                         justify="left", wraplength=560).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(tips_card, fg_color="transparent", height=10).pack()

        # ── Hilfe-Button ─────────────────────────────────────────────────────
        self._help_button(inner, "passwort").pack(fill="x", pady=(20, 0))

    # ── Logik ──────���──────────────────────────────────────────────────────────

    def _toggle_show(self) -> None:
        self._shown = not self._shown
        self._pw_entry.configure(show="" if self._shown else "●")

    def _analyze(self) -> None:
        pw = self._pw_var.get()
        if not pw:
            self._tracked = False
            self._strength_bar.set(0)
            self._strength_bar.configure(progress_color=theme.TEXT_MUTED)
            self._strength_label.configure(text="—", text_color=theme.TEXT_MUTED)
            self._entropy_label.configure(text="")
            for key in self._crit_labels:
                self._set_crit(key, False)
            return
        if not self._tracked:
            self._tracked = True
            monitoring.track_action("password_strength", "analyze")

        score, label, color, entropy = calculate_strength(pw)
        # Progress-Bar: 128 Bit = volle Balken, danach gekappt
        self._strength_bar.set(min(entropy / 128, 1.0))
        self._strength_bar.configure(progress_color=color)
        self._strength_label.configure(text=label, text_color=color)
        self._entropy_label.configure(text=f"{entropy:.1f} Bit", text_color=color)

        # Kriterien auswerten
        has_lower   = any(c.islower()            for c in pw)
        has_upper   = any(c.isupper()            for c in pw)
        has_digit   = any(c.isdigit()            for c in pw)
        has_special = any(c in string.punctuation for c in pw)

        self._set_crit("_crit_len8",    len(pw) >= 8)
        self._set_crit("_crit_len12",   len(pw) >= 12)
        self._set_crit("_crit_len16",   len(pw) >= 16)
        self._set_crit("_crit_lower",   has_lower)
        self._set_crit("_crit_upper",   has_upper)
        self._set_crit("_crit_digit",   has_digit)
        self._set_crit("_crit_special", has_special)

    def _set_crit(self, key: str, ok: bool) -> None:
        icon_lbl, text_lbl = self._crit_labels[key]
        if ok:
            icon_lbl.configure(text="✓", text_color=_OK)
            text_lbl.configure(text_color=_OK)
        else:
            icon_lbl.configure(text="○", text_color=_FAIL)
            text_lbl.configure(text_color=_FAIL)
