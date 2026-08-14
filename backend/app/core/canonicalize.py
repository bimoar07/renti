"""Canonicalization & Obfuscation Analysis (ADR 09).

Normalizes raw text representation to detect intentional obfuscation,
leetspeak, repeated characters, and unicode homoglyphs while preserving
the raw input for user-facing context and audit logs.
"""
import re
import unicodedata

# Basic leet-to-char mapping for Indonesian text safety inspection
LEET_MAP = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "@": "a",
    "5": "s",
    "$": "s",
    "7": "t",
    "8": "b",
}


def canonicalize_text(text: str) -> str:
    """Normalizes whitespace, unicode homoglyphs, and common leetspeak."""
    if not text:
        return ""

    # 1. Normalize Unicode (NFKC)
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Lowercase
    lowered = normalized.lower()

    # 3. Leetspeak substitution
    de_leeted = []
    for char in lowered:
        de_leeted.append(LEET_MAP.get(char, char))
    canonical = "".join(de_leeted)

    # 4. Collapse repeated characters (2+ consecutive occurrences to 1)
    canonical = re.sub(r"(.)\1+", r"\1", canonical)

    # 5. Remove non-alphanumeric trailing punctuation if attached
    canonical = re.sub(r"[!?,.;:]+", " ", canonical)

    # 6. Normalize whitespace and strip
    canonical = re.sub(r"\s+", " ", canonical).strip()

    return canonical
