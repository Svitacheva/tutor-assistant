"""Тесты для Части 2: классификация типа записи."""

import json
from pathlib import Path

from src.classifier import classify

DATASET = json.loads(
    (Path(__file__).parent.parent / "dataset.json").read_text(encoding="utf-8")
)
RECORDS = {r["id"]: r["text"] for r in DATASET["records"]}


def test_classify_r1_is_observation():
    record_type, confidence = classify(RECORDS["R1"])
    assert record_type == "observation"
    assert confidence >= 0.5


def test_classify_r2_is_lesson_report():
    record_type, confidence = classify(RECORDS["R2"])
    assert record_type == "lesson_report"
    assert confidence >= 0.5


def test_classify_r3_is_parent_note():
    record_type, confidence = classify(RECORDS["R3"])
    assert record_type == "parent_note"
    assert confidence >= 0.5


def test_classify_r5_is_recommendation():
    record_type, confidence = classify(RECORDS["R5"])
    assert record_type == "recommendation"
    assert confidence >= 0.5


def test_classify_r6_is_observation():
    """R6 — спорный кейс.

    Семантически это observation: есть эмоция («настроение») и
    деятельность («играл»). Отсутствие метаданных (дата, ID, автор)
    не является основанием для unknown — классификатор определяет
    тип записи, а не её полноту.

    Если заказчик потребует unknown — применить штраф за отсутствие
    метаданных (см. RESULTS.md, раздел «Спорные кейсы»).
    """
    record_type, confidence = classify(RECORDS["R6"])
    assert record_type == "observation"
    assert confidence >= 0.5


def test_classify_empty_is_unknown():
    record_type, confidence = classify("")
    assert record_type == "unknown"
    assert confidence == 0.0