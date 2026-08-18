#!/usr/bin/env python3

import csv
from pathlib import Path
import sys
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inspect_idmt_bass_tempo_metadata  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "idmt.zip"
        output = root / "metadata.tsv"
        with zipfile.ZipFile(archive, "w") as source:
            source.writestr(
                "annotation/001.xml",
                "<annotation><globalParameter><instrument>Bass</instrument>"
                "<tempo>120</tempo><patternLength>2.0</patternLength>"
                "</globalParameter></annotation>",
            )
        assert inspect_idmt_bass_tempo_metadata.main(
            ["--archive", str(archive), "--output", str(output)]
        ) == 0
        with output.open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source, delimiter="\t"))
        assert rows == [
            {"track_id": "001", "parameter": "instrument", "value": "Bass", "timing_or_pattern_field": ""},
            {"track_id": "001", "parameter": "patternLength", "value": "2.0", "timing_or_pattern_field": "yes"},
            {"track_id": "001", "parameter": "tempo", "value": "120", "timing_or_pattern_field": "yes"},
        ]
    print("test_inspect_idmt_bass_tempo_metadata: 1 check passed")


if __name__ == "__main__":
    main()
