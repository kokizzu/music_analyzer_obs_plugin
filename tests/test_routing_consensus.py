from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_routing_consensus import confirmed


class RoutingConsensusTests(unittest.TestCase):
    def test_three_consecutive_predictions_required(self):
        hits = {}
        for expected in (set(), set(), {60}, {60}):
            actual, hits = confirmed({60}, hits)
            self.assertEqual(actual, expected)

    def test_missing_prediction_resets_confirmation(self):
        _, hits = confirmed({60}, {})
        _, hits = confirmed({60}, hits)
        actual, hits = confirmed(set(), hits)
        self.assertEqual((actual, hits), (set(), {}))
        actual, _ = confirmed({60}, hits)
        self.assertEqual(actual, set())

    def test_pitches_have_independent_confirmation(self):
        _, hits = confirmed({60}, {})
        _, hits = confirmed({60, 64}, hits)
        actual, hits = confirmed({60, 64}, hits)
        self.assertEqual(actual, {60})
        actual, _ = confirmed({64}, hits)
        self.assertEqual(actual, {64})


if __name__ == '__main__':
    unittest.main()
