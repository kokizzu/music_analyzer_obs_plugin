from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from trace_keyboard_stages import attribute


class AttributionTests(unittest.TestCase):
    def events(self, changes):
        return [dict(sequence=str(i), stage=stage, between='0', midi=str(midi), before=str(before), after=str(after))
                for i, (stage, midi, before, after) in enumerate([('frame', -1, 0, 0)] + changes)]

    def test_final_origin_tracks_resurrection(self):
        initial, origins, removed = attribute(self.events([('initial', 60, 0, .5), ('suppress', 60, .5, 0), ('recover', 60, 0, .2)]), {60})
        self.assertEqual((initial, origins, removed), ({60}, {60: 'recover'}, {60: 'suppress'}))

    def test_final_loss_is_attributed_to_last_remover(self):
        initial, origins, removed = attribute(self.events([('initial', 60, 0, .5), ('clear', 60, .5, 0)]), set())
        self.assertEqual((initial, origins, removed), ({60}, {}, {60: 'clear'}))

    def test_broken_transition_and_wrong_final_state_fail(self):
        with self.assertRaises(AssertionError):
            attribute(self.events([('clear', 60, .5, 0)]), set())
        with self.assertRaises(AssertionError):
            attribute(self.events([('add', 60, 0, .5)]), set())


if __name__ == '__main__':
    unittest.main()
