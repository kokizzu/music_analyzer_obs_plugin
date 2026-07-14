#!/usr/bin/env python3
import contextlib
import json
import os
import tempfile
from pathlib import Path

import inspect_musicnet_remote


@contextlib.contextmanager
def patched_env(values):
    previous = {}
    missing = object()
    for key, value in values.items():
        previous[key] = os.environ.get(key, missing)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is missing:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)


def musicnet_record(description=None, files=None, license_id="cc-by-4.0"):
    return {
        "title": "MusicNet",
        "doi_url": "https://doi.org/10.5281/zenodo.5120004",
        "metadata": {
            "license": {"id": license_id},
            "description": description
            if description is not None
            else (
                "MusicNet contains PCM-encoded audio wave files and corresponding "
                "CSV-encoded note label files with the precise time of each note "
                "and the instrument that plays each note."
            ),
        },
        "files": files
        if files is not None
        else [
            {
                "key": "musicnet.tar.gz",
                "size": 11_097_394_998,
                "links": {"self": "https://zenodo.org/api/records/5120004/files/musicnet.tar.gz/content"},
            },
            {
                "key": "musicnet_metadata.csv",
                "size": 43_775,
                "links": {
                    "self": "https://zenodo.org/api/records/5120004/files/musicnet_metadata.csv/content"
                },
            },
            {
                "key": "musicnet_midis.tar.gz",
                "size": 2_601_302,
                "links": {
                    "self": "https://zenodo.org/api/records/5120004/files/musicnet_midis.tar.gz/content"
                },
            },
        ],
    }


def run_remote(record):
    with tempfile.TemporaryDirectory() as temp:
        record_path = Path(temp) / "musicnet.json"
        write_json(record_path, record)
        with patched_env({"MUSIC_ANALYZER_MUSICNET_RECORD_JSON": str(record_path)}):
            return inspect_musicnet_remote.main()


def test_accepts_current_musicnet_record_shape():
    if run_remote(musicnet_record()) != 0:
        raise AssertionError("MusicNet remote metadata should accept current archive shape")


def test_requires_dataset_archive():
    files = [file_info for file_info in musicnet_record()["files"] if file_info["key"] != "musicnet.tar.gz"]
    if run_remote(musicnet_record(files=files)) == 0:
        raise AssertionError("MusicNet remote metadata should require the audio/label archive")


def test_requires_note_label_semantics():
    if run_remote(musicnet_record(description="MusicNet contains classical recordings.")) == 0:
        raise AssertionError("MusicNet remote metadata should require audio, note, and instrument semantics")


def main():
    test_accepts_current_musicnet_record_shape()
    test_requires_dataset_archive()
    test_requires_note_label_semantics()
    print("test_inspect_musicnet_remote: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
