import math
import string
from typing import Tuple


def _pool_size(password: str) -> int:
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += 32
    if any(ord(c) > 127 for c in password):
        pool += 128
    return max(pool, 1)


def calculate_entropy(password: str) -> float:
    """Brute-Force-Entropie in Bit: log2(pool_size) × Länge."""
    if not password:
        return 0.0
    return math.log2(_pool_size(password)) * len(password)


def calculate_strength(password: str) -> Tuple[int, str, str, float]:
    """Returns (score 0–4, label, hex color, entropy_bits)."""
    entropy = calculate_entropy(password)

    if entropy < 40:
        score, label, color = 0, "Sehr schwach", "#ef4444"
    elif entropy < 60:
        score, label, color = 1, "Schwach",      "#f97316"
    elif entropy < 80:
        score, label, color = 2, "Mittel",       "#f59e0b"
    elif entropy < 128:
        score, label, color = 3, "Stark",        "#22c55e"
    else:
        score, label, color = 4, "Sehr stark",   "#22c55e"

    return score, label, color, entropy
