#!/usr/bin/env python3
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_guitarset_misses.py"


def run_analysis(log_text: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "guitarset_verbose.log"
        log_path.write_text(log_text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(log_path)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected `{needle}` in output:\n{text}")


def main() -> int:
    output = run_analysis(
        "\n".join(
            [
                "case1: chord opportunity `Cmaj7`, detected global `--`, key `--`, "
                "guitar `C`, other `--`, expected pc `C,E,G,B`, guitar pc `C,E,G,B`, "
                "guitar cells `C3:1.00,E3:0.80,G3:0.70,B3:0.40`",
                "case2: chord opportunity `Cmaj7`, detected global `--`, key `--`, "
                "guitar `Am7`, other `--`, expected pc `C,E,G,B`, guitar pc `C,E,G,A,B`, "
                "guitar cells `C3:0.70,E3:0.65,G3:0.60,A2:1.00,B3:0.50`",
                "case3: chord opportunity `Cmaj7`, detected global `--`, key `--`, "
                "guitar `C`, other `--`, expected pc `C,E,G,B`, guitar pc `C,E,G`, "
                "guitar cells `C3:1.00,E3:0.70,G3:0.60`",
                "case4: chord opportunity `C`, detected global `--`, key `--`, "
                "guitar `--`, other `--`, expected pc `C,E,G`, guitar pc `C,E`, "
                "guitar cells `C3:1.00,E3:0.70`",
                "case5: chord opportunity `C`, detected global `--`, key `--`, "
                "guitar `--`, other `--`, expected pc `C,E,G`, guitar pc `--`, "
                "guitar cells `--`",
                "case6: chord opportunity `G`, detected global `--`, key `--`, "
                "guitar `--`, other `--`, expected pc `G,B,D`, guitar pc `G,D`, "
                "guitar cells `G2:1.00,D3:0.70`, guitar analysis pc `G,B,D`, "
                "guitar analysis cells `G2:1.00,B2:0.30,D3:0.70`, guitar smooth pc `G,B,D`, "
                "guitar smooth cells `G2:0.85,B2:0.22,D3:0.64`",
            ]
        )
    )
    require(output, "misses 6")
    require(output, "1 full_tones_present_same_root_wrong_quality")
    require(output, "1 full_tones_present_root_shift")
    require(output, "1 same_root_but_expected_tones_missing")
    require(output, "2 expected_tones_missing_no_chord")
    require(output, "1 no_guitar_notes")
    require(output, "2 100%")
    require(output, "1 75-99%")
    require(output, "2 50-74%")
    require(output, "1 0%")
    require(output, "analysis guitar grid coverage buckets")
    require(output, "display_missing_analysis_full 1")
    require(output, "display_missing_smooth_full 1")
    print("test_analyze_guitarset_misses: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
