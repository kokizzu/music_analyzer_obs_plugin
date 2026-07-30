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
analyzer_drum_samples: ok (usable 21, skipped 2, kick recall 3/4 primary 2/4 precision 3/6 false 3 50%, snare recall 4/5 primary 4/5 precision 4/8 false 4 50%, tom recall 5/6 primary 5/6 precision 5/10 false 5 50%)
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
    require(output, "sample metrics usable=21 skipped=2")
    require(output, "sample kick: recall=3/4 75.00% primary=2/4 50.00% precision=3/6 50.00% false=3")
    require(output, "sample tom: recall=5/6 83.33% primary=5/6 83.33% precision=5/10 50.00% false=5")
    require(output, "active expected tom: hit=5/10 hit_share=50.00% off_target=5 top_off_target=snare=3 kick=2")
    require(output, "primary totals ambiguous=2 kick=4 none=1 snare=8 tom=7")
    require(output, "primary expected kick: hit=2/5 hit_share=40.00% off_target=3 top_off_target=ambiguous=1 snare=1 tom=1")
    require(output, "primary expected tom: hit=5/12 hit_share=41.67% off_target=7 top_off_target=snare=3 kick=2 ambiguous=1 none=1")

    tsv_header = ["sample", "expected", "got"]
    for category in ["kick", "snare", "hihat", "crash", "tom", "ride", "rim"]:
        tsv_header.append(f"{category}_level")
    tsv_rows = [
        ["a.wav", "kick", "kick", "1.0", "0", "0", "0", "0", "0", "0"],
        ["b.wav", "kick", "snare", "0.5", "0.8", "0", "0", "0", "0", "0"],
        ["c.wav", "snare", "snare", "0", "1.0", "0", "0", "0.4", "0", "0"],
        ["d.wav", "tom", "none", "0", "0", "0", "0", "0", "0", "0"],
    ]
    tsv_text = "\n".join(
        ["\t".join(tsv_header), *("\t".join(row) for row in tsv_rows)]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tsv = pathlib.Path(tmpdir) / "drum.tsv"
        tsv.write_text(tsv_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(tsv)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    require(output, "sample metrics usable=4")
    require(output, "sample kick: recall=2/2 100.00% primary=1/2 50.00% precision=2/2 100.00% false=0")
    require(output, "sample snare: recall=1/1 100.00% primary=1/1 100.00% precision=1/2 50.00% false=1")
    require(output, "sample tom: recall=0/1 0.00% primary=0/1 0.00% precision=0/1 0.00% false=1")
    require(output, "active matrix rows=3 events=5")
    require(output, "active expected kick: hit=2/3 hit_share=66.67% off_target=1 top_off_target=snare=1")
    require(output, "primary totals kick=1 none=1 snare=2")
    require(output, "primary expected tom: hit=0/1 hit_share=0.00% off_target=1 top_off_target=none=1")
    print("test_summarize_drum_gate_matrix: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
