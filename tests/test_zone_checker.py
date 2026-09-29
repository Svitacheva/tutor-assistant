import json
from pathlib import Path

import pytest

from src.zone_checker import check_zone

DATASET = json.loads((Path(__file__).parent.parent / "dataset.json").read_text(encoding="utf-8"))
NOTES = DATASET["zone_notes"]


@pytest.mark.parametrize("note,expected_zone", [
    ("отказ от еды третий день подряд", True),
    ("ударил себя по голове при смене маршрута", True),
    ("не отвечал на обращённую речь весь день", True),
    ("закрывал уши в столовой из-за шума", True),
    ("заснул только к полуночи, спал 5 часов", True),
    ("впервые сам застегнул куртку", True),
    ("не удерживает карандаш, роняет мелкие предметы", True),
    ("плакал 20 минут без видимой причины", True),
    ("поездка в центр на автобусе заняла 40 минут", False),
    ("родители перенесли занятие на четверг", False),
    ("оформлена справка для поликлиники", False),
    ("ел только жёлтую еду, остальное отодвигал", True),
    ("отказался идти на занятие, потому что шёл дождь", True),
    ("был весёлым на празднике, много бегал и шумел", True),
])
def test_check_zone(note, expected_zone):
    in_zone, _, _ = check_zone(note, llm=None)
    assert in_zone is expected_zone


def test_check_zone_empty():
    in_zone, confidence, _ = check_zone("", llm=None)
    assert in_zone is False
    assert confidence == 0.0