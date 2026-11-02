"""Causal candidate eligibility for the isolated release-grace experiment."""
import math

STAGE = 'suppress_other_dominant_same_pitch_keyboard_shadows'


def eligible(smoothed, final, last_stage, confirmed, hits, previous_visible, relative, explained):
    return (smoothed and not final and last_stage == STAGE and confirmed and hits >= 3 and previous_visible >= 3 and
            math.isfinite(relative) and math.isfinite(explained) and relative >= .8 and explained >= .3)
