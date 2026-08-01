#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "filter_drum_attribute_rows.py"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        rows = write(
            root / "drums.tsv",
            """
sample	expected	got	energy_low	energy_mid	energy_high	kick_body	snare_body	tom_body	snare_crack	upper_tom_body	body_shape	kick_level	kick_trigger	kick_threshold	kick_shape	kick_band	kick_seg	kick_shape_score	snare_level	snare_trigger	snare_threshold	snare_shape	snare_band	snare_seg	snare_shape_score	tom_level	tom_trigger	tom_threshold	tom_shape	tom_band	tom_seg	tom_shape_score	merged_expected
tom/a.wav	tom	snare	0.25	0.56	0.19	10	20	32	4	20	4	0.0	10	1.42	0	3	4	5	0.98	20	1.42	1	30	40	50	0.68	16	1.42	1	45	60	65	0
snare/b.wav	snare	snare	0.12	0.70	0.18	6	30	35	20	16	1	0.0	6	1.42	0	1	2	3	0.95	30	1.42	1	20	21	22	0.20	8	1.42	0	6	7	8	0
kick/c.wav	kick	tom	0.80	0.15	0.05	40	18	50	2	30	0	0.82	12	1.42	1	12	12	13	0.10	5	1.42	0	5	5	5	0.90	14	1.42	1	44	45	46	1
            """,
        )

        route = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--route",
                "tom:snare",
                "--columns",
                "sample,expected,got,status,expected_level,got_level,tom_snare_body_ratio,upper_tom_snare_body_ratio,upper_tom_crack_ratio,upper_tom_snare_crack_ratio",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "tom/a.wav\ttom\tsnare\tmiss\t0.68\t0.98\t1.600000\t1.000000\t5.000000\t5.000000" in route
        assert "count\t1" in route

        counts = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--status",
                "miss",
                "--count-by",
                "expected",
                "--count-by",
                "got",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "tom\tsnare\t1" in counts
        assert "kick\ttom\t1" in counts
        assert "count\t2" in counts

        numeric = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--min",
                "tom_snare_body_ratio=2.0",
                "--max",
                "energy_high=0.10",
                "--columns",
                "sample,tom_snare_body_ratio,energy_high",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "kick/c.wav\t2.777778\t0.05" in numeric
        assert "count\t1" in numeric

        upper_tom_ratio = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--min",
                "upper_tom_snare_body_ratio=1.5",
                "--max",
                "upper_tom_snare_crack_ratio=16",
                "--columns",
                "sample,upper_tom_snare_body_ratio,upper_tom_snare_crack_ratio",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "kick/c.wav\t1.666667\t15.000000" in upper_tom_ratio
        assert "count\t1" in upper_tom_ratio

        missing_numeric = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--max",
                "hihat_rim_shape_score_ratio=2.0",
                "--columns",
                "sample,hihat_rim_shape_score_ratio",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "count\t0" in missing_numeric

        active_route = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--active-route",
                "tom:snare",
                "--columns",
                "sample,expected,got,snare_level",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "tom/a.wav\ttom\tsnare\t0.98" in active_route
        assert "count\t1" in active_route

        active_threshold = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(rows),
                "--active-route",
                "tom:snare",
                "--active-threshold",
                "0.99",
                "--columns",
                "sample,expected,got,snare_level",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "count\t0" in active_threshold

        cymbal_rows = write(
            root / "cymbals.tsv",
            """
sample	expected	got	hihat_level	hihat_trigger	hihat_threshold	hihat_shape_score	hihat_band	hihat_seg	rim_level	rim_trigger	rim_threshold	rim_shape_score	rim_band	rim_seg	crash_level	crash_trigger	crash_threshold	crash_shape_score	crash_band	crash_seg	ride_level	ride_trigger	ride_threshold	ride_shape_score	ride_band	ride_seg
hihat/d.wav	hihat	crash	0.80	8	4	1.20	60	70	0.20	2	4	1.00	20	30	0.72	6	4	0.90	65	75	0.40	3	4	0.70	35	45
ride/e.wav	hihat	ride	0.95	7	4	0.80	50	60	0.10	1	4	0.40	10	20	0.20	2	4	0.30	25	35	0.88	4	4	0.60	40	50
            """,
        )

        cymbal = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(cymbal_rows),
                "--route",
                "hihat:crash",
                "--min",
                "hihat_rim_shape_score_ratio=1.10",
                "--columns",
                "sample,hihat_rim_shape_score_ratio,ride_hihat_shape_score_ratio,crash_hihat_level_ratio,ride_hihat_level_ratio",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "hihat/d.wav\t70.000000\t0.642857\t0.900000\t0.500000" in cymbal
        assert "count\t1" in cymbal

        ride = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(cymbal_rows),
                "--route",
                "hihat:ride",
                "--max",
                "ride_hihat_level_ratio=0.93",
                "--columns",
                "sample,ride_hihat_level_ratio",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        assert "ride/e.wav\t0.926316" in ride
        assert "count\t1" in ride

    print("test_filter_drum_attribute_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
