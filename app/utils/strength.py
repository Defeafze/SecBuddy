import string
from typing import Tuple


def calculate_strength(password: str) -> Tuple[int, str, str]:
    """Returns (score 0–4, label, hex color)."""
    score = 0

    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    variety = sum([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in string.punctuation for c in password),
    ])
    if variety >= 2:
        score += 1
    if variety >= 4:
        score += 1

    score = min(4, score)

    levels = [
        "Sehr schwach", "#ef4444",
        "Schwach",      "#f97316",
        "Mittel",       "#f59e0b",
        "Stark",        "#22c55e",
        "Sehr stark",   "#22c55e",
    ]
    label = levels[score * 2]
    color = levels[score * 2 + 1]
    return score, label, color
