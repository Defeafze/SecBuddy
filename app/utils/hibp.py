import hashlib
import threading
import requests
from typing import Optional, Callable


def check_password_async(
    password: str,
    callback: Callable[[Optional[int], Optional[str]], None],
) -> None:
    def _run() -> None:
        try:
            sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
            prefix, suffix = sha1[:5], sha1[5:]

            resp = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                headers={"Add-Padding": "true"},
                timeout=8,
            )
            resp.raise_for_status()

            for line in resp.text.splitlines():
                h, count = line.split(":")
                if h == suffix:
                    callback(int(count), None)
                    return
            callback(0, None)

        except requests.Timeout:
            callback(None, "Zeitüberschreitung – bitte Internetverbindung prüfen.")
        except Exception as exc:
            callback(None, f"Fehler: {exc}")

    threading.Thread(target=_run, daemon=True).start()
