import json
import os
from pathlib import Path


def _saved_mode() -> str:
    try:
        appdata = os.environ.get("APPDATA")
        path = (
            Path(appdata) / "SecBuddy" / "config.json"
            if appdata
            else Path.home() / ".config" / "SecBuddy" / "config.json"
        )
        return json.loads(path.read_text(encoding="utf-8")).get("appearance_mode", "Dark")
    except Exception:
        return "Dark"


_LIGHT = _saved_mode() == "Light"

# ── Farben ────────────────────────────────────────────────────────────────────

if _LIGHT:
    BG_MAIN      = "#f1f5f9"
    BG_SIDEBAR   = "#e2e8f0"
    BG_SURFACE   = "#ffffff"
    ACCENT       = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    TEXT_PRIMARY   = "#0f172a"
    TEXT_SECONDARY = "#334155"
    TEXT_MUTED     = "#64748b"
    SUCCESS     = "#16a34a"
    SUCCESS_BG  = "#f0fdf4"
    DANGER      = "#dc2626"
    DANGER_BG   = "#fef2f2"
    WARNING     = "#d97706"
    BORDER      = "#cbd5e1"
else:
    BG_MAIN      = "#0f172a"
    BG_SIDEBAR   = "#0a101e"
    BG_SURFACE   = "#1e293b"
    ACCENT       = "#3b82f6"
    ACCENT_HOVER = "#2563eb"
    TEXT_PRIMARY   = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED     = "#64748b"
    SUCCESS     = "#22c55e"
    SUCCESS_BG  = "#052e16"
    DANGER      = "#ef4444"
    DANGER_BG   = "#450a0a"
    WARNING     = "#f59e0b"
    BORDER      = "#334155"

# ── Schriften ─────────────────────────────────────────────────────────────────

FONT_TITLE      = ("Segoe UI", 22, "bold")
FONT_HEADING    = ("Segoe UI", 16, "bold")
FONT_SUBHEADING = ("Segoe UI", 13, "bold")
FONT_BODY       = ("Segoe UI", 12)
FONT_SMALL      = ("Segoe UI", 11)
FONT_CAPTION    = ("Segoe UI", 10)

SIDEBAR_WIDTH = 215
RADIUS        = 8
