#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_sample_manifests.py"


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {needle!r} in:\n{text}")


def run_script(*paths: pathlib.Path) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--top-sources", "3", *(str(path) for path in paths)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_header_manifest_summary() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = pathlib.Path(tmpdir) / "real_note_samples" / "manifest.tsv"
        manifest.parent.mkdir()
        manifest.write_text(
            "\n".join(
                [
                    "id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities",
                    "a\tbass\tbass\telectronic\t29\tF1\ta.wav\t",
                    "b\tpiano\tkeyboard\tacoustic\t60\tC4\tb.wav\t",
                    "c\tpiano\tkeyboard\tacoustic\t64\tE4\tc.wav\t",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        output = run_script(manifest)

    require(output, f"sample_manifest path={manifest}")
    require(output, "rows=3 audio=0 notes=0")
    require(output, "families=piano=2,bass=1")
    require(output, "sources=acoustic=2,electronic=1")
    require(output, "midi=29-64(F1-E4)")
    require(output, "sample_manifest_total manifests=1 rows=3")


def test_event_manifest_summary() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = pathlib.Path(tmpdir) / "guitar_chord_mix_samples" / "manifest.tsv"
        manifest.parent.mkdir()
        manifest.write_text(
            "\n".join(
                [
                    "# Guitar analyzer manifest",
                    "AUDIO\tclip-a\ta.wav",
                    "NOTE\tclip-a\t0.100\t0.600\t40",
                    "NOTE\tclip-a\t0.100\t0.600\t47",
                    "AUDIO\tclip-b\tb.wav",
                    "NOTE\tclip-b\t1.000\t1.250\t64",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        output = run_script(manifest)

    require(output, f"sample_manifest path={manifest}")
    require(output, "rows=5 audio=2 notes=3")
    require(output, "families=guitar=5")
    require(output, "midi=40-64(E2-E4)")
    require(output, "duration=0.250-0.500s")
    require(output, "sample_manifest_total manifests=1 rows=5 audio=2 notes=3")


def test_combines_multiple_manifests() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        drums = root / "drum_samples" / "manifest.tsv"
        drums.parent.mkdir()
        drums.write_text(
            "\n".join(
                [
                    "category\tpath\tduration_seconds\tsource",
                    "kick\tkick/a.wav\t0.20\tkit-a",
                    "snare\tsnare/a.wav\t0.30\tkit-a",
                    "snare\tsnare/b.wav\t0.35\tkit-b",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        vocals = root / "vocadito_samples" / "manifest.tsv"
        vocals.parent.mkdir()
        vocals.write_text(
            "\n".join(
                [
                    "id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities",
                    "v1\tvocals\tvocals\tvocadito-a\t57\tA3\tv1.wav\t",
                    "v2\tvocals\tvocals\tvocadito-a\t60\tC4\tv2.wav\t",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        output = run_script(drums, vocals)

    require(output, "sample_manifest_total manifests=2 rows=5")
    require(output, "families=drums=3,vocals=2")
    require(output, "categories=snare=2,kick=1")
    require(output, "midi=57-60(A3-C4)")
    require(output, "duration=0.200-0.350s")


def test_midi_drum_kit_header_uses_drum_family_and_categories() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = pathlib.Path(tmpdir) / "drum_kit_samples" / "manifest.tsv"
        manifest.parent.mkdir()
        manifest.write_text(
            "\n".join(
                [
                    "family\tprogram\tprogram_name\tmidi\tpath\tnote\tsoundfont\tsignature",
                    "kick\t0\tKick\t35\tkick.wav\tB1\tkit.sf2\tabc",
                    "snare\t0\tSnare\t38\tsnare.wav\tD2\tkit.sf2\tabc",
                    "snare\t0\tSnare\t40\tsnare2.wav\tE2\tkit.sf2\tabc",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        output = run_script(manifest)

    require(output, "rows=3 audio=0 notes=0")
    require(output, "families=drums=3")
    require(output, "categories=snare=2,kick=1")
    require(output, "midi=35-40(B1-E2)")


if __name__ == "__main__":
    test_header_manifest_summary()
    test_event_manifest_summary()
    test_combines_multiple_manifests()
    test_midi_drum_kit_header_uses_drum_family_and_categories()
    print("test_summarize_sample_manifests: ok")
