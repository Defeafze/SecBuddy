"""
ml_classifier.py — KI-gestützte Phishing-Erkennung via Hugging Face Transformers.

Das Modell (ealvaradob/bert-finetuned-phishing, ~400 MB) wird einmalig heruntergeladen
und danach vollständig lokal ausgeführt. Erster Start dauert 1–2 Minuten.
"""

from __future__ import annotations
from typing import Optional
import threading

_lock = threading.Lock()
_pipeline = None
_unavailable = False
_loading = False


def is_loaded() -> bool:
    return _pipeline is not None


def is_unavailable() -> bool:
    return _unavailable


def _load() -> None:
    global _pipeline, _unavailable, _loading
    _loading = True
    try:
        from transformers import pipeline as hf_pipeline
        _pipeline = hf_pipeline(
            "text-classification",
            model="ealvaradob/bert-finetuned-phishing",
            truncation=True,
            max_length=512,
        )
    except Exception:
        _unavailable = True
    finally:
        _loading = False


def ensure_loaded_async(callback=None) -> None:
    """Lädt das Modell im Hintergrund. Ruft callback() auf wenn fertig."""
    def worker():
        with _lock:
            if _pipeline is None and not _unavailable:
                _load()
        if callback:
            callback()
    threading.Thread(target=worker, daemon=True).start()


def classify(text: str) -> Optional[dict]:
    """
    Klassifiziert Text als Phishing oder harmlos.
    Gibt {'label': str, 'score': float} zurück oder None bei Fehler / fehlenden Dependencies.
    """
    global _pipeline, _unavailable
    if _unavailable:
        return None
    with _lock:
        if _pipeline is None and not _unavailable:
            _load()
    if _pipeline is None:
        return None
    try:
        results = _pipeline(text[:2000])
        return results[0] if results else None
    except Exception:
        return None
