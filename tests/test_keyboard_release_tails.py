import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_keyboard_release_tails import stale_tail


class ReleaseTailTest(unittest.TestCase):
    def test_postprocessing_addition_is_not_a_smoothing_tail(self):
        row=dict(raw='0',smoothed='0',final='.5',confirmed='0',envelope='0',misses='739')
        self.assertFalse(stale_tail(row,0.,0.))
        tail=dict(row,smoothed='.5',confirmed='1',envelope='.5',misses='2')
        self.assertTrue(stale_tail(tail,0.,0.))
        for change in (dict(raw='.1'),dict(final='0'),dict(misses='1'),dict(envelope='0'),dict(confirmed='0')):
            self.assertFalse(stale_tail(dict(tail,**change),0.,0.))
        self.assertFalse(stale_tail(tail,.01,0.))
        self.assertFalse(stale_tail(tail,0.,.01))
        self.assertFalse(stale_tail(tail,float('nan'),0.))


if __name__=='__main__':
    unittest.main()
