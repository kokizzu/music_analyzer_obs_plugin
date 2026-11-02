import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from supervised_piano_dictionary import learn_dictionary
from joint_pitch_reference import fit


class DictionaryTest(unittest.TestCase):
    def test_learns_missing_timbre_energy_without_changing_unobserved_pitch(self):
        prior=np.array([[1.,0.],[0.,1.],[0.,0.]])
        observed=np.array([[.8,.8],[0.,0.],[.6,.6]])
        mask=np.array([[True,True],[False,False]])
        learned=learn_dictionary(prior,observed,mask,epochs=20)
        self.assertGreater(learned[2,0],.05)
        np.testing.assert_array_equal(learned[:,1],prior[:,1])
        np.testing.assert_allclose(np.linalg.norm(learned,axis=0),1.,atol=1e-12)
        before=np.linalg.norm(observed-prior@fit(prior,observed))
        after=np.linalg.norm(observed-learned@fit(learned,observed))
        self.assertLess(after,before)
        np.testing.assert_array_equal(learn_dictionary(prior,observed,np.zeros_like(mask)),prior)

    def test_rejects_invalid_supervision(self):
        prior=np.eye(2)
        observed=np.eye(2)
        for mask in (np.ones((3,2),dtype=bool),np.ones((2,2))):
            with self.assertRaises(ValueError):
                learn_dictionary(prior,observed,mask)
        with self.assertRaises(ValueError):
            learn_dictionary(prior,-observed,np.ones((2,2),dtype=bool))


if __name__=='__main__':
    unittest.main()
