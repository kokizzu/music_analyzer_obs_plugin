import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from note_onset_score import score_onsets


def note(start,key_end,end=2.,midi=60,channel=0):
    return dict(start=start,key_end=key_end,end=end,midi=midi,channel=channel)


class OnsetScoreTest(unittest.TestCase):
    def test_repeated_strike_during_pedal_does_not_require_visibility_gap(self):
        result=score_onsets([(60,.15),(60,.55)],[note(.1,.2),note(.5,.6)],1.)
        self.assertEqual((result['matched'],result['missed'],result['unmatched']), (2,0,0))

    def test_one_prediction_cannot_match_two_strikes_and_early_is_unmatched(self):
        result=score_onsets([(60,.09),(60,.16)],[note(.1,.3),note(.15,.3)],1.)
        self.assertEqual((result['matched'],result['missed'],result['unmatched']), (1,1,1))

    def test_short_later_note_does_not_lose_feasible_match(self):
        result=score_onsets([(60,.125),(60,.20)],[note(.1,.4),note(.12,.13)],1.)
        self.assertEqual(result['matched'],2)

    def test_percussion_and_right_censoring(self):
        result=score_onsets([], [note(.1,.2,channel=9),note(.95,1.2,end=1.4)],1.)
        self.assertEqual((result['missed'],result['censored']), (0,1))

    def test_invalid_and_future_events_fail(self):
        for events in ([(60,1.01)],[(60,float('nan'))],[(128,.2)],[(60,-.1)]):
            with self.assertRaises(ValueError):
                score_onsets(events,[],1.)


if __name__=='__main__':
    unittest.main()
