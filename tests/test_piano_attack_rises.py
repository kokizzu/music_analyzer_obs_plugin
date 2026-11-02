import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from screen_piano_attack_rises import rising


class AttackRiseTest(unittest.TestCase):
    def test_preceding_history_only(self):
        activation=np.zeros((88,8))
        activation[60-21,:5]=[.1,.2,.3,.6,10.]
        self.assertFalse(rising(activation,2,60))
        self.assertTrue(rising(activation,3,60))
        activation[60-21,4:]=1000.
        self.assertTrue(rising(activation,3,60))
        activation[60-21,3]=.599
        self.assertFalse(rising(activation,3,60))
        activation[:]=0.
        self.assertFalse(rising(activation,3,60))


if __name__=='__main__':
    unittest.main()
