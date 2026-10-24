#!/usr/bin/env python3
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from measure_sustained_piano import score


class Tests(unittest.TestCase):
    def test_held_note_recall_and_foreign_rows(self):
        rows = [dict(end_sample="4800", bass="", guitar="60", keys="", voice="", other="")]
        notes = [dict(midi=60, channel=0, start=0., key_end=.5, end=.5)]
        result = score(rows, notes, 48000)
        self.assertEqual(result["missing_any_row_note_seconds"], 0.)
        self.assertEqual(result["missing_keyboard_note_seconds"], .05)
        self.assertEqual(result["foreign_guitar_frame_seconds"], .05)

    def test_pedal_grace_is_not_called_wrong_pitch(self):
        rows = [dict(end_sample="24000", bass="", guitar="", keys="60", voice="", other="")]
        notes = [dict(midi=60, channel=0, start=0., key_end=.2, end=.3)]
        result = score(rows, notes, 48000)
        self.assertEqual(result["held_note_seconds"], 0.)
        self.assertEqual(result["unsupported_pitch_note_seconds"], 0.)


if __name__ == "__main__":
    unittest.main()
