#!/usr/bin/env python3
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_drum_attack_shapes import features, decode_pcm
import numpy as np


class Tests(unittest.TestCase):
    def test_amplitude_invariance(self):
        t = np.arange(4800) / 48000
        sound = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30)
        np.testing.assert_allclose(features(sound, 48000), features(sound * .03, 48000), atol=1e-8)

    def test_invalid_and_silent_input(self):
        self.assertIsNone(features(np.zeros(4800), 48000))
        self.assertIsNone(features(np.full(4800, np.nan), 48000))

    def test_tonal_and_noisy_flatness_differ(self):
        tone = np.sin(2 * np.pi * 440 * np.arange(4800) / 48000)
        noise = np.random.default_rng(0).normal(size=4800)
        self.assertGreater(features(noise, 48000)[-4], features(tone, 48000)[-4])

    def test_24_bit_signed_pcm(self):
        np.testing.assert_allclose(decode_pcm(bytes.fromhex("000080000000ffff7f"), 3, 1), [-1., 0., 8388607 / 8388608])


if __name__ == "__main__":
    unittest.main()
