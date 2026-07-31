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
kind	status	family	note	midi	path	display_note	display_midi	display_delta	primary_note	primary_midi	primary_delta	debug_note	debug_owner	nearest_debug_delta	bass_level	piano_level	guitar_level	vocal_level	other_level	amb_level	bass_notes	piano_notes	guitar_notes	vocal_notes	other_notes	amb_notes	raw_expected_ratio	raw_tuned_ratio	raw_tuned_abs_cent_offset	raw_expected_rank	keyboard_score	guitar_score	vocal_score	other_score	pitch_confidence	periodicity	fit_error
note	hit	piano	C4	60	piano.wav	C4	60	0	C4	60	0	C4	piano	0	0	0.9	0.1	0	0	0	--	C4:0.9	--	--	--	--	1	1	0	1	0.9	0.1	0	0	0.9	0.8	0.1
note	miss	guitar	E3	52	guitar.wav	E4	64	12	E3	52	0	E3	piano	0	0	0.8	0.2	0	0	0	--	--	E3:0.5,E4:0.6	--	--	--	0.7	0.8	4	2	0.8	0.2	0	0	0.7	0.6	0.2
            """,
        )
        real_note = write(
            root / "real.tsv",
            """
sample_id	status	family	source	expected_note	expected_midi	first_row	buffer	row_label	buffer_strongest_row	buffer_visual_strongest_row	debug_note	debug_delta	debug_owner	bass_level	guitar_level	piano_level	vocal_level	other_level	amb_level	bass_notes	guitar_notes	piano_notes	vocal_notes	other_notes	amb_notes	expected_row_exact_level	expected_row_pitch_level	strongest_row_exact_level	strongest_row_pitch_level	expected_exact_row_count	expected_pitch_row_count	expected_row_visual_exact_level	expected_row_visual_pitch_level	visual_strongest_row_exact_level	visual_strongest_row_pitch_level	expected_visual_exact_row_count	expected_visual_pitch_row_count	raw_expected_ratio	raw_tuned_ratio	raw_tuned_abs_cent_offset	raw_expected_rank	keyboard_score	guitar_score	vocal_score	other_score	pitch_confidence	periodicity	fit_error	partial1	partial2	partial3	partial4	partial5
s1	hit	guitar	acoustic	E3	52	guitar	0	E3	guitar	guitar	E3	0	guitar	0	0.9	0.1	0	0	0	--	E3:0.9	--	--	--	--	0.9	0.9	0.9	0.9	1	1	0.9	0.9	0.9	0.9	1	1	1	1	0	1	0.1	0.9	0	0	0.9	0.8	0.1	1	0.42	0.20	0.08	0.04
s2	ownership_miss	piano	electronic	C4	60	bass	1	C4	bass	guitar	C4	0	guitar	0.8	0.2	0.4	0	0	0	C4:0.8	C4:0.2	C4:0.4	--	--	--	0.4	0.4	0.8	0.8	3	3	0.2	0.2	0.2	0.2	3	3	1	1	0	1	0.4	0.6	0	0	0.8	0.7	0.1	1	0.25	0.11	0.03	0.01
s3	hit	bass	electric	E2	40	bass	0	E2	bass	bass	E3	12	bass	0.9	0.2	0.1	0	0	0	E2:0.9	E2:0.3	--	--	--	--	0.9	0.9	0.9	0.9	2	2	0.9	0.9	0.9	0.9	2	2	1	1	0	1	0.1	0.2	0	0	0.9	0.8	0.1	1	0.36	0.18	0.07	0.02
            """,
        )
        guitar = write(
            root / "guitar.tsv",
            """
recording_id	status	expected_chords	expected_chord_qualities	quality	expected_label	expected_root	expected_quality_compact	guitar_match_kind	chord_hit	simple_chord_hit	guitar_chord_hit	expected_label_in_display	expected_label_in_raw	expected_label_in_smooth	expected_root_in_display	guitar_chord	guitar_raw_chord	guitar_smoothed_chord	guitar_chord_confidence	guitar_raw_chord_confidence	guitar_smoothed_chord_confidence	global_chord	support	expected_pitch_classes	guitar_pitch_classes	guitar_analysis_pitch_classes	guitar_smoothed_pitch_classes	visible_missing_tones	analysis_missing_tones	smooth_missing_tones	evidence_class	evidence_source	visible_root	visible_third	visible_fifth	analysis_root	analysis_third	analysis_fifth	smooth_root	smooth_third	smooth_fifth	raw_root	raw_third	raw_fifth	raw_opposite_third	raw_third_anchor_ratio	raw_third_opposite_margin	guitar_note_hits	guitar_false_positive_pitch_classes	rms
g1	chord_hit	C	major	maj	C	C	maj	display_exact	1	1	1	1	1	1	1	C	C	C	0.92	0.90	0.88	C	visible3	C,E,G	C,E,G	C,E,G	C,E,G	--	--	--	display_exact	display	1	1	1	1	1	1	1	1	1	1	1	1	0	1	1	3	0	0.2
g2	chord_miss	Am	minor	m	Am	A	m	display_same_root_other	0	0	0	0	0	0	1	Asus2	Asus2	Asus2	0.40	0.35	0.34	--	visible2	A,C,E	A,C	A,C	A,C	fifth	fifth	fifth	fifth_missing	grid	1	1	0	1	1	0	1	1	0	1	1	0.2	0.1	1	0.9	2	0	0.2
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
                "--top",
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
    assert "display pitch quality=exact=1 octave_alias=1" in output
    assert "primary pitch quality=exact=2" in output
    assert (
        "exact-octave coverage debug[exact=2/2 100.0% pitch-class=2/2 100.0% octave-alias=0/2 0.0%] "
        "display[exact=1/2 50.0% pitch-class=2/2 100.0% octave-alias=1/2 50.0%] "
        "primary[exact=2/2 100.0% pitch-class=2/2 100.0% octave-alias=0/2 0.0%]"
    ) in output
    assert "target octave duplicates=guitar:dup1=1" in output
    assert "display octave alias buckets:" in output
    assert "1 guitar/-- expected=E3/52 detected=E4/+12 status=miss owner=piano" in output
    assert "primary octave alias buckets=--" in output
    assert "piano rows=1 notes=1 range=C4/60 hit=1/1 100.0%" in output
    assert "piano rows=1 notes=1 range=C4/60 hit=1/1 100.0% pitch=exact=1 display=exact=1 primary=exact=1 octdup=0=1" in output
    assert "guitar rows=1 notes=1 range=E3/52 hit=0/1 0.0%" in output
    assert "guitar rows=1 notes=1 range=E3/52 hit=0/1 0.0% pitch=exact=1 display=octave_alias=1 primary=exact=1 octdup=1=1" in output
    assert "program/note buckets:" in output
    assert (
        "guitar/-- expected=E3/52 rows=1 status=miss=1 debug=exact=1 "
        "display=octave_alias=1 primary=exact=1 owners=piano=1"
    ) in output
    assert "features=raw:0.7 tuned:0.8 cent:4 rank:2 pitch:0.7 periodic:0.6 fit:0.2" in output
    assert "scores=key:0.8 gtr:0.2 voc:0 oth:0" in output
    assert "miss guitar expected=E3/52 display=E4/12 primary=E3/0 got=E3/piano" in output
    assert "octdup=1" in output
    assert "measured real-note full-mix rows" in output
    assert "debug owner mismatches=piano->guitar=1" in output
    assert "pitch quality=exact=2" in output
    assert (
        "exact-octave coverage debug[exact=2/3 66.7% pitch-class=3/3 100.0% octave-alias=1/3 33.3%]"
    ) in output
    assert (
        "grid exact-octave coverage expected-row[exact=3/3 100.0% pitch-class=3/3 100.0%] "
        "strongest-row[exact=3/3 100.0% pitch-class=3/3 100.0%] "
        "any-row[exact=3/3 100.0% pitch-class=3/3 100.0%]"
    ) in output
    assert (
        "visual grid exact-octave coverage expected-row[exact=3/3 100.0% pitch-class=3/3 100.0%] "
        "strongest-row[exact=3/3 100.0% pitch-class=3/3 100.0%] "
        "any-row[exact=3/3 100.0% pitch-class=3/3 100.0%]"
    ) in output
    assert (
        "visual full-highlight>=0.25 coverage expected-row[exact=2/3 66.7% pitch-class=2/3 66.7%] "
        "strongest-row[exact=2/3 66.7% pitch-class=2/3 66.7%]"
    ) in output
    assert (
        "row routing expected-row exact=3/3 100.0% first-row expected=2/3 66.7% "
        "strongest-row expected=2/3 66.7% visual-row exact=3/3 100.0% "
        "visual-strongest expected=2/3 66.7% visual-lit exact=2/3 66.7% "
        "visual-strongest-lit expected=2/3 66.7%"
    ) in output
    assert "first-row routes=guitar/acoustic->guitar=1 piano/electronic->bass=1 bass/electric->bass=1" in output
    assert "visual-strongest routes=guitar/acoustic->guitar=1 piano/electronic->guitar=1 bass/electric->bass=1" in output
    assert "same-midi spillover>=0.25 entries=1 samples=1 routes=bass/electric->guitar=1" in output
    assert "detected octave alias buckets:" in output
    assert "1 bass/electric expected=E2/40 detected=E3/+12 status=hit owner=bass" in output
    assert "guitar rows=1 samples=1 notes=1 range=E3/52 hit=1/1 100.0%" in output
    assert "guitar rows=1 samples=1 notes=1 range=E3/52 hit=1/1 100.0% pitch=exact=1 expected-row=1/1 100.0% first-row=1/1 100.0% strongest-row=1/1 100.0% visual-row=1/1 100.0% visual-strongest=1/1 100.0% visual-lit=1/1 100.0% visual-strongest-lit=1/1 100.0%" in output
    assert "piano rows=1 samples=1 notes=1 range=C4/60 hit=0/1 0.0%" in output
    assert "piano rows=1 samples=1 notes=1 range=C4/60 hit=0/1 0.0% pitch=exact=1 expected-row=1/1 100.0% first-row=0/1 0.0% strongest-row=0/1 0.0% visual-row=1/1 100.0% visual-strongest=0/1 0.0% visual-lit=0/1 0.0% visual-strongest-lit=0/1 0.0%" in output
    assert "source/note buckets:" in output
    assert (
        "piano/electronic expected=C4/60 rows=1 status=ownership_miss=1 "
        "debug=exact=1 owners=guitar=1"
    ) in output
    assert "features=raw:1 tuned:1 cent:0 rank:1 pitch:0.8 periodic:0.7 fit:0.1" in output
    assert "scores=key:0.4 gtr:0.6 voc:0 oth:0" in output
    assert "ownership_miss piano/electronic expected=C4/60 first=bass" in output
    assert "partials=p1:1,p2:0.25,p3:0.11,p4:0.03,p5:0.01 sample=s2" in output
    assert "measured guitar chord rows" in output
    assert "maj chord_hit=1/1 100.0%" in output
    assert "m chord_hit=0/1 0.0%" in output
    assert "expected chord buckets:" in output
    assert (
        "Am quality=m rows=1 status=chord_miss=1 match=display_same_root_other=1 "
        "display=Asus2=1 evidence=fifth_missing=1"
    ) in output
    assert "conf=disp:0.4 raw:0.35 smooth:0.34 rms:0.2" in output
    assert "tones=vr:1 v3:1 v5:0 ar:1 a3:1 a5:0 rr:1 r3:1 r5:0.2 anchor:1 margin:0.9" in output
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
