#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_piano_chord_state_audit.py"
SPEC = importlib.util.spec_from_file_location("piano_chord_state_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "state.tsv"
        path.write_text(
            "recording\tanchor_sample\tframe\tcenter_sample\texpected_chords\tkeyboard_chord\tchord_hit\n"
            "1\t100\t-1\t90\tC\tC\t1\n"
            "1\t100\t0\t100\tC\t--\t0\n"
            "1\t100\t1\t110\tC\tC\t1\n"
            "2\t200\t-1\t190\tD\tE\t0\n"
            "2\t200\t0\t200\tD\tD\t1\n"
            "2\t200\t1\t210\tD\tD\t1\n",
            encoding="utf-8",
        )
        values = MODULE.summarize(path)
        assert values[:6] == (2, 6, 4, 1, 1, 1)
        assert values[6] == {-1: (2, 1, 1), 0: (2, 1, 1), 1: (2, 2, 0)}
    print("test_summarize_piano_chord_state_audit: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
