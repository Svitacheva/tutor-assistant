"""Часть 1. Извлечение полей из текста."""

from __future__ import annotations

from .patterns import AUTHOR_PATTERNS, CHILD_ID_PATTERN, ZONE_EXPLICIT_PATTERNS
from .utils import parse_date, parse_sleep_hours


def extract_child_id(text: str) -> str | None:
    """Извлекает ID ребёнка в формате CH-XXXX."""
    match = CHILD_ID_PATTERN.search(text)
    if not match:
        return None
    return f"CH-{match.group(1)}"


def extract_author(text: str) -> str | None:
    """Извлекает автора записи (тьютор/специалист/мама/папа/родители)."""
    for pattern, role in AUTHOR_PATTERNS:
        match = pattern.search(text)
        if match:
            if role in ("мама", "папа", "родители"):
                return role
            name = match.group(1).strip()
            return f"{role} {name}"
    return None


def extract_zone(text: str) -> str | None:
    """Извлекает зону, только если она явно указана в тексте.

    Семантический анализ зон — это Часть 3.
    """
    for pattern, kind in ZONE_EXPLICIT_PATTERNS:
        match = pattern.search(text)
        if match:
            if kind == "explicit":
                return match.group(1).lower()
            return kind
    return None


def extract(text: str) -> dict:
    """Извлекает поля из текста наблюдения.

    Args:
        text: Сырой текст записи.

    Returns:
        Словарь с ключами date, child_id, author, sleep_hours, zone.
        Ненайденные поля равны None.
    """
    return {
        "date": parse_date(text),
        "child_id": extract_child_id(text),
        "author": extract_author(text),
        "sleep_hours": parse_sleep_hours(text),
        "zone": extract_zone(text),
    }