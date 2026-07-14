#!/usr/bin/env python3
import json
import os
import sys
import urllib.request


RECORD_URL = "https://zenodo.org/api/records/5120004"


def load_record():
    local_path = os.environ.get("MUSIC_ANALYZER_MUSICNET_RECORD_JSON", "")
    if local_path:
        with open(local_path, "r", encoding="utf-8") as record_file:
            return json.load(record_file)

    with urllib.request.urlopen(RECORD_URL, timeout=30) as response:
        return json.load(response)


def file_by_key(record, key):
    for file_info in record.get("files", []):
        if file_info.get("key") == key:
            return file_info
    return None


def file_url(file_info):
    return file_info.get("links", {}).get("self", "") if file_info else ""


def file_size(file_info):
    size = file_info.get("size", 0) if file_info else 0
    return size if isinstance(size, int) else 0


def format_size(size):
    units = ("B", "KB", "MB", "GB")
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024.0
    return f"{size} B"


def license_id(record):
    return record.get("metadata", {}).get("license", {}).get("id", "")


def description_text(record):
    return record.get("metadata", {}).get("description", "")


def validate_record(record):
    problems = []
    dataset = file_by_key(record, "musicnet.tar.gz")
    metadata = file_by_key(record, "musicnet_metadata.csv")
    midis = file_by_key(record, "musicnet_midis.tar.gz")
    description = description_text(record).lower()

    if "musicnet" not in record.get("title", "").lower():
        problems.append("record title does not identify MusicNet")
    if license_id(record) != "cc-by-4.0":
        problems.append("record license is not cc-by-4.0")
    if not dataset or file_size(dataset) < 10 * 1024 * 1024 * 1024:
        problems.append("record missing musicnet.tar.gz audio/label archive")
    if not metadata or file_size(metadata) < 10 * 1024:
        problems.append("record missing musicnet_metadata.csv")
    if not midis or file_size(midis) < 1 * 1024 * 1024:
        problems.append("record missing musicnet_midis.tar.gz")
    for phrase in (
        "pcm-encoded audio wave files",
        "csv-encoded",
        "precise time of each note",
        "instrument that plays each note",
    ):
        if phrase not in description:
            problems.append(f"record description missing `{phrase}`")

    return problems, dataset, metadata, midis


def main():
    try:
        record = load_record()
    except (OSError, json.JSONDecodeError, urllib.error.URLError) as exc:
        print(f"inspect_musicnet_remote: {exc}", file=sys.stderr)
        return 1

    problems, dataset, metadata, midis = validate_record(record)
    if problems:
        for problem in problems:
            print(f"inspect_musicnet_remote: {problem}", file=sys.stderr)
        return 1

    print(
        "inspect_musicnet_remote: "
        f"record={record.get('doi_url', RECORD_URL)} license={license_id(record)} "
        f"dataset={dataset.get('key')}:{format_size(file_size(dataset))} "
        f"metadata={metadata.get('key')}:{format_size(file_size(metadata))} "
        f"midis={midis.get('key')}:{format_size(file_size(midis))}"
    )
    print(f"inspect_musicnet_remote: dataset_url={file_url(dataset)}")
    print(f"inspect_musicnet_remote: metadata_url={file_url(metadata)}")
    print(f"inspect_musicnet_remote: midis_url={file_url(midis)}")
    print(
        "inspect_musicnet_remote: after extracting musicnet.tar.gz, run "
        "MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet make inspect-real-musicnet"
    )
    print(
        "inspect_musicnet_remote: after extracting musicnet.tar.gz, run "
        "MUSIC_ANALYZER_MUSICNET_ROOT=/path/to/musicnet make test-real-musicnet-20"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
