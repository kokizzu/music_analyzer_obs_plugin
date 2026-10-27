"""Assert visual-row gate policy across legacy and stable-metric recipes."""
import re


def assert_visual_row_contract(makefile, recipe):
    stable = '--min-stable-visual-row-percent' in recipe
    metric = 'stable-visual' if stable else 'visual'
    required_floor = 67 if stable else 38
    variable = 'REAL_NOTE_FULL_MIX_AGG_MIN_VISUAL_ROW_PERCENT'
    match = re.search(rf'^{variable}\s*\?=\s*(\d+)\s*$', makefile, re.MULTILINE)
    assert match, f'missing numeric default for {variable}'
    assert int(match.group(1)) >= required_floor, (
        f'{metric} aggregate floor must remain >= {required_floor}%'
    )
    bindings = [('', variable),
                ('guitar-', 'REAL_NOTE_FULL_MIX_AGG_MIN_GUITAR_VISUAL_ROW_PERCENT'),
                ('other-', 'REAL_NOTE_FULL_MIX_AGG_MIN_OTHER_VISUAL_ROW_PERCENT')]
    for prefix, setting in bindings:
        expected = f'--{prefix}min-{metric}-row-percent "$(' + setting + ')"'
        assert expected in recipe, f'aggregate checker must bind {expected}'
    if stable:
        for prefix in ('', 'bass-', 'guitar-', 'piano-', 'vocals-', 'other-'):
            expected = f'--{prefix}min-visual-row-percent 0'
            assert expected in recipe, f'stable gate must explicitly disable legacy gate: {expected}'
