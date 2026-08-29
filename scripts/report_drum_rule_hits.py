#!/usr/bin/env python3
"""Print fixture rows that triggered the tom-body/snare-tie recovery."""

import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOVERY_FLAG = 1 << 31
CATEGORY = os.environ.get("DRUM_RULE_HIT_CATEGORY", "tom")
RULE_FLAGS = re.compile(r"rule_flags=0x([0-9a-fA-F]+)")


def main() -> None:
    environment = os.environ.copy()
    environment.update({
        "MUSIC_ANALYZER_DRUM_SAMPLES_REQUIRED": "1",
        "MUSIC_ANALYZER_DRUM_SAMPLES_DIR": "build/drum_samples_spread",
        "MUSIC_ANALYZER_DRUM_SAMPLE_FILTER_CATEGORY": CATEGORY,
        "MUSIC_ANALYZER_DRUM_SAMPLE_REQUIRED_CATEGORIES": CATEGORY,
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRIMARY_RECALL_PERCENT": "0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_MIN_PRECISION_PERCENT": "0",
        "MUSIC_ANALYZER_DRUM_SAMPLE_VERBOSE_ALL": "1",
    })
    result = subprocess.run(
        [str(ROOT / "build" / "analyzer_drum_samples")], cwd=ROOT, env=environment,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    hits = []
    for line in result.stdout.splitlines():
        match = RULE_FLAGS.search(line)
        if match and int(match.group(1), 16) & RECOVERY_FLAG:
            hits.append(line)
    print(f"category={CATEGORY} recovery_hits={len(hits)}")
    for line in hits:
        print(line)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
