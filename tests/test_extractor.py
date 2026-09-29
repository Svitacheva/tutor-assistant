import json
from pathlib import Path

import pytest

from src.extractor import extract

DATASET = json.loads((Path(__file__).parent.parent / "dataset.json").read_text(encoding="utf-8"))
RECORDS = {r["id"]: r["text"] for r in DATASET["records"]}


def test_extract_r1():
    result = extract(RECORDS["R1"])
    assert result["date"] == "2025-03-05"
    assert result["child_id"] == "CH-0421"
    assert result["sleep_hours"] == 6.5


def test_extract_r2():
    result = extract(RECORDS["R2"])
    assert result["date"] == "2025-03-01"
    assert result["child_id"] == "CH-0107"
    assert result["sleep_hours"] == 6.5
    assert result["zone"] == "моторика"


def test_extract_r3():
    result = extract(RECORDS["R3"])
    assert result["date"] == "2025-03-01"
    assert result["child_id"] == "CH-0342"
    assert result["sleep_hours"] == 5.75


def test_extract_r4():
    result = extract(RECORDS["R4"])
    assert result["date"] == "2025-03-07"
    assert result["child_id"] == "CH-0421"
    assert result["sleep_hours"] == 6.5
    assert result["zone"] == "сенсорика"


def test_extract_r5():
    result = extract(RECORDS["R5"])
    assert result["date"] == "2025-03-12"
    assert result["child_id"] == "CH-0107"
    assert result["sleep_hours"] is None


def test_extract_r6_returns_none():
    result = extract(RECORDS["R6"])
    assert result["date"] is None
    assert result["child_id"] is None
    assert result["sleep_hours"] is None