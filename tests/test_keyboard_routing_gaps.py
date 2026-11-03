import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_keyboard_routing_gaps import partition_attacks
from routing_duration_score import score


class AuditTest(unittest.TestCase):
    def test_separates_preexisting_visibility_from_wrong_family(self):
        frames=[dict(end_sample=str(i*800),keys='60',guitar='61',voice='',bass='',other='',ambiguous='') for i in range(1,9)]
        notes=[dict(channel=0,midi=m,start=.1,key_end=.3,end=.3) for m in (60,61,62)]
        actual=partition_attacks(frames,notes,16000,{}, {})
        reference=score(frames,notes,16000)['keys']
        self.assertEqual((actual['matched'],actual['missed']),(reference['matched_attacks'],reference['missed_attacks']))
        self.assertEqual(actual['categories'],dict(keyboard_already_visible_at_onset=1,guitar_or_voice_visible_by_deadline=1,no_observation_by_deadline=1))

    def test_prior_visibility_distinguishes_pedal_and_unsupported_history(self):
        frames=[dict(end_sample=str(i*800),keys='60',guitar='',voice='',bass='',other='',ambiguous='') for i in range(1,9)]
        notes=[dict(channel=0,midi=60,start=0.,key_end=.05,end=.25),dict(channel=0,midi=60,start=.1,key_end=.3,end=.3)]
        supported=partition_attacks(frames,notes,16000,{}, {})
        unsupported=partition_attacks(frames,notes[1:],16000,{}, {})
        self.assertEqual(supported['prior_visibility_context']['prior_note_sounding'],1)
        self.assertEqual(unsupported['prior_visibility_context']['no_prior_annotation_support'],1)


if __name__=='__main__':
    unittest.main()
