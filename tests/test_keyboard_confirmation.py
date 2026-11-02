import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_keyboard_confirmation import positive, values, isolated_additions
from evaluate_guitar_duplicate_model import FEATURES


class ConfirmationTest(unittest.TestCase):
    def test_isolated_flash_is_not_a_confirmation_bridge(self):
        frames = [dict(end_sample=10, keys=''), dict(end_sample=20, keys='60'), dict(end_sample=30, keys='')]
        accepted = [dict(end_sample=20, midi=60)]
        self.assertEqual(isolated_additions(frames, accepted, 10), 1)
        frames[-1]['keys'] = '60'
        self.assertEqual(isolated_additions(frames, accepted, 10), 0)

    def test_full_next_hop(self):
        self.assertTrue(positive(dict(held_seconds=.05, unsupported_seconds=0)))
        self.assertFalse(positive(dict(held_seconds=.049, unsupported_seconds=0)))
        self.assertFalse(positive(dict(held_seconds=0, unsupported_seconds=0)))
        self.assertFalse(positive(dict(held_seconds=.05, unsupported_seconds=.001)))
        self.assertTrue(positive(dict(held_seconds=0, unsupported_seconds=0), pedal_support=True))
        self.assertFalse(positive(dict(held_seconds=0, unsupported_seconds=.001), pedal_support=True))

    def test_features_have_no_labels_or_future(self):
        row = {key: '0' for key in FEATURES}
        case = dict(candidate=row, midi=60, tracking=dict(raw='.3', envelope='.1'), held_seconds=.05, unsupported_seconds=0)
        before = values(case)
        case.update(held_seconds=0, unsupported_seconds=.05)
        self.assertEqual(before, values(case))
        self.assertEqual(len(before), len(FEATURES) + 3)
        row['onset'] = 'nan'
        with self.assertRaises(AssertionError):
            values(case)


if __name__ == '__main__':
    unittest.main()
