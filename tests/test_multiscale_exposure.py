import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_multiscale_exposure import geometry, project


class ExposureTest(unittest.TestCase):
    def test_short_window_accepts_a_different_low_pitch(self):
        rate=16000
        frequency=440*2**((40-69)/12)
        audio=.2*np.sin(2*np.pi*frequency*np.arange(6400)/rate)
        short=project(audio,len(audio),geometry(rate,.1))
        long=project(audio,len(audio),geometry(rate,.4))
        self.assertGreater(short[36-21],.01)
        self.assertLess(max(long[36-21],long[36-21+19]),.01)
        self.assertIsNone(project(audio,100,geometry(rate,.1)))
        np.testing.assert_array_equal(project(np.zeros(6400),6400,geometry(rate,.4)),np.zeros(38))


if __name__=='__main__':
    unittest.main()
