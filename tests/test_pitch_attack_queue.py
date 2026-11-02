import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pitch_attack_queue import simulate_latest,available_result


class QueueTest(unittest.TestCase):
    def test_latest_pending_and_completion_clock(self):
        events=[dict(end_sample=n,wall_ms=80.) for n in (100,150,200,250)]
        queue=simulate_latest(events,1000)
        self.assertEqual([r['model_end_sample'] for r in queue],[100,150,250])
        self.assertEqual([r['completed_sample'] for r in queue],[180,260,340])
        self.assertIsNone(available_result(queue,179,150))
        self.assertEqual(available_result(queue,200,150)['model_end_sample'],100)
        self.assertEqual(available_result(queue,250,150)['model_end_sample'],100)
        self.assertIsNone(available_result(queue,251,150))
        self.assertEqual(available_result(queue,260,150)['model_end_sample'],150)

    def test_rounds_execution_up_and_rejects_bad_clock(self):
        queue=simulate_latest([dict(end_sample=100,wall_ms=.1)],44100)
        self.assertEqual(queue[0]['completed_sample'],105)
        for events in ([dict(end_sample=1,wall_ms=-1.)],
                       [dict(end_sample=1,wall_ms=math.nan)],
                       [dict(end_sample=2,wall_ms=1.),dict(end_sample=1,wall_ms=1.)]):
            with self.assertRaises(ValueError):
                simulate_latest(events,1000)

    def test_preparation_is_paid_before_inference(self):
        queue=simulate_latest([dict(end_sample=90,ready_sample=100,wall_ms=20.)],1000)
        self.assertEqual(queue[0]['model_end_sample'],90)
        self.assertEqual(queue[0]['started_sample'],100)
        self.assertEqual(queue[0]['completed_sample'],120)
        self.assertIsNone(available_result(queue,119,150))
        with self.assertRaises(ValueError):
            simulate_latest([dict(end_sample=100,ready_sample=99,wall_ms=1.)],1000)


if __name__=='__main__':
    unittest.main()
