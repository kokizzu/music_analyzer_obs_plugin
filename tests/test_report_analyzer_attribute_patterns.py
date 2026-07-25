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
kind	status	family	expected_family	program_name	note	midi	path	window_ms	detected_expected_row	detected_anywhere	display_note	display_midi	display_delta	debug_note	debug_owner	debug_conf	raw_expected_rank	raw_tuned_abs_cent_offset	bass_notes	piano_notes	guitar_notes	vocal_notes	other_notes	amb_notes
note	hit	guitar	guitar	clean	C3	48	s.wav	100	1	1	C3	48	0	C3	guitar	1	1	0	--	--	C3:1.0,C4:0.5	--	--	--
note	hit	piano	piano	grand	E4	64	p.wav	100	1	1	E4	64	0	E5	guitar	0.7	2	9	--	E4:1.0	--	--	--	--
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
recording_id	status	expected_chords	expected_chord_qualities	quality	expected_label	expected_root	expected_quality_compact	guitar_match_kind	guitar_chord	guitar_raw_chord	guitar_smoothed_chord	global_chord	support	guitar_pitch_classes	guitar_analysis_pitch_classes	guitar_smoothed_pitch_classes	visible_missing_tones	analysis_missing_tones	smooth_missing_tones	evidence_class	evidence_source	raw_root	raw_third	raw_fifth	raw_opposite_third	raw_third_anchor_ratio	raw_third_opposite_margin	quality_raw
g1	chord_miss	Am	min	m	Am	A	m	display_same_root_other	Asus2	Asus2	Asus2	--	visible2_analysis2_smooth2_rootvis1	A,E	A,E	A,E	third	third	third	third_missing	grid	1	0.02	1	0.1	0.02	-0.08	A:r1,m30.02,51
g2	chord_hit	C	maj	maj	C	C	maj	display_exact	C	C	C	--	visible3_analysis3_smooth3_rootvis1	C,E,G	C,E,G	C,E,G	--	--	--	display_exact	display	1	1	1	0	1	1	C:r1,M31,51
g3	chord_miss	C#m	min	m	C#	C#	m	display_different_root	A	A	B	--	visible2_analysis3_smooth3_rootvis1	C#,E	C#,E,G#	C#,E,G#	fifth	--	--	analysis_full_tone_label_gap	analysis	1	1	1	0	1	1	C#:r1,m31,51
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
    assert "pitch quality exact=1 octave_alias=1" in output
    assert "display pitch quality exact=2" in output
    assert "target octave duplicates guitar:dup1=1" in output
    assert "guitar: rows=1 owners=guitar=1 pitch=exact=1 display=exact=1 octdup=1=1" in output
    assert "piano: rows=1 owners=guitar=1 pitch=octave_alias=1 display=exact=1 octdup=0=1" in output
    assert "real-note full-mix attributes" in output
    assert "row pitch quality octave_alias=1 exact=1" in output
    assert "ownership_miss:piano/electronic->bass" in output
    assert "debug-midi deltas 12=1" in output
    assert "guitar chord attributes" in output
    assert "full-tone expected-label gaps visible=0/0 analysis=1/1 smoothed=1/1" in output
    assert "miss match kinds display_same_root_other=1 display_different_root=1" in output
    assert "miss evidence classes third_missing=1 analysis_full_tone_label_gap=1" in output
    assert "miss evidence sources grid=1 analysis=1" in output
    assert "full-tone expected-label gap examples" in output
    assert "analysis expected=C#m got=A raw=A smooth=B" in output
    assert "match=display_different_root" in output
    assert "evidence=analysis_full_tone_label_gap/analysis" in output
    assert "third_anchor=1" in output
    assert "raw tone medians root=1 third=0.51 fifth=1 third_anchor=0.51 third_margin=0.46" in output
    assert "drum primary attributes" in output
    assert "snare->tom" in output
    assert "level_margin_med=+0.1" in output
    assert "trigger_ratio_margin_med=--" in output
    assert "representative detected rows" in output
    assert "expected=C4/60 first=bass" in output
    assert "expected=Am got=Asus2" in output
    assert "snare->tom energy=0.2/0.7/0.1" in output
    assert "level_margin=+0.1" in output
    print("test_report_analyzer_attribute_patterns: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
