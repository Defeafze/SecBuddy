"""
Update-Checker für SecBuddy.

Ruft die GitHub Releases API im Hintergrund ab und ruft einen Callback
auf sobald eine neuere Version gefunden wird.

GitHub Releases API:
  GET https://api.github.com/repos/{owner}/{repo}/releases/latest
  → JSON mit tag_name, html_url, body (Changelog), published_at
"""

import threading
import requests


def check(owner: str, repo: str, current_version: str, on_update) -> None:
    """
    Prüft im Hintergrund ob eine neue Version auf GitHub verfügbar ist.

    on_update(version, url, notes) wird aufgerufen wenn eine neuere
    Version gefunden wurde — ACHTUNG: läuft im Background-Thread,
    UI-Updates müssen mit widget.after(0, ...) in den Main-Thread.
    """
    if not owner or not repo:
        return

    def _worker():
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
                timeout=8,
                headers={"Accept": "application/vnd.github+json"},
            )
            if resp.status_code != 200:
                return

            data     = resp.json()
            tag      = data.get("tag_name", "").lstrip("v")
            html_url = data.get("html_url", "")
            notes    = data.get("body", "") or ""

            if tag and _is_newer(tag, current_version):
                on_update(tag, html_url, notes.strip())

        except Exception:
            pass  # Netzwerkfehler o. Ä. → still ignorieren

    threading.Thread(target=_worker, daemon=True).start()


def _is_newer(latest: str, current: str) -> bool:
    """Gibt True zurück wenn latest > current (semantische Versionierung)."""
    try:
        def _parse(v: str) -> tuple:
            return tuple(int(x) for x in v.split(".")[:3])
        return _parse(latest) > _parse(current)
    except Exception:
        return False
