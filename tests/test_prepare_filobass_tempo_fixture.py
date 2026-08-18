#!/usr/bin/env python3

from pathlib import Path
import json
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_filobass_tempo_fixture as fixture  # noqa: E402


def time_signature_midi(numerator: int, denominator_power: int) -> bytes:
    track = b"\x00\xff\x58\x04" + bytes((numerator, denominator_power, 24, 8)) + b"\x00\xff\x2f\x00"
    return b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x01\xe0MTrk" + len(track).to_bytes(4, "big") + track


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        midi = root / "aligned.mid"
        midi.write_bytes(time_signature_midi(4, 2))
        assert fixture.midi_beats_per_bar(midi) == 4.0
        syncpoints = root / "swing-syncpoints.json"
        syncpoints.write_text(json.dumps([[bar, bar * 2.0] for bar in range(10)]), encoding="utf-8")
        assert fixture.syncpoint_downbeats(syncpoints) == [bar * 2.0 for bar in range(10)]
        offset, bpm = fixture.stable_segment(fixture.syncpoint_downbeats(syncpoints), 4.0, 14.0)
        assert offset == 0.0
        assert abs(bpm - 120.0) < 0.001
    print("test_prepare_filobass_tempo_fixture: 3 checks passed")


if __name__ == "__main__":
    main()
