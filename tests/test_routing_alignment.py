import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from routing_alignment import lag_evidence


class AlignmentTests(unittest.TestCase):
    def test_known_positive_and_negative_offsets(self):
        import numpy as np
        reference = np.zeros(1000)
        reference[[100, 183, 294, 408, 592, 744, 885]] = [1, 3, 2, 4, 1, 5, 2]
        for shift in (12, -8, 0):
            result = lag_evidence(np.roll(reference, shift), reference, .01)
            self.assertEqual(result['audio_lag_ms'], shift * 10)
            self.assertGreater(result['best_correlation'], .99)

    def test_silence_is_not_proof_of_alignment(self):
        self.assertFalse(lag_evidence([0.] * 100, [0.] * 100, .01)['valid'])

    def test_invalid_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            lag_evidence([1.] * 100, [1.] * 99, .01)


if __name__ == '__main__':
    unittest.main()
