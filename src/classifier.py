"""Часть 2. Классификация типа записи.

Модуль определяет тип записи (observation, lesson_report, parent_note,
recommendation, unknown) на основе взвешенных эвристик.

Подход:
    - Каждый паттерн имеет вес.
    - Скор типа = min(1.0, сумма весов сработавших паттернов).
    - Если топ-1 скор ниже порога или разрыв с топ-2 мал — возвращается unknown.

Пороги подобраны эмпирически на R1–R6:
    - R1 (сон + отвечал + односложн + заняти) = 1.0  → observation
    - R2 (отчёт + № + специалист)             = 1.3  → lesson_report
    - R3 (мама ребёнка)                       = 0.6  → parent_note
    - R4 (сон + сенсор)                       = 0.6  → observation
    - R5 (рекомендация + ввести)              = 1.0  → recommendation
    - R6 (настроение + играл)                 = 0.6  → observation (спорный кейс)
"""

from __future__ import annotations

from .patterns import (
    HEURISTIC_RULES,
    UNKNOWN_GAP_THRESHOLD,
    UNKNOWN_TOP1_THRESHOLD,
)
from .utils import normalize_text


def _heuristic_scores(text: str) -> dict[str, float]:
    """Считает взвешенный скор для каждого типа записи.

    Args:
        text: Сырой текст записи.

    Returns:
        Словарь {тип: скор}, где скор — число от 0.0 до 1.0.
    """
    normalized = normalize_text(text)
    scores: dict[str, float] = {}
    for record_type, rules in HEURISTIC_RULES.items():
        total = sum(weight for pattern, weight in rules if pattern.search(normalized))
        scores[record_type] = min(1.0, total)
    return scores


def classify(text: str) -> tuple[str, float]:
    """Классифицирует тип записи.

    Args:
        text: Сырой текст записи.

    Returns:
        Кортеж (тип, уверенность):
            - тип: один из observation, lesson_report, parent_note,
              recommendation, unknown;
            - уверенность: число от 0.0 до 1.0.

    Логика:
        1. Пустой текст → ("unknown", 0.0).
        2. Считаем взвешенные скоры для всех типов.
        3. Сортируем по убыванию.
        4. Если топ-1 < UNKNOWN_TOP1_THRESHOLD → unknown.
        5. Если разрыв топ-1 и топ-2 < UNKNOWN_GAP_THRESHOLD → unknown.
        6. Иначе возвращаем топ-1 тип и его скор.
    """
    if not text or not text.strip():
        return "unknown", 0.0

    scores = _heuristic_scores(text)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    if not ranked or ranked[0][1] == 0.0:
        return "unknown", 0.0

    top1_type, top1_score = ranked[0]
    top2_score = ranked[1][1] if len(ranked) > 1 else 0.0

    if top1_score < UNKNOWN_TOP1_THRESHOLD:
        return "unknown", round(top1_score, 2)
    if (top1_score - top2_score) < UNKNOWN_GAP_THRESHOLD:
        return "unknown", round(top1_score, 2)

    return top1_type, round(top1_score, 2)