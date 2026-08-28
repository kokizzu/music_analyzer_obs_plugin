#!/usr/bin/env python3
"""Guard generic early-onset hi-hat recovery against tonal full-mix bleed."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/analyzer.cpp"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    require("generic_early_onset_hihat_evidence" in source,
            "generic early-onset hi-hat recovery is not separately guarded")
    require("drum_segment_bands[HiHat] >= 1.20f" in source,
            "generic hi-hat recovery lacks a minimum cymbal-band floor")
    require("drum_segment_bands[HiHat] >= strongest_cymbal_drum * 0.62f" in source,
            "generic hi-hat recovery lacks dominant hi-hat evidence")
    require("snapshot.drum_debug_trigger_scores[HiHat] >= trigger_threshold * 2.50f" in source,
            "generic hi-hat recovery lacks a strict local trigger requirement")
    require("real_drum_track_source || generic_early_onset_hihat_evidence" in source,
            "labelled real drum tracks must retain early hi-hat recovery")
    require("snapshot.drum_debug_onset <= 2.49f &&\n\t\t(real_drum_track_source || generic_early_onset_hihat_evidence)" in source,
            "final early hi-hat recovery must require dominant cymbal evidence in generic mixes")
    require("drum_segment_bands[Ride] <= 1.15f &&\n\t\t(real_drum_track_source || generic_early_onset_hihat_evidence)" in source,
            "quiet-ride hi-hat recovery must require dominant cymbal evidence in generic mixes")
    require("generic_tonal_short_onset_hihat_bleed" in source,
            "generic tonal short-onset hi-hat bleed is not capped")
    require("onset <= 2.00f" in source and "snapshot.high_energy >= 0.20f" in source,
            "tonal hi-hat bleed cap must require a short, bright onset")
    require("cap_drum_level(HiHat, 0.28f)" in source,
            "tonal hi-hat bleed cap must keep the result below the visible threshold")
    require("final_generic_pure_tone_hihat_false_positive" in source,
            "generic pure-tone hi-hat bleed is not capped after recovery")
    require("input_mode == AnalysisInputMode::FullMix && !drum_transient && drum_level_[HiHat] > 0.30f" in source,
            "pure-tone hi-hat cap must not reject a genuine transient attack")
    require("snapshot.high_energy >= 0.95f" in source and
            "(snapshot.low_energy + snapshot.mid_energy) <= 0.05f" in source,
            "pure-tone hi-hat cap must remain limited to near-all-high-band tones")
    print("check_hihat_early_recovery_guard: ok")


if __name__ == "__main__":
    main()
