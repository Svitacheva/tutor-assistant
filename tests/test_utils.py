import pytest

from src.utils import parse_date, parse_sleep_hours


@pytest.mark.parametrize("text,expected", [
    ("05.03.2025", "2025-03-05"),
    ("07.03.25", "2025-03-07"),
    ("1 марта 2025 г.", "2025-03-01"),
    ("03/01/25", "2025-03-01"),
    ("нет даты", None),
])
def test_parse_date(text, expected):
    assert parse_date(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("6 ч 30 мин", 6.5),
    ("6,5 часов", 6.5),
    ("6:30", 6.5),
    ("390 минут", 6.5),
    ("5:45", 5.75),
    ("~390 минут", 6.5),
    ("нет данных", None),
])
def test_parse_sleep_hours(text, expected):
    assert parse_sleep_hours(text) == expected