import csv
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_voice_duration_candidates import screen


class CandidateScreenTests(unittest.TestCase):
    def run_screen(self, frames):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'capture.tsv'
            with path.open('w') as stream:
                writer = csv.DictWriter(stream, fieldnames=['end_sample', 'midi', 'keys', 'guitar', 'voice'], delimiter='\t')
                writer.writeheader()
                writer.writerows(dict(end_sample=index * 2400, midi='60', keys=keys, guitar=guitar, voice=voice)
                                 for index, (keys, guitar, voice) in enumerate(frames, 1))
            with patch('audit_voice_duration_candidates.frame_context', return_value=[]), \
                 patch('audit_voice_duration_candidates.eligible', return_value=True), \
                 patch('audit_voice_duration_candidates.features', return_value=[]), \
                 patch('audit_voice_duration_candidates.lower_probability', return_value=1.):
                return screen(path, dict(model={}, threshold=.9))

    def test_repair_does_not_extend_itself(self):
        result, changed = self.run_screen([('60', '', ''), ('', '60', ''), ('', '60', '')])
        self.assertEqual(result['keys_added'], 1)
        self.assertEqual(changed['keys'], [(4800, 60)])

    def test_requires_preceding_keyboard_and_current_other_row(self):
        result, _ = self.run_screen([('', '60', ''), ('60', '', ''), ('', '', '')])
        self.assertEqual(result['gap_candidates'], 0)

    def test_voice_removal_requires_same_visible_keyboard_pitch(self):
        result, changed = self.run_screen([('', '', '60'), ('60', '', '60')])
        self.assertEqual(result['voice_removed'], 1)
        self.assertEqual(changed['voice'], [(4800, 60)])


if __name__ == '__main__':
    unittest.main()
