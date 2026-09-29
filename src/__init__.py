"""Пакет модулей цифрового помощника тьютора.

Публичный API:
    extract(text) -> dict
    classify(text) -> tuple[str, float]
    check_zone(note, llm=None) -> tuple[bool, float, str]
"""

from __future__ import annotations

from .classifier import classify
from .extractor import extract
from .zone_checker import check_zone

__all__ = ["check_zone", "classify", "extract"]