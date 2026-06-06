import os
import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # ── certifi: cacert.pem Pfad vorab setzen ─────────────────────────────────
    _ca = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
    try:
        import certifi.core
        certifi.core._CACERT_PATH = _ca
    except Exception:
        pass

    # ── SSL-Fallback: load_verify_locations tolerant machen ───────────────────
    try:
        import ssl as _ssl
        _orig_lvl = _ssl.SSLContext.load_verify_locations

        def _safe_load_verify_locations(self, cafile=None, capath=None, cadata=None):
            try:
                return _orig_lvl(self, cafile=cafile, capath=capath, cadata=cadata)
            except (FileNotFoundError, OSError):
                pass

        _ssl.SSLContext.load_verify_locations = _safe_load_verify_locations
    except Exception:
        pass
