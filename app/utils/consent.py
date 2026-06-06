"""
Einwilligungs-Dialog für anonyme Fehlerberichte und Nutzungsstatistiken.

Die Entscheidung wird in ~/.secbuddy_consent gespeichert und beim nächsten
Start nicht mehr abgefragt.
"""

from pathlib import Path
import customtkinter as ctk
from app import theme

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


def save(accepted: bool) -> None:
    try:
        _CONSENT_FILE.write_text("yes" if accepted else "no")
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
    dialog.title("Datenschutz-Einstellung")
    dialog.geometry("520x480")
    dialog.resizable(False, False)
    dialog.configure(fg_color=theme.BG_MAIN)

    # Zentrieren relativ zum Hauptfenster
    parent.update_idletasks()
    px = parent.winfo_x() + (parent.winfo_width()  - 520) // 2
    py = parent.winfo_y() + (parent.winfo_height() - 480) // 2
    dialog.geometry(f"520x480+{px}+{py}")

    # Modal — blockiert das Hauptfenster
    dialog.grab_set()
    dialog.focus_force()
    dialog.lift()

    inner = ctk.CTkFrame(dialog, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=32, pady=28)

    # ── Header ──────────────────────────────────────────────────────────────
    ctk.CTkLabel(
        inner, text="🛡️  Kurze Frage vor dem Start",
        font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
    ).pack(fill="x")

    ctk.CTkLabel(
        inner,
        text="Darf SecBuddy anonyme Berichte senden, um besser zu werden?",
        font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        wraplength=456, justify="left",
    ).pack(fill="x", pady=(6, 0))

    # ── Was wird gesammelt ───────────────────────────────────────────────────
    card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
    card.pack(fill="x", pady=(20, 0))

    ctk.CTkLabel(
        card, text="Was würde gesendet werden:",
        font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
    ).pack(anchor="w", padx=18, pady=(14, 8))

    yes_items = [
        "Fehlermeldungen bei Abstürzen — damit Bugs gefunden und behoben werden können.",
        "Welches Tool geöffnet wurde (z. B. 'Fakeshop-Detector') — damit wir wissen, was nützlich ist.",
        "App-Version und Betriebssystem — für die Fehlerdiagnose.",
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
        "Eingaben wie URLs, Passwörter oder E-Mail-Adressen — niemals.",
        "Dateinamen oder Bildinhalte — niemals.",
        "Standort oder IP-Adresse — wird von Sentry automatisch nicht gespeichert.",
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
        text="Deine Entscheidung wird gespeichert und nicht erneut abgefragt.",
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
        btn_row, text="Ja, gerne helfen  ✓", height=44,
        font=theme.FONT_SUBHEADING,
        fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
        text_color="white", corner_radius=theme.RADIUS,
        command=_accept,
    ).pack(side="left", fill="x", expand=True, padx=(0, 8))

    ctk.CTkButton(
        btn_row, text="Nein danke", height=44,
        font=theme.FONT_BODY,
        fg_color="transparent", hover_color=theme.BG_SURFACE,
        border_width=1, border_color=theme.BORDER,
        text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
        command=_decline,
    ).pack(side="left")

    # Warten bis Dialog geschlossen
    parent.wait_window(dialog)
    return result[0]
