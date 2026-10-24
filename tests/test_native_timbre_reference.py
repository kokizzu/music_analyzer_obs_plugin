#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess
import tempfile
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from native_timbre_reference import cepstra


class Tests(unittest.TestCase):
    def test_native_numpy_parity_across_rates(self):
        rng = np.random.default_rng(20261024)
        with tempfile.TemporaryDirectory(prefix="native-cepstra-") as temporary:
            directory = Path(temporary)
            for rate in (8000, 16000, 22050, 44100, 48000, 96000):
                t = np.arange(int(rate * .1 + .5)) / rate
                for kind in ("harmonic", "noise", "silence"):
                    samples = (.4 * np.sin(2 * np.pi * 220 * t) + .2 * np.sin(2 * np.pi * 660 * t)) * np.exp(-t * 10)
                    if kind == "noise": samples = rng.normal(0, .1, len(t))
                    if kind == "silence": samples[:] = 0
                    samples = samples.astype("<f4")
                    source, destination = directory / "input.f32", directory / "output.tsv"
                    source.write_bytes(samples.tobytes())
                    subprocess.run([str(ROOT / "build/native_timbre_features"), str(source), str(rate), str(destination)], check=True)
                    fields = destination.read_text().split()
                    expected = cepstra(samples, rate)
                    self.assertEqual(fields[0] == "1", expected is not None)
                    if expected is not None:
                        np.testing.assert_allclose(list(map(float, fields[1:])), expected, rtol=1e-7, atol=1e-7)


if __name__ == "__main__":
    unittest.main()
