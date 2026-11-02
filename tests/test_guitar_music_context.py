import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_guitar_music_model import frame_context


class ContextTests(unittest.TestCase):
    def test_competing_guitar_evidence_is_retained(self):
        rows = [dict(midi='60', owner='2', profile='0'), dict(midi='48', owner='1', profile='0')]
        values = frame_context(rows)
        self.assertEqual(values[1], .5)
        self.assertEqual(values[2], .5)
        self.assertEqual(sum(values[:6]), 1)
        self.assertEqual(values[8], 12 / 127)

    def test_order_and_prior_window_do_not_affect_context(self):
        rows = [dict(midi='60', owner='2', profile='0'), dict(midi='48', owner='1', profile='1')]
        expected = frame_context(rows)
        frame_context([dict(midi='100', owner='5', profile='1')] * 4)
        self.assertEqual(frame_context(list(reversed(rows))), expected)
        self.assertEqual(expected[6], .5)

    def test_empty_frame_marker_is_not_an_instrument(self):
        self.assertEqual(frame_context([dict(midi='-1', owner='5', profile='0')]), [0.] * 9)


if __name__ == '__main__':
    unittest.main()
