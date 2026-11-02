import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from joint_grace_rules import eligible, STAGE


class GraceTest(unittest.TestCase):
    def test_eligibility_is_current_and_past_only(self):
        values = dict(smoothed=True, final=False, last_stage=STAGE, confirmed=True, hits=3,
                      previous_visible=3, relative=.8, explained=.3)
        self.assertTrue(eligible(**values))
        for name, value in [('smoothed', False), ('final', True), ('last_stage', 'other'), ('confirmed', False),
                            ('hits', 2), ('previous_visible', 2), ('relative', .79), ('explained', .29),
                            ('relative', float('nan'))]:
            self.assertFalse(eligible(**dict(values, **{name: value})), name)


if __name__ == '__main__':
    unittest.main()
