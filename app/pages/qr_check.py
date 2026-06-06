import customtkinter as ctk
from tkinter import filedialog
from app import theme
from app.pages.base_page import BasePage
from app.utils.scam_analyzer import analyze_url, overall_risk, Finding
from app.utils import monitoring
from typing import List

_QR_AVAILABLE = False
try:
    import cv2 as _cv2
    import numpy as _np
    from PIL import Image as _PilImage
    _QR_AVAILABLE = True
except ImportError:
    pass

_SEVERITY_ICON  = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}
_SEVERITY_COLOR = {"high": "#ef4444", "medium": "#f97316", "low": "#eab308", "info": "#94a3b8"}


class QRCheckPage(BasePage):
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
            inner, text="QR-Code Prüfen",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Prüfe ob ein QR-Code auf eine gefährliche Seite führt — bevor du ihn öffnest.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Warnung: QR-Phishing ─────────────────────────────────────────────
        warn = ctk.CTkFrame(inner, fg_color="#1c1a09", corner_radius=theme.RADIUS,
                            border_width=1, border_color="#854d0e")
        warn.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            warn, text="⚠️  Was ist QR-Phishing (Quishing)?",
            font=theme.FONT_SUBHEADING, text_color="#fbbf24", anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        for line in [
            "Betrüger verstecken gefährliche Links in QR-Codes — auf Flyern, Plakaten, Paketen oder in E-Mails.",
            "Das Scannen öffnet oft sofort den Browser, ohne Vorwarnung. Viele Phishing-Filter prüfen QR-Codes nicht.",
            "So gehst du sicher vor: QR-Code mit der Kamera-App scannen, NICHT auf den Link tippen — URL kopieren und hier prüfen.",
        ]:
            row = ctk.CTkFrame(warn, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(row, text="  •", font=theme.FONT_SMALL,
                         text_color="#fbbf24", width=20).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=line, font=theme.FONT_SMALL,
                         text_color="#fde68a", anchor="w", justify="left",
                         wraplength=560).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(warn, fg_color="transparent", height=12).pack()

        # ── URL-Eingabe ──────────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            input_card, text="URL aus dem QR-Code hier einfügen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        self._url_entry = ctk.CTkEntry(
            input_card,
            placeholder_text="https://beispiel.de  — URL, die der QR-Code enthält",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=48, corner_radius=theme.RADIUS,
        )
        self._url_entry.pack(fill="x", padx=18, pady=(0, 12))
        self._url_entry.bind("<Return>", lambda _e: self._run_check())

        btn_row = ctk.CTkFrame(input_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))

        ctk.CTkButton(
            btn_row, text="Prüfen  →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._run_check,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="Leeren", height=42, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._clear,
        ).pack(side="left", padx=(8, 0))

        # ── Bild-Scan (optional, nur wenn pyzbar installiert) ────────────────
        if _QR_AVAILABLE:
            scan_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
            scan_card.pack(fill="x", pady=(12, 0))

            ctk.CTkLabel(
                scan_card, text="Oder: QR-Code-Bild laden und automatisch auslesen",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
            ).pack(anchor="w", padx=18, pady=(14, 4))

            ctk.CTkLabel(
                scan_card,
                text="Screenshot oder Foto eines QR-Codes hochladen — SecBuddy liest die URL automatisch aus.",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 8))

            self._scan_status = ctk.CTkLabel(
                scan_card, text="",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            )
            self._scan_status.pack(anchor="w", padx=18)

            ctk.CTkButton(
                scan_card, text="🖼️  Bild öffnen & auslesen", height=42, width=200,
                font=theme.FONT_BODY,
                fg_color="transparent", hover_color=theme.BG_SURFACE,
                border_width=1, border_color=theme.ACCENT,
                text_color=theme.ACCENT, corner_radius=theme.RADIUS,
                command=self._load_image,
            ).pack(anchor="w", padx=18, pady=(6, 16))

        # ── Ergebnis-Container ───────────────────────────────────────────────
        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "phishing").pack(fill="x", pady=(20, 0))

    # ── Logik ────────────────────────────────────────────────────────────────

    def _load_image(self) -> None:
        path = filedialog.askopenfilename(
            title="QR-Code-Bild öffnen",
            filetypes=[
                ("Bilder", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not path:
            return

        try:
            pil_img = _PilImage.open(path).convert("RGB")
            cv_img  = _cv2.cvtColor(_np.array(pil_img), _cv2.COLOR_RGB2BGR)
            detector = _cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(cv_img)
            if not data:
                self._scan_status.configure(
                    text="❌  Kein QR-Code im Bild erkannt — bitte URL manuell einfügen.",
                    text_color=theme.DANGER,
                )
                return

            url   = data
            short = url[:60] + ("…" if len(url) > 60 else "")
            self._scan_status.configure(
                text=f"✅  QR-Code erkannt: {short}",
                text_color=theme.SUCCESS,
            )
            self._url_entry.delete(0, "end")
            self._url_entry.insert(0, url)
            self._run_check()

        except Exception as exc:
            self._scan_status.configure(
                text=f"Fehler beim Lesen des Bildes: {exc}",
                text_color=theme.DANGER,
            )

    def _run_check(self) -> None:
        url = self._url_entry.get().strip()
        if not url:
            return
        monitoring.track_action("qr_check", "check_qr_url")
        self._clear_results()

        if not url.startswith(("http://", "https://", "www.")):
            url = "https://" + url

        findings = analyze_url(url)
        self._show_results(findings)

    def _show_results(self, findings: List[Finding]) -> None:
        label, color, progress = overall_risk(findings)

        risk_card = ctk.CTkFrame(self._result_area, fg_color=theme.BG_SURFACE,
                                  corner_radius=theme.RADIUS)
        risk_card.pack(fill="x", pady=(0, 10))

        top = ctk.CTkFrame(risk_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(top, text="Ergebnis:",
                     font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY,
                     anchor="w").pack(side="left")
        ctk.CTkLabel(top, text=label,
                     font=theme.FONT_SUBHEADING, text_color=color).pack(side="right")

        bar = ctk.CTkProgressBar(risk_card, height=8,
                                  progress_color=color, fg_color=theme.BORDER, corner_radius=4)
        bar.pack(fill="x", padx=18, pady=(0, 14))
        bar.set(progress)

        if not findings:
            ctk.CTkLabel(
                risk_card,
                text="Keine bekannten Phishing-Merkmale gefunden. Trotzdem gilt: Im Zweifel lieber nicht öffnen.",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 14))
        else:
            ctk.CTkLabel(
                self._result_area, text="Gefundene Warnsignale",
                font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", pady=(4, 6))
            for f in findings:
                self._finding_card(f)

        self._result_area.pack(fill="x", pady=(16, 0))

    def _finding_card(self, f: Finding) -> None:
        color = _SEVERITY_COLOR[f.severity]
        icon  = _SEVERITY_ICON[f.severity]

        card = ctk.CTkFrame(
            self._result_area, fg_color=theme.BG_SURFACE,
            corner_radius=theme.RADIUS, border_width=1, border_color=color,
        )
        card.pack(fill="x", pady=5)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            header, text=f"{icon}  {f.title}",
            font=("Segoe UI", 12, "bold"), text_color=color, anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            card, text=f.detail,
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=620,
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def _clear(self) -> None:
        self._url_entry.delete(0, "end")
        self._clear_results()

    def _clear_results(self) -> None:
        for w in self._result_area.winfo_children():
            w.destroy()
        self._result_area.pack_forget()
