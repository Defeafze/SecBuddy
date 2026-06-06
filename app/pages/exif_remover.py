import os
from tkinter import filedialog
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils import exif_strip, monitoring


class ExifRemoverPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._image_path: str | None = None
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Header ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="EXIF-Daten entfernen",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Entferne versteckte Metadaten aus Fotos — GPS-Standort, Kameramodell, Uhrzeit und mehr.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Card ────────────────────────────────────────────────────────
        info = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            info, text="Was steckt in deinen Fotos?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line, color in [
            ("Jedes Smartphone-Foto enthält EXIF-Daten: Aufnahmezeit, Kameramodell — und oft den genauen GPS-Standort.", theme.TEXT_SECONDARY),
            ("Wer dein Foto erhält, kann damit herausfinden wo du wohnst, arbeitest oder täglich bist.", theme.WARNING),
            ("Das Bereinigen erfolgt vollständig lokal — dein Bild wird niemals hochgeladen oder übertragen.", theme.SUCCESS),
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(row, text="•", font=theme.FONT_BODY,
                         text_color=theme.ACCENT, width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=line, font=theme.FONT_SMALL,
                         text_color=color, anchor="w", justify="left",
                         wraplength=580).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(info, fg_color="transparent", height=10).pack()

        # ── Datei auswählen ──────────────────────────────────────────────────
        pick_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        pick_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            pick_card, text="Foto auswählen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            pick_card,
            text="Unterstützte Formate: JPEG (.jpg) und PNG (.png)",
            font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED, anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 8))

        pick_row = ctk.CTkFrame(pick_card, fg_color="transparent")
        pick_row.pack(fill="x", padx=18, pady=(0, 16))

        self._file_label = ctk.CTkLabel(
            pick_row, text="Noch kein Foto ausgewählt",
            font=theme.FONT_BODY, text_color=theme.TEXT_MUTED, anchor="w",
        )
        self._file_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            pick_row, text="📂  Foto öffnen", width=150, height=40,
            font=theme.FONT_BODY,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._pick_file,
        ).pack(side="right")

        # ── Detail-Bereich (wird nach Dateiauswahl befüllt) ──────────────────
        self._detail_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "datenschutz").pack(fill="x", pady=(20, 0))

    # ── Logik ────────────────────────────────────────────────────────────────

    def _pick_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Foto öffnen",
            filetypes=[
                ("Bilder (JPEG / PNG)", "*.jpg *.jpeg *.png"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not path:
            return
        self._image_path = path
        self._file_label.configure(
            text=os.path.basename(path), text_color=theme.TEXT_PRIMARY,
        )
        self._analyse(path)

    def _analyse(self, path: str) -> None:
        for w in self._detail_area.winfo_children():
            w.destroy()
        self._detail_area.pack_forget()

        try:
            with open(path, 'rb') as f:
                data = f.read()
        except OSError as e:
            self._show_error(str(e))
            return

        fmt = exif_strip.detect_format(data)
        if fmt == 'unknown':
            self._show_unsupported()
            return

        meta = exif_strip.read_meta(data)
        self._show_meta_card(meta, len(data))
        self._show_action_card()
        self._detail_area.pack(fill="x", pady=(16, 0))

    def _show_meta_card(self, meta: dict, file_size: int) -> None:
        card = ctk.CTkFrame(
            self._detail_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
        )
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            card, text="Gefundene Metadaten",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 10))

        has_any = (
            meta.get('gps') or meta.get('make') or meta.get('model') or
            meta.get('datetime') or meta.get('software') or meta.get('artist') or
            meta.get('copyright') or meta.get('iptc') or meta.get('xmp') or
            meta.get('png_meta')
        )

        if not has_any:
            ctk.CTkLabel(
                card,
                text="✅  Keine Metadaten gefunden — das Foto ist bereits sauber.",
                font=theme.FONT_BODY, text_color=theme.SUCCESS, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 14))
            return

        rows = []

        if meta.get('gps'):
            rows.append(("📍  GPS-Standort:", "Gefunden  ⚠️", theme.WARNING))
        else:
            rows.append(("📍  GPS-Standort:", "Nicht vorhanden  ✅", theme.SUCCESS))

        if meta.get('make') or meta.get('model'):
            device = " ".join(filter(None, [meta.get('make'), meta.get('model')]))
            rows.append(("📷  Kamera / Gerät:", device, theme.TEXT_SECONDARY))

        if meta.get('datetime'):
            rows.append(("🕐  Aufnahmezeit:", meta['datetime'], theme.TEXT_SECONDARY))

        if meta.get('software'):
            rows.append(("⚙️  Bearbeitet mit:", meta['software'], theme.TEXT_SECONDARY))

        if meta.get('artist'):
            rows.append(("👤  Erstellt von:", meta['artist'], theme.TEXT_SECONDARY))

        if meta.get('copyright'):
            rows.append(("©️  Copyright:", meta['copyright'], theme.TEXT_SECONDARY))

        if meta.get('iptc'):
            rows.append(("📰  IPTC-Daten:", "Gefunden", theme.TEXT_SECONDARY))

        if meta.get('xmp'):
            rows.append(("📋  XMP-Metadaten:", "Gefunden", theme.TEXT_SECONDARY))

        if meta.get('png_meta'):
            rows.append(("🗒️  PNG-Metadaten:", ", ".join(meta['png_meta']), theme.TEXT_SECONDARY))

        for label, value, color in rows:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=3)
            ctk.CTkLabel(
                row, text=label,
                font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED, width=180, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=value,
                font=theme.FONT_SMALL, text_color=color, anchor="w",
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(card, fg_color="transparent", height=12).pack()

    def _show_action_card(self) -> None:
        card = ctk.CTkFrame(
            self._detail_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS,
        )
        card.pack(fill="x")

        ctk.CTkLabel(
            card, text="Metadaten entfernen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            card,
            text="Das bereinigte Foto wird als neue Datei gespeichert — das Original bleibt unverändert.",
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 10))

        self._save_btn = ctk.CTkButton(
            card, text="🧹  EXIF-Daten entfernen & speichern", height=44,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._strip_and_save,
        )
        self._save_btn.pack(fill="x", padx=18, pady=(0, 16))

    def _show_unsupported(self) -> None:
        card = ctk.CTkFrame(
            self._detail_area, fg_color=theme.DANGER_BG, corner_radius=theme.RADIUS,
            border_width=1, border_color=theme.DANGER,
        )
        card.pack(fill="x")
        ctk.CTkLabel(
            card,
            text="Format nicht unterstützt. Bitte eine JPEG- oder PNG-Datei auswählen.",
            font=theme.FONT_BODY, text_color=theme.DANGER, anchor="w",
        ).pack(anchor="w", padx=18, pady=14)
        self._detail_area.pack(fill="x", pady=(16, 0))

    def _show_error(self, msg: str) -> None:
        card = ctk.CTkFrame(
            self._detail_area, fg_color=theme.DANGER_BG, corner_radius=theme.RADIUS,
            border_width=1, border_color=theme.DANGER,
        )
        card.pack(fill="x")
        ctk.CTkLabel(
            card, text=f"Fehler beim Lesen der Datei: {msg}",
            font=theme.FONT_BODY, text_color=theme.DANGER, anchor="w",
        ).pack(anchor="w", padx=18, pady=14)
        self._detail_area.pack(fill="x", pady=(16, 0))

    def _strip_and_save(self) -> None:
        if not self._image_path:
            return
        monitoring.track_action("exif_remover", "strip_exif")

        try:
            with open(self._image_path, 'rb') as f:
                data = f.read()
        except OSError as e:
            self._save_btn.configure(
                text=f"Lesefehler: {e}", fg_color=theme.DANGER_BG, text_color=theme.DANGER,
            )
            return

        clean = exif_strip.strip(data)
        if clean is None:
            self._save_btn.configure(
                text="Format nicht unterstützt.", fg_color=theme.DANGER_BG, text_color=theme.DANGER,
            )
            return

        base, ext = os.path.splitext(os.path.basename(self._image_path))
        save_path = filedialog.asksaveasfilename(
            title="Bereinigtes Foto speichern",
            initialfile=f"{base}_clean{ext}",
            defaultextension=ext,
            filetypes=[
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not save_path:
            return

        try:
            with open(save_path, 'wb') as f:
                f.write(clean)

            saved_kb  = len(clean) // 1024
            before_kb = len(data)  // 1024
            removed_kb = before_kb - saved_kb

            label = f"✅  Gespeichert! Metadaten entfernt ({removed_kb} KB bereinigt)"
            self._save_btn.configure(
                text=label,
                fg_color="transparent",
                border_width=1, border_color=theme.SUCCESS,
                text_color=theme.SUCCESS,
            )
            self.after(5000, lambda: self._save_btn.configure(
                text="🧹  EXIF-Daten entfernen & speichern",
                fg_color=theme.ACCENT, border_width=0, text_color="white",
            ))
        except OSError as e:
            self._save_btn.configure(
                text=f"Speicherfehler: {e}", fg_color=theme.DANGER_BG, text_color=theme.DANGER,
            )
