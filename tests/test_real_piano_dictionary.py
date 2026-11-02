import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from transfer_real_piano_dictionary import label_mask


class FittingLabelsTest(unittest.TestCase):
    def test_no_future_note_and_pedal_context(self):
        times=np.array([.1,.2,.25,.5,.8,.9,1.])
        notes=[dict(midi=60,channel=0,start=.2,key_end=.3,end=.5),
               dict(midi=61,channel=9,start=0.,key_end=1.,end=1.),
               dict(midi=109,channel=0,start=0.,key_end=1.,end=1.)]
        mask=label_mask(notes,times)
        np.testing.assert_array_equal(mask[60-21],[False,False,True,True,True,False,False])
        self.assertFalse(mask[61-21].any())
        self.assertEqual(mask.shape,(88,len(times)))


if __name__=='__main__':
    unittest.main()
