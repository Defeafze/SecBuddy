"""
Einwilligungs-Dialog für anonyme Fehlerberichte und Nutzungsstatistiken.

Die Entscheidung wird in ~/.secbuddy_consent gespeichert und beim nächsten
Start nicht mehr abgefragt — es sei denn, sie wurde widerrufen.
"""

from pathlib import Path
import customtkinter as ctk
from app import theme
from app.utils import i18n

_CONSENT_FILE = Path.home() / ".secbuddy_consent"


def has_decided() -> bool:
    """True wenn der Nutzer bereits eine Entscheidung getroffen hat."""
    return _CONSENT_FILE.exists()


def is_accepted() -> bool:
    """True wenn der Nutzer zugestimmt hat."""
    try:
        return _CONSENT_FILE.read_text().strip() == "yes"
    except OSError:
        return False


def get_status() -> str:
    """Gibt 'accepted', 'declined' oder 'undecided' zurück."""
    if not _CONSENT_FILE.exists():
        return "undecided"
    return "accepted" if is_accepted() else "declined"


def save(accepted: bool) -> None:
    try:
        _CONSENT_FILE.write_text("yes" if accepted else "no")
    except OSError:
        pass


def revoke() -> None:
    """Löscht die gespeicherte Einwilligung, damit beim nächsten Start erneut gefragt wird."""
    try:
        _CONSENT_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def show_dialog(parent: ctk.CTk) -> bool:
    """
    Zeigt den modalen Einwilligungs-Dialog.
    Blockiert bis der Nutzer eine Wahl trifft.
    Gibt True zurück wenn zugestimmt wurde.
    """
    result = [False]

    dialog = ctk.CTkToplevel(parent)
    dialog.title(i18n.t("consent.title"))
    dialog.resizable(False, False)
    dialog.configure(fg_color=theme.BG_MAIN)
    dialog.transient(parent)
    dialog.withdraw()  # Zunächst versteckt — wird nach Layout-Berechnung eingeblendet

    inner = ctk.CTkFrame(dialog, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=32, pady=28)

    # ── Header ──────────────────────────────────────────────────────────────
    ctk.CTkLabel(
        inner, text=i18n.t("consent.header"),
        font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
    ).pack(fill="x")

    ctk.CTkLabel(
        inner,
        text=i18n.t("consent.subtitle"),
        font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        wraplength=456, justify="left",
    ).pack(fill="x", pady=(6, 0))

    # ── Was wird gesammelt ───────────────────────────────────────────────────
    card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
    card.pack(fill="x", pady=(20, 0))

    ctk.CTkLabel(
        card, text=i18n.t("consent.collected"),
        font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
    ).pack(anchor="w", padx=18, pady=(14, 8))

    yes_items = [
        i18n.t("consent.yes1"),
        i18n.t("consent.yes2"),
        i18n.t("consent.yes3"),
    ]
    for item in yes_items:
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=2)
        ctk.CTkLabel(row, text="✅", font=theme.FONT_SMALL,
                     text_color=theme.SUCCESS, width=22).pack(side="left", anchor="n", pady=1)
        ctk.CTkLabel(row, text=item, font=theme.FONT_SMALL,
                     text_color=theme.TEXT_SECONDARY, anchor="w", justify="left",
                     wraplength=390).pack(side="left", fill="x", expand=True)

    ctk.CTkFrame(card, height=1, fg_color=theme.BORDER).pack(fill="x", padx=18, pady=(10, 8))

    no_items = [
        i18n.t("consent.no1"),
        i18n.t("consent.no2"),
        i18n.t("consent.no3"),
    ]
    for item in no_items:
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=2)
        ctk.CTkLabel(row, text="🚫", font=theme.FONT_SMALL,
                     text_color=theme.DANGER, width=22).pack(side="left", anchor="n", pady=1)
        ctk.CTkLabel(row, text=item, font=theme.FONT_SMALL,
                     text_color=theme.TEXT_SECONDARY, anchor="w", justify="left",
                     wraplength=390).pack(side="left", fill="x", expand=True)

    ctk.CTkFrame(card, fg_color="transparent", height=10).pack()

    ctk.CTkLabel(
        inner,
        text=i18n.t("consent.saved"),
        font=theme.FONT_CAPTION, text_color=theme.TEXT_MUTED, anchor="w",
    ).pack(anchor="w", pady=(12, 0))

    # ── Buttons ──────────────────────────────────────────────────────────────
    btn_row = ctk.CTkFrame(inner, fg_color="transparent")
    btn_row.pack(fill="x", pady=(16, 0))

    def _accept():
        result[0] = True
        dialog.destroy()

    def _decline():
        result[0] = False
        dialog.destroy()

    ctk.CTkButton(
        btn_row, text=i18n.t("consent.accept_btn"), height=44,
        font=theme.FONT_SUBHEADING,
        fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
        text_color="white", corner_radius=theme.RADIUS,
        command=_accept,
    ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    ctk.CTkButton(
        btn_row, text=i18n.t("consent.decline_btn"), height=44,
        font=theme.FONT_BODY,
        fg_color="transparent", hover_color=theme.BG_SURFACE,
        border_width=1, border_color=theme.BORDER,
        text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
        command=_decline,
    ).pack(side="left")

    # ── Zentrieren und einblenden ─────────────────────────────────────────────
    def _show_centered():
        parent.update_idletasks()
        dialog.update_idletasks()
        w = 520
        h = dialog.winfo_reqheight()   # tatsächliche Inhaltshöhe
        h = max(h, 400)                # Mindesthöhe
        px = max(0, parent.winfo_x() + (parent.winfo_width()  - w) // 2)
        py = max(30, parent.winfo_y() + (parent.winfo_height() - h) // 2)
        dialog.geometry(f"{w}x{h}+{px}+{py}")
        dialog.deiconify()
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()

    dialog.after(50, _show_centered)

    parent.wait_window(dialog)
    return result[0]