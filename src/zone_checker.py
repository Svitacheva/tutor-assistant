"""Часть 3. Проверка отнесения наблюдения к отслеживаемым зонам."""

from __future__ import annotations

from .llm_client import LLMClient
from .patterns import TRACKED_ZONES, ZONE_KEYWORDS
from .utils import normalize_text


def _keyword_match(text: str) -> tuple[bool, float, str]:
    """Fallback: сопоставление по ключевым словам.

    Возвращает (in_zone, confidence, explanation).
    """
    normalized = normalize_text(text)
    best_zone: str | None = None
    best_hits = 0

    for zone, keywords in ZONE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in normalized)
        if hits > best_hits:
            best_hits = hits
            best_zone = zone

    if best_zone is None or best_hits == 0:
        return False, 0.5, "Наблюдение не относится к отслеживаемым зонам"

    # Уверенность растёт с числом совпадений, но ограничена 0.95
    confidence = min(0.95, 0.6 + 0.1 * best_hits)
    return True, round(confidence, 2), f"Относится к зоне '{best_zone}'"


def check_zone(note: str, llm: LLMClient | None = None) -> tuple[bool, float, str]:
    """Определяет, относится ли наблюдение к отслеживаемым зонам.

    Args:
        note: Текст наблюдения.
        llm: Опциональный LLM-клиент. Если None или недоступен —
             используется keyword fallback.

    Returns:
        (in_zone, confidence, explanation)
    """
    if not note or not note.strip():
        return False, 0.0, "Пустое наблюдение"

    if llm is not None and llm.available:
        result = llm.check_zone(note, TRACKED_ZONES)
        if result is not None:
            return result

    return _keyword_match(note)