import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from phase_low_keyboard_reference import geometry,projection,short_support
from audit_multiscale_exposure import project


class PhaseTest(unittest.TestCase):
    def test_amplitude_leakage_does_not_establish_pitch(self):
        for rate in (16000,44100,48000):
            count=round(rate*.4)
            hop=round(rate*.05)
            g=geometry(rate,.1)
            for played,accepted in ((36,True),(40,False)):
                f=440*2**((played-69)/12)
                audio=.2*np.sin(2*np.pi*f*np.arange(count)/rate)
                previous=projection(audio,count-hop,g)
                current=projection(audio,count,g)
                self.assertGreater(abs(current[36-21]),.01)
                self.assertEqual(36 in short_support(previous,current,hop/rate),accepted)
                np.testing.assert_allclose(np.abs(current),project(audio,count,g),atol=1e-12)
            self.assertEqual(short_support(None,current,hop/rate),set())
            silence=projection(np.zeros(count),count,g)
            self.assertEqual(short_support(silence,silence,hop/rate),set())


if __name__=='__main__':
    unittest.main()
