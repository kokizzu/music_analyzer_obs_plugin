#!/usr/bin/env python3
"""Regression checks for ESMUC prepared-manifest import."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_esmuc_choir_dataset_manifest as preparer


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "esmuc"
        root.mkdir()
        (root / "README.md").write_text("fixture", encoding="utf-8")
        for role in "SATB":
            stem = root / f"DG_FT_take1_{role}1.wav"
            stem.write_bytes(b"audio")
            stem.with_suffix(".lab").write_text("0.0 440.0 0.5\n", encoding="utf-8")
        (root / "DG_FT_take1_S2.wav").write_bytes(b"audio")
        (root / "DG_FT_take1_S2.lab").write_text("0.0 440.0 0.5\n", encoding="utf-8")
        output = Path(temporary) / "prepared"
        assert preparer.prepare(root, output, 1) == 1
        assert preparer.prepare(root, output, 1) == 1
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["pieces"][0]["id"] == "ESMUC_DG_FT_take1"
        assert [source["instrument"] for source in manifest["pieces"][0]["sources"]] == [52, 53, 54, 55]
    print("test_prepare_esmuc_choir_dataset_manifest: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
