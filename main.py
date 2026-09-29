"""CLI для прогона пайплайна на тестовых данных."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.classifier import classify
from src.extractor import extract
from src.llm_client import LLMClient
from src.zone_checker import check_zone

DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset() -> dict:
    with DATASET_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def run_extract(records: list[dict]) -> None:
    print("\n=== Часть 1. Извлечение полей ===")
    for rec in records:
        result = extract(rec["text"])
        print(f"\n[{rec['id']}] {rec['text'][:60]}...")
        for k, v in result.items():
            print(f"  {k}: {v}")


def run_classify(records: list[dict]) -> None:
    print("\n=== Часть 2. Классификация ===")
    for rec in records:
        record_type, confidence = classify(rec["text"])
        print(f"[{rec['id']}] {record_type} (confidence={confidence})")


def run_zones(notes: list[str], use_llm: bool) -> None:
    print("\n=== Часть 3. Проверка зон ===")
    llm = LLMClient() if use_llm else None
    if llm and llm.available:
        print("(используется LLM)")
    else:
        print("(используется keyword fallback)")
    for i, note in enumerate(notes, 1):
        in_zone, confidence, explanation = check_zone(note, llm)
        print(f"{i:2d}. {note}\n    -> in_zone={in_zone}, conf={confidence}, {explanation}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tutor Assistant pipeline")
    parser.add_argument("--all", action="store_true", help="Прогнать все части")
    parser.add_argument("--extract", action="store_true", help="Только Часть 1")
    parser.add_argument("--classify", action="store_true", help="Только Часть 2")
    parser.add_argument("--zones", action="store_true", help="Только Часть 3")
    parser.add_argument("--llm", action="store_true", help="Использовать LLM (если доступен)")
    args = parser.parse_args()

    data = load_dataset()

    if args.all or args.extract:
        run_extract(data["records"])
    if args.all or args.classify:
        run_classify(data["records"])
    if args.all or args.zones:
        run_zones(data["zone_notes"], use_llm=args.llm)
    if not any([args.all, args.extract, args.classify, args.zones]):
        parser.print_help()


if __name__ == "__main__":
    main()