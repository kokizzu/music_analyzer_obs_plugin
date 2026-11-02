import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from piano_context_features import features, negative_cohort, nsynth_group


class ContextFeaturesTest(unittest.TestCase):
    def test_source_identity_split_survives_pitch_velocity_and_rate(self):
        a = nsynth_group('brass_acoustic_006-039-025-original')
        b = nsynth_group('brass_acoustic_006-070-127-48k')
        self.assertEqual(a, b)
        self.assertEqual(negative_cohort(a), negative_cohort(b))
        self.assertNotEqual(a, nsynth_group('brass_acoustic_007-039-025'))

    def test_current_window_and_scale(self):
        rate = 16000
        audio = (.2*np.sin(2*np.pi*440*np.arange(1600)/rate)).astype(np.float32)
        original = features(audio, rate)
        self.assertEqual(len(original), 27)
        np.testing.assert_allclose(original, features(audio*.5, rate), atol=1e-8)
        np.testing.assert_allclose(original, features(np.concatenate((np.ones(1000), audio)), rate), atol=1e-8)
        self.assertIsNone(features(np.zeros(1600), rate))


if __name__ == '__main__':
    unittest.main()
