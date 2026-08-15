#!/usr/bin/env python3
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


PROJECT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
SCRIPT = PROJECT / "scripts" / "prepare_kraisler_manifest.py"
SPEC = importlib.util.spec_from_file_location("prepare_kraisler", SCRIPT)
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)
sys.path.insert(0, str(PROJECT / "tests"))
from generate_maestro_fixture import write_midi


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "KRAISLER"
        wav = root / "performance_wav"
        midi = root / "performance_midi"
        notes = root / "annotation_csv"
        for directory in (wav, midi, notes):
            directory.mkdir(parents=True)
        for index in range(1, 3):
            track = f"{index:02d}"
            for configuration in IMPORTER.CONFIGURATIONS:
                (wav / f"{track}_PF_{configuration}.wav").write_bytes(b"piano")
                (wav / f"{track}_VN_{configuration}.wav").write_bytes(b"violin")
                (wav / f"{track}_mix_{configuration}.wav").write_bytes(b"mixture")
            write_midi(str(midi / f"{track}_PF.mid"), index)
            (notes / f"{track}_notes_VN.csv").write_text("onset,offset,midi\n0.1,0.8,69\n", encoding="utf-8")
        output = Path(temporary) / "prepared"
        assert IMPORTER.main(["--root", str(root), "--output", str(output), "--minimum-tracks", "2"]) == 0
        pieces = json.loads((output / "manifest.json").read_text(encoding="utf-8"))["pieces"]
        assert len(pieces) == 6
        assert [source["instrument"] for source in pieces[0]["sources"]] == [0, 40]
        assert all(Path(source["notes"]).is_file() for source in pieces[0]["sources"])
        assert {piece["configuration"] for piece in pieces} == set(IMPORTER.CONFIGURATIONS)
        assert all(Path(piece["mixture_audio"]).is_file() for piece in pieces)
    print("test_prepare_kraisler_manifest: 5 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
