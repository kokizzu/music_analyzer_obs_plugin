#!/usr/bin/env python3
from pathlib import Path
import math
import struct
import sys
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_philharmonia_samples


def midi_frequency(midi):
    return 440.0 * math.pow(2.0, (midi - 69) / 12.0)


def write_sine_mix(path, components, sample_rate=48000, seconds=1.5):
    frame_count = int(sample_rate * seconds)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            t = index / sample_rate
            value = 0.0
            for midi, amplitude in components:
                value += amplitude * math.sin(2.0 * math.pi * midi_frequency(midi) * t)
            value = max(-0.95, min(0.95, value))
            frames.extend(struct.pack("<h", int(value * 32767.0)))
        wav.writeframes(bytes(frames))


def test_double_bass_is_real_bass_family():
    candidate = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/double-bass/double-bass_G2_1_forte_arco-normal.mp3",
    )
    if not candidate:
        raise AssertionError("expected double-bass one-note candidate")
    if candidate["family"] != "bass":
        raise AssertionError(f"double-bass must map to bass, got {candidate['family']}")
    if candidate["midi"] != 43:
        raise AssertionError(f"expected G2 midi 43, got {candidate['midi']}")


def test_guitar_family_mapping_is_preserved():
    guitar = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/guitar/guitar_E3_1_forte_normal.mp3",
    )
    if not guitar:
        raise AssertionError("expected guitar one-note candidate")
    if guitar["family"] != "guitar":
        raise AssertionError(f"guitar must remain guitar, got {guitar['family']}")

    mandolin = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/mandolin/mandolin_G4_1_forte_normal.mp3",
    )
    if not mandolin:
        raise AssertionError("expected mandolin one-note candidate")
    if mandolin["family"] != "guitar":
        raise AssertionError(f"mandolin must map to guitar-family, got {mandolin['family']}")

    high_mandolin = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/mandolin/mandolin_Fs6_1_piano_normal.mp3",
    )
    if not high_mandolin:
        raise AssertionError("expected high mandolin one-note candidate")
    if high_mandolin["family"] != "other":
        raise AssertionError(f"mandolin above E6 must stay other, got {high_mandolin['family']}")


def test_orchestral_strings_remain_other_family():
    candidate = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/violin/violin_A4_1_forte_arco-normal.mp3",
    )
    if not candidate:
        raise AssertionError("expected violin one-note candidate")
    if candidate["family"] != "other":
        raise AssertionError(f"violin must remain other, got {candidate['family']}")


def test_manifest_writer_supports_partial_and_final_outputs():
    row = {
        "id": "philharmonia_test",
        "family": "other",
        "collection": "strings",
        "instrument": "violin",
        "midi": 69,
        "note": "A4",
        "path": "audio/violin_A4.wav",
        "qualities": "normal",
    }
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp)
        partial = prepare_philharmonia_samples.write_manifest([row], output, partial=True)
        if partial.name != "manifest.tsv.partial":
            raise AssertionError(f"unexpected partial manifest name: {partial}")
        if (output / "manifest.tsv.partial.tmp").exists():
            raise AssertionError("partial manifest temporary file should be atomically replaced")
        if "philharmonia_test" not in partial.read_text(encoding="utf-8"):
            raise AssertionError("partial manifest should contain prepared rows")

        final = prepare_philharmonia_samples.write_manifest([row], output)
        if final.name != "manifest.tsv":
            raise AssertionError(f"unexpected final manifest name: {final}")
        if (output / "manifest.tsv.tmp").exists():
            raise AssertionError("final manifest temporary file should be atomically replaced")
        if "audio/violin_A4.wav" not in final.read_text(encoding="utf-8"):
            raise AssertionError("final manifest should contain prepared rows")


def test_manifest_complete_requires_existing_audio_and_minimum_rows():
    row = {
        "id": "philharmonia_test",
        "family": "other",
        "collection": "strings",
        "instrument": "violin",
        "midi": 69,
        "note": "A4",
        "path": "audio/violin_A4.wav",
        "qualities": "normal",
    }
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp)
        manifest = prepare_philharmonia_samples.write_manifest([row], output)
        if prepare_philharmonia_samples.manifest_complete(manifest, 1):
            raise AssertionError("manifest without referenced audio must not be complete")

        audio = output / row["path"]
        audio.parent.mkdir(parents=True, exist_ok=True)
        write_sine_mix(audio, [(69, 0.45)], seconds=0.1)
        if not prepare_philharmonia_samples.manifest_complete(manifest, 1):
            raise AssertionError("manifest with referenced audio should be complete")
        if prepare_philharmonia_samples.manifest_complete(manifest, 2):
            raise AssertionError("manifest below the requested minimum must not be complete")


def test_pitch_reference_filter_uses_analyzer_style_windows():
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp)
        clean = output / "clean_a4.wav"
        shifted = output / "shifted_a4.wav"
        low_artifact = output / "high_with_low_artifact.wav"

        write_sine_mix(clean, [(69, 0.45)])
        if not prepare_philharmonia_samples.pitch_reference_ok(clean, 69):
            raise AssertionError("clean A4 reference should pass")

        write_sine_mix(shifted, [(70, 0.45)])
        if prepare_philharmonia_samples.pitch_reference_ok(shifted, 69):
            raise AssertionError("adjacent-semitone A#4 should not pass as A4")

        write_sine_mix(low_artifact, [(21, 0.60), (91, 0.05)])
        if prepare_philharmonia_samples.pitch_reference_ok(low_artifact, 91):
            raise AssertionError("high note dominated by low artifact should not pass")


def main():
    test_double_bass_is_real_bass_family()
    test_guitar_family_mapping_is_preserved()
    test_orchestral_strings_remain_other_family()
    test_manifest_writer_supports_partial_and_final_outputs()
    test_manifest_complete_requires_existing_audio_and_minimum_rows()
    test_pitch_reference_filter_uses_analyzer_style_windows()
    print("test_prepare_philharmonia_samples: 6 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
