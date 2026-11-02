import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from capture_joint_note_coverage import causal_windows


class CausalWindowsTest(unittest.TestCase):
    def test_first_endpoint_has_only_past_audio(self):
        audio = np.arange(3200, dtype=float)
        frames = causal_windows(audio, 16000)
        np.testing.assert_array_equal(frames[0, :800], 0)
        np.testing.assert_array_equal(frames[0, 800:], audio[:800])
        np.testing.assert_array_equal(frames[1], audio[:1600])
        np.testing.assert_array_equal(frames[2], audio[800:2400])

    def test_future_audio_cannot_change_prior_windows(self):
        for rate in (16000, 44100, 48000):
            audio = np.arange(round(rate * .2), dtype=float)
            original = causal_windows(audio, rate)
            audio[round(rate * .1):] *= -10
            modified = causal_windows(audio, rate)
            np.testing.assert_array_equal(original[:2], modified[:2])
            self.assertFalse(np.array_equal(original[-1], modified[-1]))


if __name__ == '__main__':
    unittest.main()
