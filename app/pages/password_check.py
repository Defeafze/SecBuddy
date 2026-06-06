from typing import Optional
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.hibp import check_password_async
from app.utils import monitoring


class PasswordCheckPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._pw_shown = False
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Passwort-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Wurde dein Passwort schon mal bei einem Datenleck gestohlen?",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Card: Was ist ein Datenleck? ────────────────────────────────
        leak_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        leak_card.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            leak_card, text="Was ist eigentlich ein Datenleck?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line in [
            "Hacker greifen Webseiten an und stehlen dabei die Passwörter aller Nutzer — manchmal Millionen auf einmal.",
            "Diese gestohlenen Daten landen anschließend im Internet und können von jedem heruntergeladen werden.",
            "Nutzt du dasselbe Passwort auf mehreren Seiten, reicht ein einziger Hack — und Angreifer kommen überall rein.",
        ]:
            row = ctk.CTkFrame(leak_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(row, text="•", font=theme.FONT_BODY,
                         text_color=theme.ACCENT, width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=line, font=theme.FONT_SMALL,
                         text_color=theme.TEXT_SECONDARY, anchor="w",
                         justify="left", wraplength=560).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(leak_card, fg_color="transparent", height=10).pack()

        # ── Info-Card: Wie funktioniert die Prüfung? ─────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(
            info, text="Ist die Prüfung sicher?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            info,
            text=(
                "Ja — dein Passwort verlässt dein Gerät nie. SecBuddy berechnet lokal einen\n"
                "unlesbaren Code und schickt nur einen winzigen, bedeutungslosen Ausschnitt\n"
                "davon ab. Selbst wenn jemand die Verbindung abfängt, kann er nichts damit anfangen."
            ),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            justify="left", anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # ── Eingabe ──────────────────────────────────────────────────────────
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
            placeholder_text="Gib dein Passwort ein ...",
            show="●",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=42, corner_radius=theme.RADIUS,
        )
        self._pw_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._pw_entry.bind("<Return>", lambda _e: self._start_check())

        ctk.CTkButton(
            row, text="👁", width=42, height=42,
            font=("Segoe UI", 16),
            fg_color=theme.BG_MAIN, hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.RADIUS,
            command=self._toggle_show,
        ).pack(side="left", padx=(0, 8))

        self._check_btn = ctk.CTkButton(
            row, text="Prüfen  →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._start_check,
        )
        self._check_btn.pack(side="left")

        # ── Ergebnis-Bereich ─────────────────────────────────────────────────
        self._result_container = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "account").pack(fill="x", pady=(20, 0))

    def _toggle_show(self) -> None:
        self._pw_shown = not self._pw_shown
        self._pw_entry.configure(show="" if self._pw_shown else "●")

    def _start_check(self) -> None:
        pw = self._pw_var.get().strip()
        if not pw:
            return
        monitoring.track_action("password_check", "check_hibp")
        self._check_btn.configure(state="disabled", text="Prüfe ...")
        for w in self._result_container.winfo_children():
            w.destroy()
        self._result_container.pack_forget()
        check_password_async(pw, self._on_result)

    def _on_result(self, count: Optional[int], error: Optional[str]) -> None:
        self.after(0, lambda: self._show_result(count, error))

    def _show_result(self, count: Optional[int], error: Optional[str]) -> None:
        self._check_btn.configure(state="normal", text="Prüfen  →")

        if error:
            bg, icon, color = theme.BG_SURFACE, "⚠️", theme.WARNING
            title = "Verbindungsfehler"
            body  = error
        elif count == 0:
            bg, icon, color = theme.SUCCESS_BG, "✅", theme.SUCCESS
            title = "Alles gut!"
            body  = "Dieses Passwort wurde in keinem bekannten Datenleck gefunden."
        else:
            bg, icon, color = theme.DANGER_BG, "🚨", theme.DANGER
            formatted = f"{count:,}".replace(",", ".")
            title = f"Passwort {formatted}× gefunden!"
            body  = (
                "Dieses Passwort ist in Datenlecks aufgetaucht und gilt als unsicher.\n"
                "Bitte ändere es sofort überall, wo du es verwendest."
            )

        card = ctk.CTkFrame(
            self._result_container, fg_color=bg, corner_radius=theme.RADIUS,
        )
        card.pack(fill="x")

        ctk.CTkLabel(
            card, text=f"{icon}  {title}",
            font=theme.FONT_HEADING, text_color=color, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            card, text=body,
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY,
            justify="left", anchor="w", wraplength=640,
        ).pack(anchor="w", padx=18, pady=(0, 14))

        self._result_container.pack(fill="x", pady=(16, 0))
