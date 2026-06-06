"""
settings_page.py — Einstellungen für SecBuddy.
"""

import os
import sys
import subprocess
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils import config, i18n, consent

_MODE_VALUES = ["Dark", "Light", "System"]


def _restart(root=None) -> None:
    """Startet die App neu — wirkt nach Theme-Wechsel sofort."""
    if getattr(sys, "frozen", False):
        args = [sys.executable]
    else:
        args = [sys.executable] + sys.argv
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(args, creationflags=flags)
    if root is not None:
        try:
            root.destroy()
        except Exception:
            pass
    os._exit(0)


class SettingsPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        ctk.CTkLabel(
            inner, text=i18n.t("settings.title"),
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner, text=i18n.t("settings.subtitle"),
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Darstellung ──────────────────────────────────────────────────────
        app_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        app_card.pack(fill="x", pady=(24, 0))

        ctk.CTkLabel(
            app_card, text=i18n.t("settings.appearance.title"),
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            app_card, text=i18n.t("settings.appearance.desc"),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        saved_mode = config.get("appearance_mode", "Dark")
        self._mode_seg = ctk.CTkSegmentedButton(
            app_card,
            values=_MODE_VALUES,
            command=self._apply_mode,
            fg_color=theme.BG_MAIN,
            selected_color=theme.ACCENT,
            selected_hover_color=theme.ACCENT_HOVER,
            unselected_color=theme.BG_MAIN,
            unselected_hover_color=theme.BG_SURFACE,
            text_color=theme.TEXT_PRIMARY,
            font=theme.FONT_BODY,
        )
        self._mode_seg.set(saved_mode if saved_mode in _MODE_VALUES else "Dark")
        self._mode_seg.pack(anchor="w", padx=18, pady=(0, 18))

        # ── Datenschutz-Einwilligung ─────────────────────────────────────────
        consent_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        consent_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            consent_card, text=i18n.t("settings.consent.title"),
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(16, 4))

        status = consent.get_status()
        status_key = "settings.consent.accepted" if status == "accepted" else "settings.consent.declined"
        self._consent_lbl = ctk.CTkLabel(
            consent_card,
            text=i18n.t(status_key),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
        )
        self._consent_lbl.pack(anchor="w", padx=18, pady=(0, 12))

        btn_row = ctk.CTkFrame(consent_card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=18, pady=(0, 18))

        ctk.CTkButton(
            btn_row,
            text=i18n.t("settings.consent.accept_btn"),
            height=36, font=theme.FONT_BODY,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._consent_accept,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text=i18n.t("settings.consent.decline_btn"),
            height=36, font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._consent_decline,
        ).pack(side="left")

        # ── Hinweis ──────────────────────────────────────────────────────────
        hint = ctk.CTkFrame(inner, fg_color="#0c2340", corner_radius=theme.RADIUS,
                            border_width=1, border_color=theme.ACCENT)
        hint.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            hint, text=i18n.t("settings.appearance.hint.title"),
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            hint,
            text=i18n.t("settings.appearance.hint.body"),
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=640,
        ).pack(anchor="w", padx=18, pady=(0, 14))

    def _apply_mode(self, mode: str) -> None:
        config.set("appearance_mode", mode)
        _restart(self.winfo_toplevel())

    def _consent_accept(self) -> None:
        consent.save(True)
        self._consent_lbl.configure(text=i18n.t("settings.consent.accepted"))

    def _consent_decline(self) -> None:
        consent.revoke()
        root = self.winfo_toplevel()
        root.destroy()
        sys.exit(0)
