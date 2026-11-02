import sys
from pathlib import Path
import unittest

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from joint_pitch_reference import fit, spectrum


class JointPitchTest(unittest.TestCase):
    def test_harmonic_explanation_competes(self):
        dictionary = np.array([[1., 0.], [.8, 1.], [.5, .5]])
        dictionary /= np.linalg.norm(dictionary, axis=0)
        observed = dictionary[:, 1:]
        self.assertGreater(float((dictionary.T @ observed)[0, 0]), .5)
        activations = fit(dictionary, observed)
        self.assertLess(activations[0, 0], .03)
        self.assertGreater(activations[1, 0], .95)

    def test_columns_independent_and_nonnegative(self):
        dictionary = np.array([[1., .1], [.2, 1.], [.1, .3]])
        observations = dictionary @ np.array([[.3, .7], [.6, .2]])
        combined = fit(dictionary, observations)
        alone = np.column_stack([fit(dictionary, observations[:, i:i+1])[:, 0] for i in range(2)])
        np.testing.assert_allclose(combined, alone, atol=1e-12)
        self.assertTrue((combined >= 0).all())
        self.assertLess(np.linalg.norm(dictionary @ combined - observations), 1e-5)

    def test_silent_frame_and_nonfinite(self):
        self.assertEqual(float(spectrum(np.zeros((1, 1600))).sum()), 0)
        with self.assertRaises(AssertionError):
            fit(np.array([[np.nan]]), np.ones((1, 1)))


if __name__ == '__main__':
    unittest.main()
