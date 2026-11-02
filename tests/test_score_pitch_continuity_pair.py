import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from score_pitch_continuity_pair import evaluate


def fixture():
    primary=[dict(end_sample=str(i*800),bass='',guitar='',keys='60',voice='',other='',ambiguous='',chord='',bpm='0',confidence='0',drums='') for i in range(1,5)]
    paired=[dict(r,after_keys=r['keys'],unrelated_difference='',bpm_changed='0',survivor_changed='0') for r in primary]
    notes=[dict(channel=0,midi=60,start=.05,key_end=.15,end=.3)]
    return paired,primary,notes


class ScoreTest(unittest.TestCase):
    def test_detects_correct_note_loss(self):
        rows,primary,notes=fixture();rows[1]['after_keys']=''
        result=evaluate(rows,primary,notes,16000)
        self.assertFalse(result['passed']);self.assertAlmostEqual(result['deltas']['held_removed_seconds'],.05)

    def test_detects_wrong_addition_and_isolated_flash(self):
        rows,primary,notes=fixture();rows[1]['after_keys']='60,61'
        result=evaluate(rows,primary,notes,16000)
        self.assertFalse(result['passed']);self.assertAlmostEqual(result['deltas']['unsupported_added_seconds'],.05)
        self.assertEqual(result['deltas']['isolated_additions'],1)

    def test_requires_exact_primary(self):
        rows,primary,notes=fixture()
        self.assertTrue(evaluate(rows,primary,notes,16000)['passed'])
        rows[1]['voice']='60'
        with self.assertRaises(AssertionError):
            evaluate(rows,primary,notes,16000)

    def test_pedal_support_beyond_key_release_grace(self):
        _,original,_=fixture()
        primary=[dict(original[0],end_sample=str(i*800),keys='') for i in range(1,21)]
        paired=[dict(r,after_keys='60' if i in (10,11) else '',unrelated_difference='',bpm_changed='0',survivor_changed='0') for i,r in enumerate(primary)]
        note=dict(channel=0,midi=60,start=.05,key_end=.15,end=1.)
        sustained=evaluate(paired,primary,[note],16000)
        released=evaluate(paired,primary,[dict(note,end=.15)],16000)
        self.assertTrue(sustained['passed'])
        self.assertEqual(sustained['deltas']['unsupported_added_seconds'],0.)
        self.assertFalse(released['passed'])
        self.assertAlmostEqual(released['deltas']['unsupported_added_seconds'],.1)


if __name__=='__main__':
    unittest.main()
