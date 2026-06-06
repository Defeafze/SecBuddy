import customtkinter as ctk
from app import theme
from app.pages.base_page import BasePage
from app.utils.scam_analyzer import analyze_url, analyze_text, overall_risk, _extract_urls, Finding
from typing import List

_SEVERITY_ICON  = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}
_SEVERITY_COLOR = {"high": "#ef4444", "medium": "#f97316", "low": "#eab308", "info": "#94a3b8"}


class ScamCheckPage(BasePage):
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
            inner, text="Betrugs-Check",
            font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner,
            text="Prüfe verdächtige Links oder Nachrichten — bevor du klickst oder antwortest.",
            font=theme.FONT_BODY, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # ── WICHTIG: Link sicher kopieren ────────────────────────────────────
        warn = ctk.CTkFrame(inner, fg_color="#1c1a09", corner_radius=theme.RADIUS,
                            border_width=1, border_color="#854d0e")
        warn.pack(fill="x", pady=(22, 0))

        ctk.CTkLabel(
            warn, text="⚠️  Wichtig: Link kopieren, ohne ihn zu öffnen!",
            font=theme.FONT_SUBHEADING, text_color="#fbbf24", anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            warn,
            text="Das Öffnen eines Phishing-Links kann bereits gefährlich sein. "
                 "Kopiere ihn so, dass er nicht geöffnet wird:",
            font=theme.FONT_SMALL, text_color="#fde68a",
            anchor="w", justify="left", wraplength=620,
        ).pack(anchor="w", padx=18, pady=(0, 10))

        for platform, steps in [
            ("💻  Am Computer",  [
                'Rechtsklick auf den Link → "Link-Adresse kopieren"  (nicht Links-Klick!)',
                "Wenn der Link als Text kam: Text markieren → Strg+C",
            ]),
            ("📱  Am Handy",     [
                'Link lange gedrückt halten (1–2 Sekunden) → "Link kopieren"',
                "Nicht kurz antippen — das öffnet ihn sofort!",
            ]),
        ]:
            section = ctk.CTkFrame(warn, fg_color="transparent")
            section.pack(fill="x", padx=18, pady=(0, 6))
            ctk.CTkLabel(
                section, text=platform,
                font=("Segoe UI", 11, "bold"), text_color="#fbbf24", anchor="w",
            ).pack(anchor="w", pady=(4, 2))
            for step in steps:
                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x")
                ctk.CTkLabel(row, text="  •", font=theme.FONT_SMALL,
                             text_color="#fbbf24", width=20).pack(side="left", anchor="n", pady=1)
                ctk.CTkLabel(row, text=step, font=theme.FONT_SMALL,
                             text_color="#fde68a", anchor="w", justify="left",
                             wraplength=560).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(warn, fg_color="transparent", height=12).pack()

        # ── Eingabe ──────────────────────────────────────────────────────────
        input_card = ctk.CTkFrame(inner, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        input_card.pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            input_card, text="Link oder Nachrichtentext hier einfügen",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w", padx=18, pady=(14, 8))

        self._text_box = ctk.CTkTextbox(
            input_card,
            font=theme.FONT_BODY,
            fg_color=theme.BG_MAIN, border_color=theme.BORDER, border_width=1,
            text_color=theme.TEXT_PRIMARY,
            height=110, corner_radius=theme.RADIUS,
            wrap="word",
        )
        self._text_box.pack(fill="x", padx=18, pady=(0, 12))

        btn_row = ctk.CTkFrame(input_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))

        self._check_btn = ctk.CTkButton(
            btn_row, text="Prüfen  →", height=42,
            font=theme.FONT_SUBHEADING,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white", corner_radius=theme.RADIUS,
            command=self._run_check,
        )
        self._check_btn.pack(side="left")

        ctk.CTkButton(
            btn_row, text="Leeren", height=42, width=90,
            font=theme.FONT_BODY,
            fg_color="transparent", hover_color=theme.BG_SURFACE,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_MUTED, corner_radius=theme.RADIUS,
            command=self._clear,
        ).pack(side="left", padx=(8, 0))

        # ── Ergebnis-Container ───────────────────────────────────────────────
        self._result_area = ctk.CTkFrame(inner, fg_color="transparent")

        self._help_button(inner, "phishing").pack(fill="x", pady=(20, 0))

    # ── Logik ────────────────────────────────────────────────────────────────

    def _run_check(self) -> None:
        raw = self._text_box.get("1.0", "end").strip()
        if not raw:
            return

        self._clear_results()

        urls = _extract_urls(raw)
        is_single_url = len(raw.split()) == 1 and (raw.startswith("http") or raw.startswith("www."))

        if is_single_url:
            findings = analyze_url(raw)
        else:
            findings = analyze_text(raw)

        self._show_results(findings)

    def _show_results(self, findings: List[Finding]) -> None:
        label, color, progress = overall_risk(findings)

        # Risiko-Anzeige
        risk_card = ctk.CTkFrame(self._result_area, fg_color=theme.BG_SURFACE, corner_radius=theme.RADIUS)
        risk_card.pack(fill="x", pady=(0, 10))

        top = ctk.CTkFrame(risk_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            top, text="Ergebnis:",
            font=theme.FONT_SUBHEADING, text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            top, text=label,
            font=theme.FONT_SUBHEADING, text_color=color,
        ).pack(side="right")

        bar = ctk.CTkProgressBar(
            risk_card, height=8,
            progress_color=color, fg_color=theme.BORDER, corner_radius=4,
        )
        bar.pack(fill="x", padx=18, pady=(0, 14))
        bar.set(progress)

        if not findings:
            ctk.CTkLabel(
                risk_card,
                text="Keine bekannten Betrugsmerkmale gefunden. Trotzdem gilt: Im Zweifel lieber nicht klicken.",
                font=theme.FONT_SMALL, text_color=theme.TEXT_SECONDARY, anchor="w",
            ).pack(anchor="w", padx=18, pady=(0, 14))
        else:
            # Einzelne Befunde
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
            corner_radius=theme.RADIUS,
            border_width=1, border_color=color,
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
        self._text_box.delete("1.0", "end")
        self._clear_results()

    def _clear_results(self) -> None:
        for w in self._result_area.winfo_children():
            w.destroy()
        self._result_area.pack_forget()
