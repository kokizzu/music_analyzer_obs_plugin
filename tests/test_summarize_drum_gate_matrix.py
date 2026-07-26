#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_drum_gate_matrix.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    log_text = """
analyzer_drum_samples: active matrix
  expected kick  kick=3 snare=1 hihat=0 crash=0 tom=2 ride=0 rim=0
  expected snare kick=1 snare=4 hihat=0 crash=0 tom=1 ride=0 rim=0
  expected tom   kick=2 snare=3 hihat=0 crash=0 tom=5 ride=0 rim=0
analyzer_drum_samples: primary matrix
  expected kick  kick=2 snare=1 hihat=0 crash=0 tom=1 ride=0 rim=0 ambiguous=1 none=0
  expected snare kick=0 snare=4 hihat=0 crash=0 tom=1 ride=0 rim=0 ambiguous=0 none=0
  expected tom   kick=2 snare=3 hihat=0 crash=0 tom=5 ride=0 rim=0 ambiguous=1 none=1
""".strip()
    with tempfile.TemporaryDirectory() as tmpdir:
        log = pathlib.Path(tmpdir) / "drum.out"
        log.write_text(log_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(log)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "active matrix rows=3 events=22")
    require(output, "active expected tom: hit=5/10 hit_share=50.00% off_target=5 top_off_target=snare=3 kick=2")
    require(output, "primary totals ambiguous=2 kick=4 none=1 snare=8 tom=7")
    require(output, "primary expected kick: hit=2/5 hit_share=40.00% off_target=3 top_off_target=ambiguous=1 snare=1 tom=1")
    require(output, "primary expected tom: hit=5/12 hit_share=41.67% off_target=7 top_off_target=snare=3 kick=2 ambiguous=1 none=1")
    print("test_summarize_drum_gate_matrix: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
