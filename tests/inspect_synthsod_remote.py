#!/usr/bin/env python3
import json
import os
import sys
import urllib.request


AUDIO_RECORD_URL = "https://zenodo.org/api/records/13759492"
SCORES_RECORD_URL = "https://zenodo.org/api/records/14971533"


def load_record(url, env_name):
    local_path = os.environ.get(env_name, "")
    if local_path:
        with open(local_path, "r", encoding="utf-8") as record_file:
            return json.load(record_file)

    with urllib.request.urlopen(url, timeout=30) as response:
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


def validate_records(audio_record, scores_record):
    problems = []
    audio_full = file_by_key(audio_record, "SynthSOD.zip")
    audio_sample = file_by_key(audio_record, "SynthSOD-sample.zip")
    scores_zip = file_by_key(scores_record, "SynthSOD_aligned_scores.zip")
    scores_description = description_text(scores_record).lower()

    if "synthsod" not in audio_record.get("title", "").lower():
        problems.append("audio record title does not identify SynthSOD")
    if license_id(audio_record) != "cc-by-sa-4.0":
        problems.append("audio record license is not cc-by-sa-4.0")
    if not audio_full or file_size(audio_full) < 40 * 1024 * 1024 * 1024:
        problems.append("audio record missing full SynthSOD.zip archive")
    if not audio_sample or file_size(audio_sample) < 1 * 1024 * 1024 * 1024:
        problems.append("audio record missing SynthSOD-sample.zip archive")

    if "aligned scores" not in scores_record.get("title", "").lower():
        problems.append("scores record title does not identify aligned scores")
    if license_id(scores_record) != "cc-by-4.0":
        problems.append("scores record license is not cc-by-4.0")
    if not scores_zip or file_size(scores_zip) < 10 * 1024 * 1024:
        problems.append("scores record missing SynthSOD_aligned_scores.zip archive")
    for phrase in ("start and end time", "midi pitch", "midi instrument"):
        if phrase not in scores_description:
            problems.append(f"scores record description missing `{phrase}`")

    return problems, audio_full, audio_sample, scores_zip


def main():
    try:
        audio_record = load_record(AUDIO_RECORD_URL, "MUSIC_ANALYZER_SYNTHSOD_AUDIO_RECORD_JSON")
        scores_record = load_record(SCORES_RECORD_URL, "MUSIC_ANALYZER_SYNTHSOD_SCORES_RECORD_JSON")
    except (OSError, json.JSONDecodeError, urllib.error.URLError) as exc:
        print(f"inspect_synthsod_remote: {exc}", file=sys.stderr)
        return 1

    problems, audio_full, audio_sample, scores_zip = validate_records(audio_record, scores_record)
    if problems:
        for problem in problems:
            print(f"inspect_synthsod_remote: {problem}", file=sys.stderr)
        return 1

    print(
        "inspect_synthsod_remote: "
        f"audio_record={audio_record.get('doi_url', AUDIO_RECORD_URL)} "
        f"audio_license={license_id(audio_record)} full={audio_full.get('key')}:{format_size(file_size(audio_full))} "
        f"sample={audio_sample.get('key')}:{format_size(file_size(audio_sample))} "
        f"scores_record={scores_record.get('doi_url', SCORES_RECORD_URL)} "
        f"scores_license={license_id(scores_record)} scores={scores_zip.get('key')}:{format_size(file_size(scores_zip))}"
    )
    print(f"inspect_synthsod_remote: sample_url={file_url(audio_sample)}")
    print(f"inspect_synthsod_remote: full_url={file_url(audio_full)}")
    print(f"inspect_synthsod_remote: scores_url={file_url(scores_zip)}")
    print(
        "inspect_synthsod_remote: after downloading sample/full audio and scores zip files, run "
        "MUSIC_ANALYZER_SYNTHSOD_AUDIO_ZIP=/path/to/SynthSOD-sample.zip "
        "MUSIC_ANALYZER_SYNTHSOD_SCORES_ZIP=/path/to/SynthSOD_aligned_scores.zip "
        "make extract-real-synthsod-archives"
    )
    print(
        "inspect_synthsod_remote: after extracting audio and scores, run "
        "MUSIC_ANALYZER_SYNTHSOD_ROOT=/path/to/SynthSOD-data "
        "MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT=/path/to/SynthSOD-aligned-scores "
        "make inspect-real-synthsod && make test-real-synthsod-20"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
