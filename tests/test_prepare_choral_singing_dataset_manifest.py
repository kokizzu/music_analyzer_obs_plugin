#!/usr/bin/env python3
"""Regression check for deterministic CSD SATB manifest import."""

from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
from pathlib import Path


PROJECT = Path(__file__).parents[1]
SCRIPT = PROJECT / "scripts" / "prepare_choral_singing_dataset_manifest.py"
SPEC = importlib.util.spec_from_file_location("prepare_csd", SCRIPT)
assert SPEC and SPEC.loader
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "ChoralSingingDataset"
        root.mkdir()
        (root / "README.txt").write_text("fixture", encoding="utf-8")
        for work in IMPORTER.WORKS:
            for role, _ in IMPORTER.ROLES:
                (root / f"CSD_{work}_{role}_notes.lab").write_text("0.0 440.0 1.0\n", encoding="utf-8")
                for index in IMPORTER.SINGER_INDICES:
                    (root / f"CSD_{work}_{role}_{index}.wav").write_bytes(b"fixture")
        output = Path(temporary) / "prepared"
        assert IMPORTER.prepare(root, output, 12) == 12
        pieces = json.loads((output / "manifest.json").read_text(encoding="utf-8"))["pieces"]
        assert len(pieces) == 12
        assert [source["instrument"] for source in pieces[0]["sources"]] == [52, 53, 54, 55]
        with (output / pieces[0]["sources"][0]["notes"]).open(newline="", encoding="utf-8") as source:
            assert next(csv.DictReader(source))["note"] == "69"
        assert IMPORTER.prepare(root, output, 12) == 12
    print("test_prepare_choral_singing_dataset_manifest: 4 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
