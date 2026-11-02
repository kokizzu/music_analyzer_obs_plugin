import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from routing_duration_score import score


def frames(active, count=20):
    return [dict(end_sample=(i + 1) * 500, keys='60' if i + 1 in active else '',
                 guitar='', voice='', bass='', other='', ambiguous='') for i in range(count)]


def note(start=.1, key_end=.6, end=.6):
    return dict(midi=60, channel=0, start=start, key_end=key_end, end=end)


class DurationTests(unittest.TestCase):
    def test_separates_attack_dropout_and_early_release(self):
        result = score(frames({4, 5, 9, 10}), [note()], 10000, release_grace=0)
        keys = result['keys']
        self.assertAlmostEqual(keys['held_note_seconds'], .5)
        self.assertAlmostEqual(keys['missing_note_seconds'], .3)
        self.assertAlmostEqual(keys['onset_gap_seconds'], .1)
        self.assertAlmostEqual(keys['internal_dropout_seconds'], .15)
        self.assertAlmostEqual(keys['early_release_seconds'], .05)
        self.assertEqual(keys['matched_attacks'], 1)
        self.assertAlmostEqual(keys['attack_latency_ms'][0], 100)

    def test_pedal_support_does_not_become_acoustic_false_note_truth(self):
        rows = frames(set(range(2, 17)))
        reference = [note(key_end=.3, end=.7)]
        self.assertAlmostEqual(score(rows, reference, 10000)['keys']['annotation_unsupported_note_seconds'], 0)
        self.assertAlmostEqual(score(rows, reference, 10000, release_grace=0)['keys']['annotation_unsupported_note_seconds'], .15)

    def test_continuous_pitch_is_not_a_second_attack(self):
        result = score(frames(set(range(2, 14))), [note(.1, .3, .3), note(.4, .6, .6)], 10000)
        self.assertEqual(result['keys']['matched_attacks'], 1)
        self.assertEqual(result['keys']['missed_attacks'], 1)
        self.assertEqual(result['keys']['missing_note_seconds'], 0)

    def test_overlapping_same_pitch_is_not_double_counted(self):
        result = score(frames(set(range(2, 14))), [note(.1, .5, .5), note(.3, .6, .6)], 10000)
        self.assertAlmostEqual(result['keys']['held_note_seconds'], .5)

    def test_ambiguous_notes_count_toward_any_row(self):
        rows = frames(set())
        for row in rows:
            row['ambiguous'] = '60'
        result = score(rows, [note()], 10000)
        self.assertEqual(result['any_row']['missing_note_seconds'], 0)
        self.assertAlmostEqual(result['keys']['missing_note_seconds'], .5)

    def test_foreign_row_note_duration_counts_polyphony(self):
        rows = frames(set())
        rows[2]['guitar'] = '60,64'
        result = score(rows, [], 10000)
        self.assertAlmostEqual(result['foreign_rows']['guitar_note_seconds'], .1)
        self.assertAlmostEqual(result['foreign_rows']['guitar_active_seconds'], .05)

    def test_missing_hop_is_rejected(self):
        rows = frames(set())
        del rows[3]
        with self.assertRaises(ValueError):
            score(rows, [note()], 10000)

    def test_startup_delay_is_not_hidden(self):
        result = score(frames(set(range(1, 5))), [note(0, .2, .2)], 10000)
        self.assertAlmostEqual(result['keys']['missing_note_seconds'], .05)
        self.assertEqual(result['keys']['attack_latency_ms'], [50])

    def test_attack_deadline_beyond_recording_is_censored(self):
        result = score(frames(set()), [note(.98, 1.2, 1.2)], 10000)
        self.assertEqual(result['censored_attacks'], 1)
        self.assertEqual(result['keys']['missed_attacks'], 0)
        self.assertAlmostEqual(result['keys']['held_note_seconds'], .02)

    def test_one_display_attack_cannot_match_two_midi_attacks(self):
        result = score(frames({4, 5}), [note(.1, .25, .25), note(.15, .3, .3)], 10000)
        self.assertEqual(result['keys']['matched_attacks'], 1)
        self.assertEqual(result['keys']['missed_attacks'], 1)


if __name__ == '__main__':
    unittest.main()
