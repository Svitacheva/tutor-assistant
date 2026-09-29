"""Утилиты: нормализация текста, парсинг дат и времени."""

from __future__ import annotations

from datetime import date

from .patterns import (
    DATE_PATTERNS,
    MONTHS_RU,
    SLEEP_COLON_PATTERN,
    SLEEP_FLOAT_PATTERN,
    SLEEP_HM_PATTERN,
    SLEEP_MINUTES_PATTERN,
)


def normalize_text(text: str) -> str:
    """Приводит текст к нижнему регистру и заменяет ё→е для устойчивости."""
    return text.lower().replace("ё", "е")


def parse_date(text: str) -> str | None:
    """Извлекает дату из текста и возвращает ISO-строку (YYYY-MM-DD).

    Поддерживаемые форматы:
      - 05.03.2025  -> 2025-03-05
      - 07.03.25    -> 2025-03-07
      - 1 марта 2025 г. -> 2025-03-01
      - 03/01/25    -> 2025-03-01 (трактуем как MM/DD/YY)

    Returns:
        ISO-строка или None, если дата не найдена.
    """
    for pattern, fmt in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        try:
            if fmt == "dd.mm.yyyy":
                d, m, y = match.groups()
                return date(int(y), int(m), int(d)).isoformat()
            if fmt == "dd.mm.yy":
                d, m, y = match.groups()
                return date(2000 + int(y), int(m), int(d)).isoformat()
            if fmt == "d month yyyy":
                d, month_name, y = match.groups()
                month = MONTHS_RU.get(month_name.lower().replace("ё", "е"))
                if month is None:
                    continue
                return date(int(y), month, int(d)).isoformat()
            if fmt == "mm/dd/yy":
                m, d, y = match.groups()
                return date(2000 + int(y), int(m), int(d)).isoformat()
        except ValueError:
            # Некорректная дата (например, 32.13.2025) — ищем следующий паттерн
            continue
    return None


def parse_sleep_hours(text: str) -> float | None:
    """Извлекает длительность сна в часах (float).

    Поддерживаемые форматы:
      - "6 ч 30 мин" -> 6.5
      - "6,5 часов"  -> 6.5
      - "6:30"       -> 6.5
      - "390 минут"  -> 6.5
      - "5:45"       -> 5.75

    Returns:
        Часы (float) или None.
    """
    match = SLEEP_HM_PATTERN.search(text)
    if match:
        hours, minutes = int(match.group(1)), int(match.group(2))
        return round(hours + minutes / 60, 2)

    match = SLEEP_FLOAT_PATTERN.search(text)
    if match:
        return round(float(match.group(1).replace(",", ".")), 2)

    match = SLEEP_COLON_PATTERN.search(text)
    if match:
        hours, minutes = int(match.group(1)), int(match.group(2))
        if hours < 24 and minutes < 60:
            return round(hours + minutes / 60, 2)

    match = SLEEP_MINUTES_PATTERN.search(text)
    if match:
        return round(int(match.group(1)) / 60, 2)

    return None