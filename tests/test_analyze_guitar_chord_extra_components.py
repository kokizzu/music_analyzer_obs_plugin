#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import importlib.util


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_guitar_chord_extra_components.py"


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write(
            pathlib.Path(tmpdir) / "guitar.tsv",
            """
recording_id	status	expected_chords	guitar_chord	expected_pitch_classes	guitar_cells	guitar_analysis_cells	guitar_match_kind	evidence_class	evidence_source
hit_equiv	chord_hit	Csus2	Csus2=Gsus4	C,D,G	C3:0.90,D3:0.82,G3:0.77	C3:0.91,D3:0.83,G3:0.78	display_exact	display_exact	display
hit_contains	chord_hit	Am	Am=C6	A,C,E	A2:0.90,C3:0.84,E3:0.80,G3:0.76	A2:0.91,C3:0.85,E3:0.81,G3:0.77	display_exact	display_exact	display
hit_same_root	chord_hit	C	C=Cmaj7=Cpow=Caug=Em	C,E,G	C3:0.90,E3:0.82,G3:0.76,B3:0.70,G#4:0.05	C3:0.91,E3:0.83,G3:0.77,B3:0.71,G#4:0.05	display_exact	display_exact	display
miss_unrelated	chord_miss	Dm	A#aug=Dpow	D,F,A	D3:0.88,A3:0.80	D3:0.89,A3:0.81	display_different_root	power_only_ambiguous	root_fifth
            """,
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--examples",
                "3",
                "--limit",
                "8",
                "--simulate-prune",
                "primary-equivalent",
                "--simulate-prune",
                "primary-equivalent-plain",
                "--simulate-prune",
                "primary-equivalent-plain-observed-playable",
                "--simulate-prune",
                "common-observed-playable",
                "--simulate-prune",
                "primary-same-root-equivalent",
                "--simulate-prune",
                "observed-playable",
                "--simulate-prune",
                "primary-equivalent-observed-playable",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    output = completed.stdout
    assert "guitar chord extra components rows=4/4 components=8 hit_rows=3 hit_components=6" in output
    assert "label component counts 2=3 5=1" in output
    assert "extra component counts 1=2 4=1 2=1" in output
    assert "crowded labels >=7 rows=0 hit_rows=0 max_components=5" in output
    assert "component suffixes pow=2 aug=2 sus4=1 6=1 maj7=1 m=1" in output
    assert "component relations" in output
    for text in (
        "contains_expected=2",
        "subset_of_expected=2",
        "different_root_extra=2",
        "same_pitch_set=1",
        "same_root_extra=1",
    ):
        assert text in output
    assert "hit component relations" in output
    for text in (
        "contains_expected=2",
        "same_pitch_set=1",
        "subset_of_expected=1",
        "same_root_extra=1",
        "different_root_extra=1",
    ):
        assert text in output
    assert "detected rootless subsets rootless_subset_of_Cmaj7=1" in output
    assert "hit detected rootless subsets rootless_subset_of_Cmaj7=1" in output
    assert "component standard-guitar playability playable=8" in output
    assert "hit component standard-guitar playability playable=6" in output
    assert "component observed-guitar playability display_analysis=6 unsupported=2" in output
    assert "hit component observed-guitar playability display_analysis=5 unsupported=1" in output
    assert "observed-guitar unsupported examples" in output
    assert "hit_same_root status=chord_hit expected=C got=C=Cmaj7=Cpow=Caug=Em extra=Caug" in output
    assert "detected rootless subset examples" in output
    assert "hit_same_root status=chord_hit expected=C got=C=Cmaj7=Cpow=Caug=Em extra=Em relation=rootless_subset_of_Cmaj7" in output
    assert "same_pitch_set examples" in output
    assert "hit_equiv status=chord_hit expected=Csus2 got=Csus2=Gsus4 extra=Gsus4" in output
    assert "contains_expected examples" in output
    assert "hit_contains status=chord_hit expected=Am got=Am=C6 extra=C6" in output
    assert "same_root_extra examples" in output
    assert "hit_same_root status=chord_hit expected=C got=C=Cmaj7=Cpow=Caug=Em extra=Caug" in output
    assert "different_root_extra examples" in output
    assert "miss_unrelated status=chord_miss expected=Dm got=A#aug=Dpow extra=A#aug" in output
    assert (
        "prune policy primary-equivalent: rows=4 current_hits=3 pruned_hits=3 "
        "lost_hits=0 gained_hits=0 components=5/11 extras=2/8"
    ) in output
    assert "  removed suffixes pow=2 6=1 maj7=1 aug=1 m=1" in output
    assert "  retained extra suffixes sus4=1 aug=1" in output
    assert (
        "prune policy primary-equivalent-plain: rows=4 current_hits=3 pruned_hits=3 "
        "lost_hits=0 gained_hits=0 components=6/11 extras=3/8"
    ) in output
    assert "  retained extra suffixes sus4=1 m=1 aug=1" in output
    assert (
        "prune policy primary-equivalent-plain-observed-playable: rows=4 current_hits=3 "
        "pruned_hits=3 lost_hits=0 gained_hits=0 components=10/11 extras=7/8"
    ) in output
    assert "  retained extra suffixes pow=2 sus4=1 6=1 maj7=1 m=1 aug=1" in output
    assert (
        "prune policy common-observed-playable: rows=4 current_hits=3 "
        "pruned_hits=3 lost_hits=0 gained_hits=0 components=10/11 extras=7/8"
    ) in output
    assert "  retained extra suffixes pow=2 sus4=1 6=1 maj7=1 m=1 aug=1" in output
    assert (
        "prune policy primary-same-root-equivalent: rows=4 current_hits=3 pruned_hits=3 "
        "lost_hits=0 gained_hits=0 components=8/11 extras=5/8"
    ) in output
    assert "  retained extra suffixes aug=2 sus4=1 maj7=1 pow=1" in output
    assert (
        "prune policy observed-playable: rows=4 current_hits=3 pruned_hits=3 "
        "lost_hits=0 gained_hits=0 components=10/11 extras=7/8"
    ) in output
    assert "  retained extra suffixes pow=2 sus4=1 6=1 maj7=1 m=1 aug=1" in output
    assert (
        "prune policy primary-equivalent-observed-playable: rows=4 current_hits=3 pruned_hits=3 "
        "lost_hits=0 gained_hits=0 components=10/11 extras=7/8"
    ) in output
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("analyze_guitar_chord_extra_components", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    unknown_suffix_row = {
        "guitar_cells": "C3:0.90,E3:0.80,G3:0.75",
        "guitar_analysis_cells": "C3:0.90,E3:0.80,G3:0.75",
    }
    assert module.prune_labels(["C", "C13"], "common-observed-playable", unknown_suffix_row) == ["C"]
    print("test_analyze_guitar_chord_extra_components: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
