#!/usr/bin/env python3
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "tests", "real_dataset_catalog.json")
DOC_PATH = os.path.join(ROOT, "docs", "real_audio_dataset_candidates.md")

ALLOWED_CATEGORIES = {
    "direct_fit",
    "direct_fit_small",
    "truth_no_isolated_stems",
    "synth_multitrack_truth",
    "real_vocal_multitrack_truth",
    "single_instrument_truth",
    "real_stems_weak_truth",
}

REQUIRED_FIELDS = {
    "id",
    "name",
    "category",
    "piece_count",
    "real_audio",
    "isolated_sources",
    "assembled_mix",
    "aligned_symbolic_truth",
    "truth",
    "automation_target",
    "source_url",
    "evidence",
}

OPTIONAL_URL_FIELDS = {
    "annotation_url",
    "download_url",
    "documentation_url",
    "metadata_url",
}

OPTIONAL_STRING_FIELDS = {
    "download_note",
}


def fail(message):
    print(f"inspect_real_dataset_catalog: {message}", file=sys.stderr)
    return 1


def load_json(path):
    with open(path, "r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def load_text(path):
    with open(path, "r", encoding="utf-8") as doc_file:
        return doc_file.read()


def check_dataset_shape(dataset, index):
    missing = sorted(REQUIRED_FIELDS - set(dataset.keys()))
    if missing:
        return f"dataset #{index} missing fields: {', '.join(missing)}"

    if dataset["category"] not in ALLOWED_CATEGORIES:
        return f"{dataset['id']}: invalid category {dataset['category']}"
    if not isinstance(dataset["piece_count"], int) or dataset["piece_count"] < 0:
        return f"{dataset['id']}: piece_count must be a non-negative integer"
    for key in ("real_audio", "isolated_sources", "assembled_mix", "aligned_symbolic_truth"):
        if not isinstance(dataset[key], bool):
            return f"{dataset['id']}: {key} must be boolean"
    for key in ("id", "name", "truth", "automation_target", "source_url", "evidence"):
        if not isinstance(dataset[key], str):
            return f"{dataset['id']}: {key} must be a string"
    if not dataset["source_url"].startswith("https://"):
        return f"{dataset['id']}: source_url must be https"
    for key in OPTIONAL_URL_FIELDS:
        if key in dataset and not isinstance(dataset[key], str):
            return f"{dataset['id']}: {key} must be a string"
        if key in dataset and dataset[key] and not dataset[key].startswith("https://"):
            return f"{dataset['id']}: {key} must be https"
    for key in OPTIONAL_STRING_FIELDS:
        if key in dataset and not isinstance(dataset[key], str):
            return f"{dataset['id']}: {key} must be a string"
    return ""


def main():
    try:
        catalog = load_json(CATALOG_PATH)
        docs = load_text(DOC_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        return fail(str(exc))

    datasets = catalog.get("datasets", [])
    if not isinstance(datasets, list):
        return fail("datasets must be a list")
    if len(datasets) < 15:
        return fail(f"expected at least 15 checked dataset candidates, got {len(datasets)}")

    ids = set()
    for index, dataset in enumerate(datasets, start=1):
        problem = check_dataset_shape(dataset, index)
        if problem:
            return fail(problem)
        if dataset["id"] in ids:
            return fail(f"duplicate dataset id {dataset['id']}")
        ids.add(dataset["id"])
        if dataset["name"] not in docs:
            return fail(f"{dataset['id']}: docs do not mention dataset name {dataset['name']}")

    target_minimum = int(catalog.get("criteria", {}).get("target_minimum_pieces", 20))
    direct_fit = [item for item in datasets if item["category"] == "direct_fit"]
    direct_fit_20 = [item for item in direct_fit if item["piece_count"] >= target_minimum]
    if not direct_fit_20:
        return fail(f"no direct-fit dataset reaches {target_minimum} pieces")

    automated = [item for item in direct_fit_20 if item["automation_target"]]
    if len(automated) != 1 or automated[0]["id"] != "urmp":
        return fail("URMP must be the single automated 20+ direct-fit real-audio gate")
    if automated[0]["automation_target"] != "test-real-multitrack-20":
        return fail("URMP automation target must be test-real-multitrack-20")

    for item in direct_fit:
        if not item["real_audio"] or not item["isolated_sources"] or not item["assembled_mix"]:
            return fail(f"{item['id']}: direct-fit datasets require real audio, sources, and mix")
        if not item["aligned_symbolic_truth"]:
            return fail(f"{item['id']}: direct-fit datasets require aligned symbolic truth")

    for item in datasets:
        if item["category"] == "direct_fit_small" and item["piece_count"] >= target_minimum:
            return fail(f"{item['id']}: direct_fit_small reaches target minimum; reclassify it")
        if item["category"] == "truth_no_isolated_stems" and item["isolated_sources"]:
            return fail(f"{item['id']}: truth_no_isolated_stems cannot claim isolated sources")
        if item["category"] == "real_stems_weak_truth" and item["aligned_symbolic_truth"]:
            return fail(f"{item['id']}: weak-truth stem dataset cannot claim aligned symbolic truth")
        if item["category"] == "single_instrument_truth" and item["assembled_mix"]:
            return fail(f"{item['id']}: single-instrument truth datasets should not claim full mixtures")
        if item["category"] == "real_vocal_multitrack_truth":
            if not (item["real_audio"] and item["isolated_sources"] and item["assembled_mix"]):
                return fail(f"{item['id']}: vocal multitrack datasets require real audio, sources, and mix")
            if not item["aligned_symbolic_truth"]:
                return fail(f"{item['id']}: vocal multitrack datasets require aligned F0 truth")

    print(
        "inspect_real_dataset_catalog: "
        f"checked={len(datasets)} direct_fit={len(direct_fit)} "
        f"direct_fit_20={len(direct_fit_20)} automated={automated[0]['automation_target']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
