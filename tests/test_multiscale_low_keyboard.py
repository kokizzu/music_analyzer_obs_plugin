import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from screen_multiscale_low_keyboard import OriginalHistory


class HistoryTest(unittest.TestCase):
    def test_original_visibility_and_warmup(self):
        h=OriginalHistory()
        for _ in range(3):
            self.assertEqual(h.finish({21},set(),True),set())
        self.assertEqual(h.finish({21},set(),True),{21})
        self.assertEqual(h.finish({21},{21},True),set())
        self.assertEqual(h.finish({21},set(),True),set())
        h.finish(set(),{21},True)
        for _ in range(3):
            self.assertEqual(h.finish({21},set(),True),set())
        self.assertEqual(h.finish({21},set(),False),set())
        self.assertEqual(h.finish({21},set(),True),{21})

    def test_short_support_can_latch_before_long_warmup(self):
        h=OriginalHistory()
        h.finish({22},{22},False)
        for _ in range(8):
            self.assertEqual(h.finish({22},set(),True),set())


if __name__=='__main__':
    unittest.main()
