#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "report_analyzer_attribute_patterns.py"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        instrument = write(
            root / "instrument.tsv",
            """
kind	status	family	expected_family	program_name	note	midi	path	window_ms	detected_expected_row	detected_anywhere	debug_note	debug_owner	debug_conf	raw_expected_rank	raw_tuned_abs_cent_offset
note	hit	guitar	guitar	clean	C3	48	s.wav	100	1	1	C3	guitar	1	1	0
note	hit	piano	piano	grand	E4	64	p.wav	100	1	1	E5	guitar	0.7	2	9
            """,
        )
        real_note = write(
            root / "real.tsv",
            """
sample_id	status	family	source	expected_note	expected_midi	first_row	buffer	buffer_strongest_row	debug_note	debug_owner	raw_expected_ratio	raw_tuned_abs_cent_offset	raw_local_best_note	raw_expected_rank
p1	ownership_miss	piano	electronic	C4	60	bass	0	bass	C5	guitar	1	0	C4	1
p2	hit	guitar	acoustic	E3	52	guitar	0	guitar	E3	guitar	1	0	E3	1
            """,
        )
        guitar = write(
            root / "guitar.tsv",
            """
recording_id	status	expected_chords	expected_chord_qualities	quality	guitar_chord	global_chord	support	visible_missing_tones	analysis_missing_tones	smooth_missing_tones	raw_root	raw_third	raw_fifth
g1	chord_miss	Am	min	m	Asus2	--	visible2_analysis2_smooth2_rootvis1	third	third	third	1	0.02	1
g2	chord_hit	C	maj	maj	C	--	visible3_analysis3_smooth3_rootvis1	--	--	--	1	1	1
            """,
        )
        drum = write(
            root / "drum.tsv",
            """
sample	expected	got	energy_low	energy_mid	energy_high	kick_level	snare_level	tom_level
snare/1.wav	snare	tom	0.2	0.7	0.1	0.1	0.8	0.9
            """,
        )
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--instrument",
                str(instrument),
                "--real-note",
                str(real_note),
                "--guitar-chord",
                str(guitar),
                "--drum",
                str(drum),
                "--limit",
                "4",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = result.stdout
    assert "instrument sample attributes" in output
    assert "real-note full-mix attributes" in output
    assert "ownership_miss:piano/electronic->bass" in output
    assert "debug-midi deltas 12=1" in output
    assert "guitar chord attributes" in output
    assert "raw tone medians root=1 third=0.02 fifth=1" in output
    assert "drum primary miss attributes" in output
    assert "snare->tom" in output
    print("test_report_analyzer_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
