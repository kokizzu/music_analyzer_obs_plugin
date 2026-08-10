#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_egmd_drum_recovery.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing `{needle}` in:\n{text}")


def test_scores_candidate_recovery_rules() -> None:
    sample = "\n".join(
        [
            "E-GMD miss SongA sample 100 expected kick,snare missing snare: levels BASS DRUM=0.90* SNARE=0.20 HIHAT=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | SNARE band=4.00 seg=3.00 shape=2.00 trig=8.00/1.00 supported=1 level=0.20 | HIHAT band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.80/0.12/0.08 transient=1.80 onset=8.00 body=0.60/10.00/0.30 crack=1.00 upperTom=0.10 bodyShape=0",
            "E-GMD false-positive SongB sample 200 expected kick: BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | SNARE band=4.00 seg=3.00 shape=2.00 trig=8.00/1.00 supported=1 level=0.20 | HIHAT band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.80/0.12/0.08 transient=1.80 onset=8.00 body=0.60/10.00/0.30 crack=1.00 upperTom=0.10 bodyShape=0",
            "E-GMD miss SongC sample 300 expected kick,ride missing ride: levels BASS DRUM=0.90* RIDE=0.00 HIHAT=0.00 CRASH=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | HIHAT band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | CRASH band=1.00 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | RIDE band=3.00 seg=3.00 shape=3.00 trig=6.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.75/0.15/0.10 transient=2.00 onset=5.00 body=1.00/1.00/1.00 crack=0.10 upperTom=0.10 bodyShape=0",
            "E-GMD miss SongD sample 400 expected hihat,snare missing snare: levels SNARE=0.20 HIHAT=0.60* SNARE band=2.00 seg=1.00 shape=1.00 trig=0.80/1.00 supported=1 level=0.20 | HIHAT band=1.00 seg=0.80 shape=0.80 trig=3.00/1.00 supported=1 level=0.60* | rms=0.0050 energy=0.35/0.42/0.23 transient=1.50 onset=2.00 body=0.50/0.70/1.20 crack=0.06 upperTom=0.70 bodyShape=4",
            "E-GMD miss SongE sample 500 expected kick,snare missing snare: levels BASS DRUM=0.90* SNARE=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | SNARE band=4.00 seg=3.00 shape=2.00 trig=8.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.80/0.10/0.05 transient=1.80 onset=16.00 body=50.00/30.00/40.00 crack=4.00 upperTom=2.00 bodyShape=0",
            "E-GMD miss SongF sample 600 expected kick missing kick: levels BASS DRUM=0.00 SNARE=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.00 | SNARE band=4.00 seg=3.00 shape=2.00 trig=8.00/1.00 supported=0 level=0.00 | rms=0.1000 energy=0.80/0.10/0.05 transient=1.80 onset=16.00 body=50.00/35.00/40.00 crack=4.00 upperTom=2.00 bodyShape=0",
            "E-GMD miss SongG sample 700 expected kick,tom missing tom: levels BASS DRUM=0.90* TOMS=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | TOMS band=60.00 seg=52.00 shape=50.00 trig=14.00/0.62 supported=0 level=0.00 | rms=0.0800 energy=0.86/0.10/0.03 transient=1.80 onset=16.00 body=50.00/20.00/52.00 crack=3.00 upperTom=11.00 bodyShape=0",
            "E-GMD window SongH sample 800 expected hihat,ride,snare: levels HIHAT=0.80* RIDE=0.00 SNARE=0.80* HIHAT band=2.00 seg=1.00 shape=1.00 trig=4.00/1.00 supported=1 level=0.80* | SNARE band=6.00 seg=4.00 shape=3.00 trig=4.00/1.00 supported=1 level=0.80* | CRASH band=0.80 seg=0.50 shape=0.50 trig=1.00/1.00 supported=0 level=0.00 | RIDE band=2.00 seg=1.20 shape=1.20 trig=8.00/1.00 supported=0 level=0.00 | rms=0.0500 energy=0.05/0.80/0.15 transient=1.90 onset=5.00 body=2.00/5.00/6.00 crack=1.00 upperTom=2.00 bodyShape=1",
            "E-GMD window SongI sample 900 expected kick,ride: levels BASS DRUM=0.90* RIDE=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | HIHAT band=0.80 seg=0.50 shape=0.50 trig=1.00/1.00 supported=0 level=0.00 | CRASH band=0.80 seg=0.50 shape=0.50 trig=1.00/1.00 supported=0 level=0.00 | RIDE band=2.00 seg=1.20 shape=1.20 trig=8.00/1.00 supported=0 level=0.00 | rms=0.0400 energy=0.86/0.12/0.02 transient=1.90 onset=25.00 body=30.00/12.00/40.00 crack=1.00 upperTom=6.00 bodyShape=0",
            "E-GMD window SongJ sample 1000 expected crash,kick: levels BASS DRUM=0.90* CRASH=0.00 BASS DRUM band=10.00 seg=9.00 shape=8.00 trig=8.00/1.00 supported=1 level=0.90* | HIHAT band=0.80 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | CRASH band=2.00 seg=2.00 shape=2.00 trig=2.00/1.00 supported=0 level=0.00 | RIDE band=0.80 seg=1.00 shape=1.00 trig=1.00/1.00 supported=0 level=0.00 | rms=0.0400 energy=0.86/0.12/0.02 transient=1.90 onset=900.00 body=35.00/17.00/48.00 crack=0.80 upperTom=7.00 bodyShape=0",
            "E-GMD window SongK sample 1100 expected hihat,kick: levels BASS DRUM=0.74* HIHAT=0.00 BASS DRUM band=43.05 seg=13.89 shape=29.99 trig=2.44/0.45 supported=1 level=0.74* | HIHAT band=0.32 seg=0.41 shape=0.41 trig=1.45/1.42 supported=0 level=0.00 | CRASH band=0.52 seg=0.56 shape=0.56 trig=1.45/1.42 supported=0 level=0.00 | RIDE band=0.34 seg=0.42 shape=0.42 trig=1.45/1.42 supported=0 level=0.00 | rms=0.0328 energy=0.88/0.11/0.02 transient=1.49 onset=2.55 body=12.42/6.59/15.87 crack=0.68 upperTom=3.71 bodyShape=0",
            "E-GMD window SongL sample 1200 expected hihat,kick: levels BASS DRUM=0.98* SNARE=0.81* HIHAT=0.28 BASS DRUM band=807.61 seg=191.32 shape=407.64 trig=73.78/0.45 supported=1 level=0.98* | SNARE band=99.55 seg=113.11 shape=113.82 trig=16.37/1.42 supported=1 level=0.81* | HIHAT band=1.35 seg=3.19 shape=3.19 trig=19.64/1.42 supported=0 level=0.28 | CRASH band=0.40 seg=2.38 shape=2.38 trig=21.72/1.42 supported=0 level=0.00 | RIDE band=1.93 seg=3.26 shape=3.26 trig=16.43/1.42 supported=0 level=0.00 | rms=0.3258 energy=0.90/0.08/0.01 transient=1.97 onset=43.35 body=166.73/108.18/278.16 crack=9.59 upperTom=55.93 bodyShape=0",
            "E-GMD window SongM sample 1300 expected crash,kick,ride: levels BASS DRUM=0.99* HIHAT=0.92* CRASH=0.14 RIDE=0.34* BASS DRUM band=98.99 seg=51.13 shape=107.13 trig=185.72/0.45 supported=1 level=0.99* | HIHAT band=1.27 seg=1.66 shape=1.66 trig=10.56/0.37 supported=0 level=0.92* | CRASH band=1.18 seg=1.24 shape=1.24 trig=12.09/1.42 supported=0 level=0.14 | RIDE band=1.31 seg=1.81 shape=1.81 trig=10.46/1.42 supported=0 level=0.34* | rms=0.0531 energy=0.84/0.13/0.03 transient=1.91 onset=27.33 body=45.16/25.48/65.91 crack=1.68 upperTom=10.01 bodyShape=0",
            "E-GMD window SongN sample 1400 expected crash,snare: levels BASS DRUM=0.75* SNARE=0.00 CRASH=0.00 BASS DRUM band=39.37 seg=56.14 shape=108.03 trig=2.70/0.45 supported=1 level=0.75* | SNARE band=21.14 seg=31.81 shape=35.49 trig=1.60/1.42 supported=0 level=0.00 | HIHAT band=0.72 seg=1.35 shape=1.35 trig=1.48/0.37 supported=0 level=0.69* | CRASH band=0.40 seg=1.10 shape=1.10 trig=1.48/1.42 supported=0 level=0.00 | RIDE band=0.75 seg=1.49 shape=1.49 trig=1.48/1.42 supported=0 level=0.00 | rms=0.0725 energy=0.69/0.25/0.06 transient=1.65 onset=2.55 body=49.46/30.66/74.92 crack=2.67 upperTom=14.04 bodyShape=0",
            "E-GMD window SongO sample 1500 expected crash,kick: levels BASS DRUM=0.74* HIHAT=0.67* CRASH=0.00 BASS DRUM band=118.89 seg=43.71 shape=94.66 trig=2.43/0.45 supported=1 level=0.74* | HIHAT band=1.24 seg=0.69 shape=0.69 trig=1.46/0.37 supported=0 level=0.67* | CRASH band=0.64 seg=0.57 shape=0.57 trig=1.46/1.42 supported=0 level=0.00 | RIDE band=1.84 seg=1.12 shape=1.12 trig=1.46/1.42 supported=0 level=0.00 | rms=0.0837 energy=0.87/0.10/0.03 transient=1.64 onset=2.55 body=39.38/27.33/56.51 crack=2.75 upperTom=16.14 bodyShape=0",
            "E-GMD window SongP sample 1600 expected crash,kick: levels BASS DRUM=0.71* SNARE=0.67* HIHAT=0.67* CRASH=0.00 BASS DRUM band=43.71 seg=17.70 shape=33.83 trig=2.15/0.45 supported=1 level=0.71* | SNARE band=25.64 seg=18.79 shape=21.11 trig=1.64/0.43 supported=1 level=0.67* | HIHAT band=0.69 seg=0.73 shape=0.73 trig=1.48/0.37 supported=0 level=0.67* | CRASH band=0.42 seg=0.48 shape=0.48 trig=1.48/1.42 supported=0 level=0.00 | RIDE band=1.23 seg=1.16 shape=1.16 trig=1.48/1.42 supported=0 level=0.00 | rms=0.0547 energy=0.63/0.32/0.05 transient=1.95 onset=2.55 body=16.02/17.60/26.48 crack=2.33 upperTom=13.20 bodyShape=0",
            "E-GMD window SongQ sample 1700 expected crash,kick: levels BASS DRUM=0.73* HIHAT=0.68* CRASH=0.00 BASS DRUM band=276.33 seg=58.49 shape=120.27 trig=2.39/0.45 supported=1 level=0.73* | HIHAT band=5.94 seg=3.76 shape=3.76 trig=1.49/0.37 supported=1 level=0.68* | CRASH band=4.34 seg=2.21 shape=2.21 trig=1.49/1.42 supported=0 level=0.00 | RIDE band=16.28 seg=8.92 shape=8.92 trig=1.49/1.42 supported=0 level=0.00 | rms=0.1328 energy=0.83/0.10/0.07 transient=1.57 onset=2.55 body=50.97/51.67/104.62 crack=5.23 upperTom=34.99 bodyShape=0",
            "E-GMD window SongR sample 1800 expected crash,kick: levels BASS DRUM=0.99* SNARE=0.24 HIHAT=0.28 CRASH=0.00 BASS DRUM band=45.18 seg=11.79 shape=24.75 trig=187.16/0.45 supported=1 level=0.99* | HIHAT band=0.50 seg=0.23 shape=0.23 trig=1.26/1.42 supported=0 level=0.28 | CRASH band=0.26 seg=0.18 shape=0.18 trig=1.25/1.42 supported=0 level=0.00 | RIDE band=0.48 seg=0.26 shape=0.26 trig=1.17/1.42 supported=0 level=0.00 | rms=0.0183 energy=0.86/0.13/0.01 transient=2.13 onset=2.77 body=10.33/8.16/18.26 crack=0.57 upperTom=4.00 bodyShape=0",
            "E-GMD window SongS sample 1900 expected crash,kick: levels BASS DRUM=0.75* HIHAT=0.69* CRASH=0.00 BASS DRUM band=42.16 seg=68.33 shape=129.12 trig=2.85/0.45 supported=1 level=0.75* | HIHAT band=2.07 seg=2.69 shape=2.69 trig=1.59/0.37 supported=1 level=0.69* | CRASH band=0.92 seg=1.10 shape=1.10 trig=1.59/1.42 supported=0 level=0.00 | RIDE band=3.45 seg=4.19 shape=4.19 trig=1.59/1.42 supported=0 level=0.00 | rms=0.0714 energy=0.64/0.16/0.20 transient=2.12 onset=2.55 body=60.64/21.24/74.03 crack=1.89 upperTom=7.47 bodyShape=0",
            "E-GMD window SongT sample 2000 expected hihat,kick,ride: levels BASS DRUM=0.99* HIHAT=0.85* RIDE=0.00 BASS DRUM band=80.49 seg=30.88 shape=65.68 trig=136.29/0.45 supported=1 level=0.99* | HIHAT band=4.64 seg=0.99 shape=0.99 trig=5.69/0.37 supported=0 level=0.85* | CRASH band=4.35 seg=0.73 shape=0.73 trig=10.76/1.42 supported=0 level=0.00 | RIDE band=4.38 seg=1.53 shape=1.53 trig=4.94/1.42 supported=0 level=0.00 | rms=0.0387 energy=0.85/0.12/0.03 transient=2.04 onset=3.19 body=27.58/8.53/30.32 crack=0.60 upperTom=3.84 bodyShape=0",
            "E-GMD window SongU sample 2100 expected ride,snare: levels BASS DRUM=0.96* SNARE=0.34* HIHAT=0.94* RIDE=0.00 BASS DRUM band=288.46 seg=79.96 shape=175.72 trig=29.13/0.45 supported=1 level=0.96* | SNARE band=22.45 seg=27.83 shape=27.70 trig=14.53/1.42 supported=1 level=0.34* | HIHAT band=3.69 seg=2.97 shape=2.97 trig=16.10/0.37 supported=0 level=0.94* | CRASH band=1.47 seg=1.29 shape=1.29 trig=15.57/1.42 supported=0 level=0.00 | RIDE band=5.62 seg=3.08 shape=3.08 trig=14.54/1.42 supported=0 level=0.00 | rms=0.1165 energy=0.88/0.09/0.03 transient=2.08 onset=17.24 body=72.51/26.26/68.87 crack=3.86 upperTom=13.70 bodyShape=0",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "egmd.err"
        path.write_text(sample, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--examples", "2"],
            check=True,
            text=True,
            capture_output=True,
        )

    output = result.stdout
    require(output, "evaluate_egmd_drum_recovery: events=21")
    require(output, "rule=supported-low-snare category=snare")
    require(output, "tp_gain=1 fp_gain=0 net=1")
    require(output, "rule=kick-backed-snare category=snare")
    require(output, "tp_gain=2 fp_gain=2 net=0")
    require(output, "rule=embedded-ride category=ride")
    require(output, "tp_gain=1 fp_gain=0 net=1")
    require(output, "rule=low-crack-kick-backed-snare category=snare matched=2")
    require(output, "rule=low-treble-kick-backed-tom category=tom matched=1")
    require(output, "rule=mid-dominant-embedded-ride category=ride matched=1")
    require(output, "rule=low-rms-embedded-ride category=ride matched=2")
    require(output, "rule=long-onset-low-rms-crash category=crash matched=1")
    require(output, "rule=threshold-low-band-hihat category=hihat matched=1")
    require(output, "rule=dense-low-high-hihat category=hihat matched=1")
    require(output, "rule=mid-onset-low-rms-crash category=crash matched=1")
    require(output, "rule=short-balanced-crash category=crash matched=1")
    require(output, "rule=short-low-dominant-crash category=crash matched=1")
    require(output, "rule=short-mid-heavy-crash category=crash matched=1")
    require(output, "rule=broad-low-ratio-crash category=crash matched=1")
    require(output, "rule=quiet-threshold-crash category=crash matched=1")
    require(output, "rule=treble-dense-crash category=crash matched=1")
    require(output, "rule=compact-low-rms-ride category=ride matched=1")
    require(output, "rule=broad-low-dominant-ride category=ride matched=1")


if __name__ == "__main__":
    test_scores_candidate_recovery_rules()
    print("test_evaluate_egmd_drum_recovery: ok")
