#!/usr/bin/env python3
"""Measure whether suppressed one-shot hi-hats have a safe recovery region."""

from collections import Counter
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "build/idmt_drums_primary_attribute_rows.tsv"
HF_PATH = ROOT / "build/hf_drum_kit_primary_attribute_rows.tsv"
SPREAD_PATH = ROOT / "build/drum_spread_exact_attribute_rows.tsv"


def number(row: dict[str, str], name: str) -> float:
    try:
        return float(row.get(name, "0"))
    except ValueError:
        return 0.0


def selected(rows: list[dict[str, str]], band: float, trigger: float) -> list[dict[str, str]]:
    return [
        row for row in rows
        if number(row, "hihat_level") == 0.0
        and number(row, "hihat_band") >= band
        and number(row, "hihat_trigger") >= trigger
    ]


def summary(rows: list[dict[str, str]]) -> str:
    expected = Counter(row.get("expected", "unknown") for row in rows)
    true_count = expected.pop("hihat", 0)
    false_count = sum(expected.values())
    precision = 100.0 * true_count / len(rows) if rows else 0.0
    negatives = ",".join(f"{name}:{count}" for name, count in sorted(expected.items())) or "-"
    return f"total={len(rows):3} hihat={true_count:3} false={false_count:3} precision={precision:5.1f}% negatives={negatives}"


def score(rows: list[dict[str, str]]) -> tuple[int, int, float]:
    truth = sum(row.get("expected") == "hihat" for row in rows)
    precision = truth / len(rows) if rows else 0.0
    return truth, len(rows), precision


def main() -> int:
    if not PATH.exists():
        print(f"missing {PATH.relative_to(ROOT)}; run the IDMT attribute collector first")
        return 1
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    print(f"rows={len(rows)} columns={','.join(rows[0].keys()) if rows else '-'}")
    print("base hihat_level=0 with band/trigger grid")
    for band in (4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0):
        for trigger in (8.0, 12.0, 16.0, 24.0, 32.0, 40.0):
            candidates = selected(rows, band, trigger)
            if candidates:
                print(f"band>={band:4.0f} trigger>={trigger:4.0f} {summary(candidates)}")

    base = selected(rows, 4.0, 8.0)
    numeric_columns = [
        name for name in rows[0]
        if name not in {"sample", "expected", "got", "merged_expected", "hihat_level"}
        and not name.startswith("flag_")
        and all(row.get(name, "").replace(".", "", 1).replace("-", "", 1).isdigit() for row in base)
    ]
    ranked: list[tuple[int, int, float, str]] = []
    for name in numeric_columns:
        values = sorted({number(row, name) for row in base})
        for index in range(1, 10):
            threshold = values[(len(values) - 1) * index // 10]
            for operator in (">=", "<="):
                subset = [
                    row for row in base
                    if number(row, name) >= threshold if operator == ">="
                ] if operator == ">=" else [row for row in base if number(row, name) <= threshold]
                truth, total, precision = score(subset)
                if truth >= 5:
                    ranked.append((truth, total, precision, f"{name}{operator}{threshold:.3f}"))
    ranked.sort(key=lambda item: (item[2], item[0], -item[1]), reverse=True)
    print("best one-attribute subsets with at least five recoverable hi-hats")
    for truth, total, precision, condition in ranked[:16]:
        print(f"{condition:48} hihat={truth:2}/{total:3} precision={precision * 100:5.1f}%")

    print("existing bleed-rule flags among base candidates")
    for name in (name for name in rows[0] if name.startswith("flag_")):
        subset = [row for row in base if number(row, name) != 0.0]
        truth, total, precision = score(subset)
        if total:
            print(f"{name:48} hihat={truth:2}/{total:3} precision={precision * 100:5.1f}%")

    print("cross-corpus proposed recovery: level=0, band>=4, trigger>=8, hihat_seg>=8.938, hihat_shape=1")
    for corpus, path in (("IDMT", PATH), ("HF", HF_PATH), ("spread", SPREAD_PATH)):
        if not path.exists():
            print(f"{corpus}: missing {path.relative_to(ROOT)}")
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            corpus_rows = list(csv.DictReader(handle, delimiter="\t"))
        subset = [
            row for row in corpus_rows
            if number(row, "hihat_level") == 0.0
            and number(row, "hihat_band") >= 4.0
            and number(row, "hihat_trigger") >= 8.0
            and number(row, "hihat_seg") >= 8.938
            and number(row, "hihat_shape") != 0.0
        ]
        print(f"{corpus}: {summary(subset)}")

    print("IDMT proposed-recovery cases")
    proposed = [
        row for row in base
        if number(row, "hihat_seg") >= 8.938
    ]
    for row in proposed:
        print(
            f"{row.get('expected', '?'):5} got={row.get('got', '?'):5} "
            f"hat={number(row, 'hihat_seg'):5.2f} "
            f"shape={row.get('hihat_shape', '?')} high={number(row, 'energy_high'):.2f} "
            f"snare={number(row, 'snare_level'):4.2f} tom={number(row, 'tom_level'):4.2f} "
            f"kick={number(row, 'kick_level'):4.2f} rim={number(row, 'rim_level'):4.2f} "
            f"sample={row.get('sample', '?')}"
        )

    candidates = selected(rows, 4.0, 8.0)
    print("examples for hihat candidates")
    for row in (row for row in candidates if row.get("expected") == "hihat"):
        print(
            f"{row.get('path', '?')} got={row.get('got', '?')} "
            f"band={number(row, 'hihat_band'):.2f} trigger={number(row, 'hihat_trigger'):.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
