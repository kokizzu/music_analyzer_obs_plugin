#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_philharmonia_samples


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
    candidate = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/guitar/guitar_E3_1_forte_normal.mp3",
    )
    if not candidate:
        raise AssertionError("expected guitar one-note candidate")
    if candidate["family"] != "guitar":
        raise AssertionError(f"guitar must remain guitar, got {candidate['family']}")


def test_orchestral_strings_remain_other_family():
    candidate = prepare_philharmonia_samples.parse_candidate(
        "Strings.zip",
        "Strings/violin/violin_A4_1_forte_arco-normal.mp3",
    )
    if not candidate:
        raise AssertionError("expected violin one-note candidate")
    if candidate["family"] != "other":
        raise AssertionError(f"violin must remain other, got {candidate['family']}")


def main():
    test_double_bass_is_real_bass_family()
    test_guitar_family_mapping_is_preserved()
    test_orchestral_strings_remain_other_family()
    print("test_prepare_philharmonia_samples: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
