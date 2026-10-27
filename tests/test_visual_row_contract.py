import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from visual_row_contract import assert_visual_row_contract


def fixture(stable):
    metric = 'stable-visual' if stable else 'visual'
    makefile = f'REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT ?= {67 if stable else 38}\n'
    recipe = ' '.join(f'--{prefix}min-{metric}-row-percent "$(REAL_NOTE_FULL_MIX_AGG_MIN_{family}VISUAL_ROW_PERCENT)"'
                      for prefix, family in (('', ''), ('guitar-', 'GUITAR_'), ('other-', 'OTHER_')))
    if stable:
        recipe += ' ' + ' '.join(f'--{prefix}min-visual-row-percent 0'
                                 for prefix in ('', 'bass-', 'guitar-', 'piano-', 'vocals-', 'other-'))
    return makefile, recipe


class VisualRowContractTests(unittest.TestCase):
    def test_legacy_metric(self):
        assert_visual_row_contract(*fixture(False))

    def test_stable_metric(self):
        assert_visual_row_contract(*fixture(True))

    def test_stable_metric_rejects_obsolete_floor(self):
        makefile, recipe = fixture(True)
        with self.assertRaisesRegex(AssertionError, '>= 67'):
            assert_visual_row_contract(makefile.replace('67', '38'), recipe)

    def test_stronger_floor_is_allowed(self):
        makefile, recipe = fixture(True)
        assert_visual_row_contract(makefile.replace('67', '70'), recipe)

    def test_wrong_metric_binding_is_rejected(self):
        makefile, recipe = fixture(True)
        with self.assertRaisesRegex(AssertionError, 'bind'):
            assert_visual_row_contract(makefile, recipe.replace('--guitar-min-stable-visual', '--guitar-min-visual'))

    def test_parallel_legacy_gate_is_rejected(self):
        makefile, recipe = fixture(True)
        with self.assertRaisesRegex(AssertionError, 'disable legacy'):
            assert_visual_row_contract(makefile, recipe.replace('--min-visual-row-percent 0', '--min-visual-row-percent 38'))


if __name__ == '__main__':
    unittest.main()
