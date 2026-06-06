import customtkinter as ctk
from app import theme


class BasePage(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color=theme.BG_MAIN, corner_radius=0)
        self._navigate = None   # Gesetzt von app.py via set_navigate()

    def set_navigate(self, fn) -> None:
        """Speichert die App-weite Navigationsfunktion für Help-Buttons."""
        self._navigate = fn

    def _help_button(self, parent: ctk.CTkFrame, help_tab: str) -> ctk.CTkButton:
        """
        Erstellt einen kleinen 'Hilfe & Wissen'-Button am Ende einer Seite.
        help_tab: Kategorie-ID, auf die der Tab der Hilfe-Seite gesetzt wird.
        """
        return ctk.CTkButton(
            parent,
            text="❓  Hilfe & Wissen zu diesem Tool",
            font=theme.FONT_SMALL,
            fg_color="transparent",
            hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED,
            corner_radius=theme.RADIUS,
            height=34,
            anchor="w",
            command=lambda: self._navigate and self._navigate("help", help_tab),
        )
