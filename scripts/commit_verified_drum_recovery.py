#!/usr/bin/env python3
"""Stage and commit only the verified mixed-drum recovery hunks."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = "src/analyzer.cpp"


def run(*args: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=ROOT, input=input_text, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result


def replace_in_block(text: str, marker: str, old: str, new: str) -> str:
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"missing required analyzer marker: {marker}")
    end = text.find(";", start)
    if end < 0:
        raise RuntimeError(f"unterminated analyzer marker: {marker}")
    block = text[start:end + 1]
    if block.count(old) != 1:
        raise RuntimeError(f"unexpected base form for: {marker}\n{block}")
    return text[:start] + block.replace(old, new) + text[end + 1:]


def stage_source() -> None:
    base = run("git", "show", f"HEAD:{SOURCE}").stdout
    current = (ROOT / SOURCE).read_text(encoding="utf-8")
    staged = base
    staged = replace_in_block(
        staged,
        "const bool kick_backed_snare_transient =",
        "!one_shot_drum_source && drum_transient && onset >= 1.55f &&",
        "drum_transient && onset >= 1.55f &&",
    )
    staged = replace_in_block(
        staged,
        "const bool final_real_mix_short_low_treble_snare_context_false_positive =",
        "drum_detection_enabled &&\n\t\t\t!one_shot_drum_source &&",
        "drum_detection_enabled &&\n\t\t\t!one_shot_drum_source &&\n\t\t\t!drum_transient &&",
    )
    staged = replace_in_block(
        staged,
        "const bool source_scoped_kick_heavy_snare_false_positive =",
        "drum_detection_enabled && !one_shot_drum_source &&\n"
        "\t\t\tdrum_level_[Snare] > 0.30f && kick_body >= 108.56f && rms <= 0.2712f",
        "drum_detection_enabled && !one_shot_drum_source &&\n"
        "\t\t\tdrum_level_[Snare] > 0.30f && !kick_backed_snare_transient &&\n"
        "\t\t\tkick_body >= 108.56f && rms <= 0.2712f",
    )
    staged = replace_in_block(
        staged,
        "const bool mixed_mid_dominant_kick_bleed =",
        "snapshot.mid_energy >= 0.39f;",
        "snapshot.mid_energy >= 0.39f &&\n"
        "\t\t!(snapshot.low_energy >= 0.42f && snapshot.mid_energy <= 0.46f &&\n"
        "\t\t  kick_body >= 90.0f && onset >= 1.0f &&\n"
        "\t\t  snapshot.drum_debug_trigger_scores[Kick] >=\n"
        "\t\t\t  snapshot.drum_debug_trigger_thresholds[Kick] * 3.0f);",
    )
    for marker in (
        "const bool kick_backed_snare_transient =",
        "const bool final_real_mix_short_low_treble_snare_context_false_positive =",
        "const bool source_scoped_kick_heavy_snare_false_positive =",
        "const bool mixed_mid_dominant_kick_bleed =",
    ):
        start = staged.find(marker)
        end = staged.find(";", start)
        block = staged[start:end + 1]
        if block not in current:
            current_start = current.find(marker)
            current_end = current.find(";", current_start)
            raise RuntimeError(
                f"working tree diverged from verified staged hunk: {marker}\n"
                f"expected:\n{block}\ncurrent:\n{current[current_start:current_end + 1]}"
            )
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as before_file:
        before_file.write(base)
        before = Path(before_file.name)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as after_file:
        after_file.write(staged)
        after = Path(after_file.name)
    try:
        diff = run("git", "diff", "--no-index", str(before), str(after), check=False)
        if diff.returncode not in (0, 1) or not diff.stdout:
            raise RuntimeError(diff.stderr or "unable to construct verified drum patch")
        patch = diff.stdout.replace(f"a{before}", f"a/{SOURCE}")
        patch = patch.replace(f"b{after}", f"b/{SOURCE}")
        run("git", "apply", "--cached", input_text=patch)
    finally:
        before.unlink(missing_ok=True)
        after.unlink(missing_ok=True)


def main() -> int:
    if run("git", "diff", "--cached", "--quiet", check=False).returncode != 0:
        raise RuntimeError("index is not empty; refusing to mix this fix with existing staged work")
    stage_source()
    staged = run("git", "diff", "--cached", "--name-only").stdout.splitlines()
    if staged != [SOURCE]:
        raise RuntimeError(f"unexpected staged paths: {staged}")
    run("git", "commit", "-m", "Recover corroborated mixed drum hits")
    print("committed verified mixed drum recovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
