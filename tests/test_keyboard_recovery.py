from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_keyboard_recovery import coverage
from evaluate_keyboard_recovery import eligible


class KeyboardRecoveryTests(unittest.TestCase):
    def candidate(self, **changes):
        row = dict(midi='60', keys='', guitar='60', mfcc_valid='1', profile='0',
                   keyboard_score='.9', guitar_score='.01', vocal_score='.01')
        return dict(row, **changes)

    def test_recovery_needs_other_row_pitch_and_missing_keyboard(self):
        self.assertTrue(eligible(self.candidate()))
        self.assertFalse(eligible(self.candidate(keys='60')))
        self.assertFalse(eligible(self.candidate(guitar='61')))
        self.assertFalse(eligible(self.candidate(midi='-1')))

    def test_profile_and_nonfinite_evidence_fail_closed(self):
        self.assertFalse(eligible(self.candidate(profile='1')))
        self.assertFalse(eligible(self.candidate(mfcc_valid='0')))
        self.assertFalse(eligible(self.candidate(keyboard_score='nan')))
        self.assertFalse(eligible(self.candidate(vocal_score='inf')))

    def test_labels_cover_next_hop_without_backdating(self):
        self.assertAlmostEqual(coverage([(0., .12)], .1, .15), .02)
        self.assertEqual(coverage([(0., .1)], .1, .15), 0.)
        self.assertAlmostEqual(coverage([(.1, .15)], .1, .15), .05)


if __name__ == '__main__':
    unittest.main()
