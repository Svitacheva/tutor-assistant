"""Опциональный LLM-клиент с fallback.

Если GIGACHAT_CREDENTIALS не задан или библиотека недоступна —
available=False, и весь пайплайн работает на эвристиках.

Принцип: любая ошибка LLM не должна ломать пайплайн — вместо этого
возвращаем None, и вызывающий код использует fallback.
"""

from __future__ import annotations

import json
import os
from typing import Any

# Конкретные исключения, которые могут возникнуть при работе с LLM.
# BLE001: не используем blind except Exception — перехватываем только то,
# что реально может произойти.
_LLM_ERRORS: tuple[type[BaseException], ...] = (
    ImportError,           # gigachat не установлен
    ValueError,            # неверные credentials / аргументы
    TypeError,             # неверный тип ответа
    KeyError,              # нет ожидаемого поля в ответе
    AttributeError,        # неожиданная структура объекта
    json.JSONDecodeError,  # ответ не JSON
    ConnectionError,       # сетевые проблемы
    TimeoutError,          # таймаут
    OSError,               # общие ошибки ввода-вывода
)


class LLMClient:
    """Обёртка над GigaChat с graceful degradation.

    Если credentials не заданы или библиотека недоступна — available=False.
    Все методы возвращают None при ошибке, чтобы вызывающий код мог
    использовать эвристический fallback.
    """

    def __init__(self) -> None:
        self.available: bool = False
        self._client: Any = None
        self._try_init()

    def _try_init(self) -> None:
        """Пытается инициализировать GigaChat. При ошибке — available=False."""
        credentials = os.getenv("GIGACHAT_CREDENTIALS")
        if not credentials:
            return

        try:
            from gigachat import GigaChat  # type: ignore[import-not-found]

            self._client = GigaChat(credentials=credentials, verify_ssl_certs=False)
            self.available = True
        except _LLM_ERRORS:
            # Библиотека не установлена, credentials неверны и т.п.
            # Пайплайн продолжит работу на эвристиках.
            self.available = False

    def check_zone(
        self,
        note: str,
        zones: tuple[str, ...],
    ) -> tuple[bool, float, str] | None:
        """Запрашивает у GigaChat отнесение наблюдения к зонам.

        Args:
            note: Текст наблюдения.
            zones: Кортеж отслеживаемых зон.

        Returns:
            (in_zone, confidence, explanation) или None при любой ошибке.
        """
        if not self.available or self._client is None:
            return None

        prompt = (
            f"Относится ли наблюдение к одной из зон: {', '.join(zones)}?\n"
            f"Наблюдение: {note}\n"
            'Верни JSON: {"in_zone": bool, "confidence": float, '
            '"zone": str, "explanation": str}'
        )

        try:
            response = self._client.chat(prompt)
            content = response.choices[0].message.content
            data = json.loads(content)
            return (
                bool(data["in_zone"]),
                float(data["confidence"]),
                str(data["explanation"]),
            )
        except _LLM_ERRORS:
            # Любая проблема с LLM → возвращаем None, fallback сработает.
            return None