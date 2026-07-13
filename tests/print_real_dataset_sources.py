#!/usr/bin/env python3
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "tests", "real_dataset_catalog.json")

CATEGORY_TITLES = {
    "direct_fit": "direct-fit multitrack truth",
    "direct_fit_small": "smaller direct-fit add-ons",
    "truth_no_isolated_stems": "real mixes with symbolic truth but no stems",
    "single_instrument_truth": "single-instrument truth",
    "real_stems_weak_truth": "real stems with weak/no note truth",
}


def piece_label(count):
    return f"{count} piece" if count == 1 else f"{count} pieces"


def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def primary_dataset(catalog):
    target = int(catalog.get("criteria", {}).get("target_minimum_pieces", 20))
    for dataset in catalog.get("datasets", []):
        if (
            dataset.get("category") == "direct_fit"
            and dataset.get("piece_count", 0) >= target
            and dataset.get("automation_target")
        ):
            return dataset
    return None


def print_optional_url(dataset, key, label):
    url = dataset.get(key, "")
    if url:
        print(f"  {label}: {url}")


def print_primary(dataset):
    print("Primary real-audio multitrack target")
    print(f"  dataset: {dataset['name']} ({piece_label(dataset['piece_count'])})")
    print(f"  truth: {dataset['truth']}")
    print(f"  official page: {dataset['source_url']}")
    print_optional_url(dataset, "documentation_url", "documentation")
    print_optional_url(dataset, "download_url", "registration/download")
    note = dataset.get("download_note", "")
    if note:
        print(f"  note: {note}")
    print("  expected root: a directory containing official URMP piece folders")
    print("  expected files: AuMix_*, AuSep_*, Notes_*, and Sco_*.mid")
    print("  combined 20-piece gate: MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-goal-20")
    print("  preflight: MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make inspect-real-multitrack-20")
    print("  20-piece goal gate: MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-multitrack-20")
    print("  full 44-piece gate: MUSIC_ANALYZER_URMP_ROOT=/path/to/URMP make test-real-multitrack-full")


def print_catalog_summary(catalog):
    datasets = catalog.get("datasets", [])
    print()
    print(f"Catalog summary: {len(datasets)} checked public dataset candidates")
    for category, title in CATEGORY_TITLES.items():
        matches = [item for item in datasets if item.get("category") == category]
        if not matches:
            continue
        print(f"{title}:")
        for item in matches:
            automation = item.get("automation_target", "")
            suffix = f", make {automation}" if automation else ""
            print(f"  - {item['name']}: {piece_label(item['piece_count'])}{suffix}")
            print(f"    source: {item['source_url']}")
            if item.get("download_url", ""):
                print(f"    data: {item['download_url']}")
            if item.get("annotation_url", ""):
                print(f"    annotations: {item['annotation_url']}")
            if item.get("metadata_url", ""):
                print(f"    metadata: {item['metadata_url']}")
            if item.get("download_note", ""):
                print(f"    note: {item['download_note']}")


def main():
    try:
        catalog = load_catalog()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"real_dataset_sources: {exc}", file=sys.stderr)
        return 1

    primary = primary_dataset(catalog)
    if primary is None:
        print("real_dataset_sources: no automated 20+ direct-fit dataset found", file=sys.stderr)
        return 1

    print_primary(primary)
    print_catalog_summary(catalog)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
