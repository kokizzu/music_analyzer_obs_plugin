#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "print_analyzer_detected_attributes.py"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        instrument = write(
            root / "instrument.tsv",
            """
kind	status	family	note	midi	path	debug_note	debug_owner	nearest_debug_delta	bass_level	piano_level	guitar_level	vocal_level	other_level	amb_level	raw_expected_ratio	raw_tuned_ratio	raw_tuned_abs_cent_offset	raw_expected_rank	keyboard_score	guitar_score	vocal_score	other_score	pitch_confidence	periodicity	fit_error
note	hit	piano	C4	60	piano.wav	C4	piano	0	0	0.9	0.1	0	0	0	1	1	0	1	0.9	0.1	0	0	0.9	0.8	0.1
note	miss	guitar	E3	52	guitar.wav	E3	piano	0	0	0.8	0.2	0	0	0	0.7	0.8	4	2	0.8	0.2	0	0	0.7	0.6	0.2
            """,
        )
        real_note = write(
            root / "real.tsv",
            """
sample_id	status	family	source	expected_note	expected_midi	first_row	buffer	row_label	buffer_strongest_row	debug_note	debug_delta	debug_owner	bass_level	guitar_level	piano_level	vocal_level	other_level	amb_level	raw_expected_ratio	raw_tuned_ratio	raw_tuned_abs_cent_offset	raw_expected_rank	keyboard_score	guitar_score	vocal_score	other_score	pitch_confidence	periodicity	fit_error
s1	hit	guitar	acoustic	E3	52	guitar	0	E3	guitar	E3	0	guitar	0	0.9	0.1	0	0	0	1	1	0	1	0.1	0.9	0	0	0.9	0.8	0.1
s2	ownership_miss	piano	electronic	C4	60	bass	1	C4	bass	C4	0	guitar	0.8	0.2	0.4	0	0	0	1	1	0	1	0.4	0.6	0	0	0.8	0.7	0.1
            """,
        )
        guitar = write(
            root / "guitar.tsv",
            """
recording_id	status	expected_chords	expected_chord_qualities	quality	expected_label	expected_root	expected_quality_compact	guitar_match_kind	chord_hit	simple_chord_hit	guitar_chord_hit	expected_label_in_display	expected_label_in_raw	expected_label_in_smooth	expected_root_in_display	guitar_chord	guitar_raw_chord	guitar_smoothed_chord	global_chord	support	expected_pitch_classes	guitar_pitch_classes	guitar_analysis_pitch_classes	guitar_smoothed_pitch_classes	visible_missing_tones	analysis_missing_tones	smooth_missing_tones	evidence_class	evidence_source	visible_root	visible_third	visible_fifth	analysis_root	analysis_third	analysis_fifth	smooth_root	smooth_third	smooth_fifth	raw_root	raw_third	raw_fifth	raw_opposite_third	raw_third_anchor_ratio	raw_third_opposite_margin	guitar_note_hits	guitar_false_positive_pitch_classes	rms
g1	chord_hit	C	major	maj	C	C	maj	display_exact	1	1	1	1	1	1	1	C	C	C	C	visible3	C,E,G	C,E,G	C,E,G	C,E,G	--	--	--	display_exact	display	1	1	1	1	1	1	1	1	1	1	1	1	0	1	1	3	0	0.2
g2	chord_miss	Am	minor	m	Am	A	m	display_same_root_other	0	0	0	0	0	0	1	Asus2	Asus2	Asus2	--	visible2	A,C,E	A,C	A,C	A,C	fifth	fifth	fifth	fifth_missing	grid	1	1	0	1	1	0	1	1	0	1	1	0.2	0.1	1	0.9	2	0	0.2
            """,
        )
        drum_primary = write(
            root / "drum_primary.tsv",
            """
sample	expected	got	energy_low	energy_mid	energy_high	kick_body	snare_body	tom_body	snare_crack	upper_tom_body	kick_level	snare_level	hihat_level	crash_level	tom_level	ride_level	rim_level	kick_trigger	kick_threshold	snare_trigger	snare_threshold	hihat_trigger	hihat_threshold	crash_trigger	crash_threshold	tom_trigger	tom_threshold	ride_trigger	ride_threshold	rim_trigger	rim_threshold
snare.wav	snare	tom	0.2	0.7	0.1	0.1	0.8	0.9	0.6	0.2	0.1	0.8	0	0	0.9	0	0	0.1	0.4	0.7	0.5	0	0	0	0	0.8	0.4	0	0	0	0
            """,
        )
        drum_full = write(
            root / "drum_full.tsv",
            """
sample	expected	got	energy_low	energy_mid	energy_high	kick_body	snare_body	tom_body	snare_crack	upper_tom_body	kick_level	snare_level	hihat_level	crash_level	tom_level	ride_level	rim_level	kick_trigger	kick_threshold	snare_trigger	snare_threshold	hihat_trigger	hihat_threshold	crash_trigger	crash_threshold	tom_trigger	tom_threshold	ride_trigger	ride_threshold	rim_trigger	rim_threshold
kick.wav	kick	kick	0.9	0.1	0.0	0.9	0.1	0.1	0.1	0.1	1	0	0	0	0	0	0	0.9	0.4	0	0	0	0	0	0	0	0	0	0	0	0
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
                "--drum-primary",
                str(drum_primary),
                "--drum-full",
                str(drum_full),
                "--row-limit",
                "2",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = result.stdout
    assert "measured generated instrument note rows" in output
    assert "debug owner mismatches=guitar->piano=1" in output
    assert "debug pitch deltas=+0=2" in output
    assert "pitch quality=exact=2" in output
    assert "piano rows=1 notes=1 range=C4/60 hit=1/1 100.0%" in output
    assert "piano rows=1 notes=1 range=C4/60 hit=1/1 100.0% pitch=exact=1" in output
    assert "guitar rows=1 notes=1 range=E3/52 hit=0/1 0.0%" in output
    assert "guitar rows=1 notes=1 range=E3/52 hit=0/1 0.0% pitch=exact=1" in output
    assert "miss guitar expected=E3/52 got=E3/piano" in output
    assert "measured real-note full-mix rows" in output
    assert "debug owner mismatches=piano->guitar=1" in output
    assert "pitch quality=exact=2" in output
    assert "guitar rows=1 samples=1 notes=1 range=E3/52 hit=1/1 100.0%" in output
    assert "guitar rows=1 samples=1 notes=1 range=E3/52 hit=1/1 100.0% pitch=exact=1" in output
    assert "piano rows=1 samples=1 notes=1 range=C4/60 hit=0/1 0.0%" in output
    assert "piano rows=1 samples=1 notes=1 range=C4/60 hit=0/1 0.0% pitch=exact=1" in output
    assert "ownership_miss piano/electronic expected=C4/60 first=bass" in output
    assert "measured guitar chord rows" in output
    assert "maj chord_hit=1/1 100.0%" in output
    assert "m chord_hit=0/1 0.0%" in output
    assert "miss evidence=fifth_missing=1 sources=grid=1" in output
    assert "miss match kinds=display_same_root_other=1" in output
    assert "miss visible missing=fifth=1 analysis missing=fifth=1 smooth missing=fifth=1" in output
    assert "chord_miss quality=m expected=Am got=Asus2" in output
    assert "match=display_same_root_other" in output
    assert "evidence=fifth_missing/grid" in output
    assert "third_anchor=1" in output
    assert "third_margin=0.9" in output
    assert "missing=v:fifth a:fifth s:fifth" in output
    assert "measured drum primary rows" in output
    assert "snare->tom energy=0.2/0.7/0.1" in output
    assert "measured protected drum full rows" in output
    assert "kick->kick energy=0.9/0.1/0" in output
    print("test_print_analyzer_detected_attributes: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
