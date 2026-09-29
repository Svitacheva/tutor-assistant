"""Регулярные выражения, словари и константы.

Все "магические числа" и паттерны собраны здесь с обоснованием.
"""

from __future__ import annotations

import re

# --- Часть 1: извлечение ---

MONTHS_RU: dict[str, int] = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
}

# Порядок важен: сначала более специфичные форматы.
DATE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b"), "dd.mm.yyyy"),
    (re.compile(r"\b(\d{2})\.(\d{2})\.(\d{2})\b"), "dd.mm.yy"),
    (re.compile(r"\b(\d{1,2})\s+([а-яё]+)\s+(\d{4})", re.IGNORECASE), "d month yyyy"),
    (re.compile(r"\b(\d{2})/(\d{2})/(\d{2})\b"), "mm/dd/yy"),  # US-формат
]

# child_id: CH-0421, ch-0421, CH- 0107
CHILD_ID_PATTERN = re.compile(r"\bCH[\s\-]*(\d{3,4})\b", re.IGNORECASE)

# Авторы: роли + ФИО
AUTHOR_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"тьютор[а-я]*\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)?)", re.IGNORECASE), "тьютор"),
    (re.compile(r"тьют\.\s*([А-ЯЁ][а-яё]+)", re.IGNORECASE), "тьютор"),
    (re.compile(r"специалист\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)?)", re.IGNORECASE), "специалист"),
    (re.compile(r"спец\.\s*([А-ЯЁ][а-яё]+)", re.IGNORECASE), "специалист"),
    (re.compile(r"\bмама\s+реб[её]нка\b", re.IGNORECASE), "мама"),
    (re.compile(r"\bпапа\s+реб[её]нка\b", re.IGNORECASE), "папа"),
    (re.compile(r"\bродители\b", re.IGNORECASE), "родители"),
]


# Сон: 6 ч 30 мин / 6,5 часов / 6:30 / 390 минут / 5:45
SLEEP_HM_PATTERN = re.compile(r"(\d+)\s*ч\s*(\d+)\s*мин", re.IGNORECASE)
SLEEP_FLOAT_PATTERN = re.compile(r"(\d+[.,]\d+)\s*час", re.IGNORECASE)
SLEEP_COLON_PATTERN = re.compile(r"\b(\d{1,2}):(\d{2})\b")
SLEEP_MINUTES_PATTERN = re.compile(r"~?\s*(\d+)\s*мин", re.IGNORECASE)

# Явное указание зоны
ZONE_EXPLICIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"зона[:\s]+([а-яё]+)", re.IGNORECASE), "explicit"),
    (re.compile(r"сенсор\.?\s*перегрузка", re.IGNORECASE), "сенсорика"),
    (re.compile(r"сенсорн[а-я]*\s+перегрузка", re.IGNORECASE), "сенсорика"),
]

# --- Часть 2: классификация ---

RECORD_TYPES = ("observation", "lesson_report", "parent_note", "recommendation", "unknown")

# Каждый паттерн: (regex, вес). Веса подобраны так, чтобы 1 сильный
# или 2 средних сигнала давали скор >= 0.5.
HEURISTIC_RULES: dict[str, list[tuple[re.Pattern[str], float]]] = {
    "lesson_report": [
        (re.compile(r"отч[её]т о занятии", re.IGNORECASE), 0.6),
        (re.compile(r"занятие\s*№\s*\d+", re.IGNORECASE), 0.4),
        (re.compile(r"специалист\s+[А-ЯЁ]", re.IGNORECASE), 0.3),
    ],
    "recommendation": [
        (re.compile(r"рекомендац", re.IGNORECASE), 0.6),
        (re.compile(r"рекомендуется", re.IGNORECASE), 0.5),
        (re.compile(r"\bввести\b", re.IGNORECASE), 0.4),
        (re.compile(r"\bследует\b", re.IGNORECASE), 0.4),
    ],
    "parent_note": [
        (re.compile(r"мама\s+реб[её]нка", re.IGNORECASE), 0.6),
        (re.compile(r"папа\s+реб[её]нка", re.IGNORECASE), 0.6),
        (re.compile(r"\bродители\b", re.IGNORECASE), 0.5),
        (re.compile(r"\bдома\b", re.IGNORECASE), 0.3),
    ],
    "observation": [
        (re.compile(r"сон\s+\d", re.IGNORECASE), 0.3),
        (re.compile(r"спал\s+\d", re.IGNORECASE), 0.3),
        (re.compile(r"настроени", re.IGNORECASE), 0.3),
        (re.compile(r"\bел\b", re.IGNORECASE), 0.3),
        (re.compile(r"отказал", re.IGNORECASE), 0.3),
        (re.compile(r"играл", re.IGNORECASE), 0.3),
        (re.compile(r"плакал", re.IGNORECASE), 0.3),
        (re.compile(r"сенсор", re.IGNORECASE), 0.3),
    ],
}

# Порог: топ-1 >= 0.3 и разрыв >= 0.15 → классифицируем.
UNKNOWN_TOP1_THRESHOLD = 0.3
UNKNOWN_GAP_THRESHOLD = 0.15

# --- Часть 3: зоны ---

TRACKED_ZONES = (
    "эмоции", "коммуникация", "поведение", "питание",
    "сенсорика", "сон", "моторика", "самообслуживание",
)

ZONE_KEYWORDS: dict[str, list[str]] = {
    "эмоции": ["плакал", "весёл", "весел", "настроени", "тревог", "радост", "злил", "истерик"],
    "коммуникация": ["речь", "отвечал", "молчал", "обращённ", "обращенн", "жест", "односложн"],
    "поведение": ["ударил", "агресс", "отказался идти", "истерик", "аутоагресс"],
    "питание": ["ел ", "еда", "отказ от еды", "завтрак", "обед", "ужин", "жёлтую еду", "желтую еду", "отодвигал"],
    "сенсорика": ["шум", "уши", "свет", "ламп", "сенсорн", "перегрузк"],
    "сон": ["спал", "заснул", "просыпался", "сон ", "сна"],
    "моторика": ["карандаш", "застегнул", "мелкие предметы", "роняет", "удерживает"],
    "самообслуживание": ["сам застегнул", "оделся", "умылся", "сам ", "впервые сам"],
}