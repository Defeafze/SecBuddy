"""
phishing_check.py — Phishing & URL-Check (heuristisch, vollständig lokal).

Analysiert eine URL auf bekannte Phishing- und Betrugsmerkmale.
Keine Daten werden an externe Server gesendet.
"""

import threading
import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.scam_analyzer import analyze_url, analyze_text, overall_risk, Finding
from app.utils import monitoring, ml_classifier
from typing import List


_SEVERITY_ICON  = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}
_SEVERITY_COLOR = {"high": "#ef4444", "medium": "#f97316", "low": "#eab308", "info": "#94a3b8"}


class PhishingCheckPage(BasePage):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # ── Seitentitel ──────────────────────────────────────────────────────
        ctk.CTkLabel(
            inner, text="Phishing & URL-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Prüfe einen verdächtigen Link auf Phishing- und Betrugsmerkmale — komplett lokal, kein Internet nötig.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── Info-Karte ───────────────────────────────────────────────────────
        info_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        info_card.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(
            info_card, text="Worauf prüft SecBuddy?",
            font=theme.FONT_SUBHEADING, text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        for line in [
            "Verdächtige Domain-Namen (z. B. paypa1.com statt paypal.com — Buchstabentricks).",
            "Bekannte Phishing-Schlüsselwörter in der URL (login, verify, account-update, …).",
            "Ungewöhnlich lange oder verschachtelte URLs — typisch für Weiterleitungs-Tricks.",
            "IP-Adressen statt Domain-Namen — seriöse Seiten nutzen keine IP-Adressen.",
            "Verdächtige Top-Level-Domains (.xyz, .tk, .pw, …) die häufig für Betrug genutzt werden.",
        ]:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=2)
            ctk.CTkLabel(
                row, text="•", font=theme.FONT_BODY,
                text_color=theme.ACCENT, width=14,
            ).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(
                row, text=line, font=theme.FONT_SMALL,
                text_color=theme.TEXT_SECONDARY, anchor="w",
                justify="left", wraplength=560,
            ).pack(side="left", fill="x", expand=True)
        ctk.CTkFrame(info_card, fg_color="transparent", height=10).pack()

        # ── URL-Eingabe ──────────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            input_card, text="Link eingeben und prüfen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 16))

        self._url_entry = ctk.CTkEntry(
            row,
            placeholder_text="z. B.  https://paypa1-login.xyz   oder  bit.ly/3xYz",
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            height=42, corner_radius=theme.RADIUS,
        )
        self._url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._url_entry.bind("<Return>", lambda _e: self._run_check())

        ctk.CTkButton(
            row, text="Prüfen  →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._run_check,
        ).pack(side="left")

        ctk.CTkButton(
            row, text="Leeren", height=42, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._clear,
        ).pack(side="left", padx=(8, 0))

        # ── Trennlinie ───────────────────────────────────────────────────────
        sep_frame = ctk.CTkFrame(inner, fg_color="transparent")
        sep_frame.pack(fill="x", pady=(20, 0))
        ctk.CTkFrame(sep_frame, fg_color=theme.BORDER, height=1).pack(
            fill="x", side="left", expand=True, padx=(0, 12), pady=8
        )
        ctk.CTkLabel(
            sep_frame, text="ODER", font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED,
        ).pack(side="left")
        ctk.CTkFrame(sep_frame, fg_color=theme.BORDER, height=1).pack(
            fill="x", side="left", expand=True, padx=(12, 0), pady=8
        )

        # ── Text-Analyse (KI-Modell) ─────────────────────────────────────────
        text_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        text_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            text_card, text="E-Mail oder Nachricht analysieren  (KI-gestützt)",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 2))

        ctk.CTkLabel(
            text_card,
            text="Füge den Inhalt einer verdächtigen Nachricht ein. "
                 "Beim ersten Start wird ein KI-Modell einmalig heruntergeladen (~400 MB).",
            font=theme.FONT_SMALL, text_color=theme.TEXT_MUTED,
            anchor="w", wraplength=620, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 8))

        self._text_box = ctk.CTkTextbox(
            text_card,
            height=120,
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN,
            border_color=theme.BORDER,
            border_width=1,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.RADIUS,
        )
        self._text_box.pack(fill="x", padx=18, pady=(0, 10))

        text_btn_row = ctk.CTkFrame(text_card, fg_color="transparent")
        text_btn_row.pack(fill="x", padx=18, pady=(0, 16))

        ctk.CTkButton(
            text_btn_row, text="Analysieren  →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._run_text_check,
        ).pack(side="left")

        ctk.CTkButton(
            text_btn_row, text="Leeren", height=42, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._clear_text,
        ).pack(side="left", padx=(8, 0))

        self._text_status_label = ctk.CTkLabel(
            text_btn_row, text="", font=theme.FONT_SMALL,
            text_color=theme.TEXT_MUTED, anchor="w",
        )
        self._text_status_label.pack(side="left", padx=(14, 0))

        # ── Ergebnis-Container ───────────────────────────────────────────────
        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "phishing").pack(fill="x", pady=(20, 0))

    # ── Logik ────────────────────────────────────────────────────────────────

    def _run_check(self) -> None:
        url = self._url_entry.get().strip()
        if not url:
            return
        monitoring.track_action("phishing_check", "check_url")
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

        ctk.CTkLabel(
            card, text=f"{icon}  {f.title}",
            font=("Segoe UI", 12, "bold"), text_color=color, anchor="w",
        ).pack(anchor="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            card, text=f.detail,
            font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=620,
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def _run_text_check(self) -> None:
        text = self._text_box.get("1.0", "end").strip()
        if not text:
            return
        monitoring.track_action("phishing_check", "check_text")
        self._clear_results()

        if ml_classifier.is_unavailable():
            findings = analyze_text(text)
            self._show_results(findings)
            return

        status_msg = (
            "Modell wird geladen (einmalig) …"
            if not ml_classifier.is_loaded()
            else "Analysiere …"
        )
        self._text_status_label.configure(text=status_msg)

        def worker():
            findings = analyze_text(text)
            ml_result = ml_classifier.classify(text)

            if ml_result:
                label = ml_result.get("label", "").lower()
                score = ml_result.get("score", 0.0)
                if "phishing" in label and score >= 0.85:
                    findings.insert(0, Finding(
                        "high",
                        f"KI-Erkennung: Phishing ({score:.0%} Konfidenz)",
                        "Ein KI-Modell (BERT) hat diese Nachricht mit hoher Wahrscheinlichkeit "
                        "als Phishing eingestuft.",
                    ))
                elif "phishing" in label and score >= 0.55:
                    findings.insert(0, Finding(
                        "medium",
                        f"KI-Erkennung: Möglicherweise Phishing ({score:.0%} Konfidenz)",
                        "Ein KI-Modell stuft diese Nachricht als möglicherweise verdächtig ein.",
                    ))

            self.after(0, lambda: self._finish_text_check(findings))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_text_check(self, findings: List[Finding]) -> None:
        self._text_status_label.configure(text="")
        self._show_results(findings)

    def _clear(self) -> None:
        self._url_entry.delete(0, "end")
        self._clear_results()

    def _clear_text(self) -> None:
        self._text_box.delete("1.0", "end")
        self._text_status_label.configure(text="")
        self._clear_results()

    def _clear_results(self) -> None:
        for w in self._result_area.winfo_children():
            w.destroy()
        self._result_area.pack_forget()
