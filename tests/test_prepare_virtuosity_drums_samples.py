#!/usr/bin/env python3
"""Unit checks for Virtuosity Drums filename-to-label selection."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_virtuosity_drums_samples import classify  # noqa: E402


def check(path: str, expected: str | None) -> None:
    actual = classify(Path(path))
    assert actual == expected, (path, actual, expected)


def main() -> int:
    check("Samples/oh/snare/oh_snare_rimshot_vl6.flac", "rim")
    check("Samples/oh/snare/oh_snare_crossstick_vl10.flac", "rim")
    check("Samples/oh/ltom/oh_ltom_center_vl8.flac", "tom")
    check("Samples/oh/htom/oh_htom_offcenter_vl5.flac", "tom")
    check("Samples/oh/ride/oh_ride_bell_vl3_rr1.flac", "ride")
    check("Samples/oh/ride/oh_ride_ride_vl2_rr4.flac", "ride")
    check("Samples/room/snare/room_snare_rimshot_vl6.flac", None)
    check("Samples/oh/snare/oh_snare_center_vl6.flac", None)
    print("test_prepare_virtuosity_drums_samples: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
