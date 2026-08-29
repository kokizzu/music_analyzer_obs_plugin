#!/usr/bin/env python3
"""Profile full-mix ownership evidence for every real-vocal audit miss."""

import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "build" / "real_note_vocal_audit.out"
DEBUG_SCRIPT = ROOT / "scripts" / "run_real_note_debug_sample.sh"
MISS = re.compile(r"^(\S+) vocals/.* expected-row ownership missing")
EXPECTED = re.compile(r"expected=([^ ]+)")
OWNERSHIP = re.compile(
    r"own=([^:]+):(\w+)/conf=([0-9.]+)/bkvo=([0-9.,-]+)/spec=([0-9.]+)/pitch=([0-9.]+)/"
    r"per=([0-9.]+)/harm=([0-9.]+)/fit=([0-9.]+)/cent=([0-9.]+)/slope=([0-9.]+)/noise=([0-9.]+)"
)


def misses() -> list[str]:
    if not AUDIT.is_file():
        raise SystemExit(f"missing audit: {AUDIT}; run make audit-real-note-vocals first")
    return [match.group(1) for line in AUDIT.read_text(encoding="utf-8").splitlines()
            if (match := MISS.match(line))]


def parse_candidates(output: str, expected: str) -> list[dict[str, object]]:
    candidates = []
    for line in output.splitlines():
        expected_match = EXPECTED.search(line)
        ownership_match = OWNERSHIP.search(line)
        if not expected_match or not ownership_match or expected_match.group(1) != expected:
            continue
        if ownership_match.group(1) != expected:
            continue
        scores = [float(value) for value in ownership_match.group(4).split(",")]
        candidates.append({
            "owner": ownership_match.group(2),
            "confidence": float(ownership_match.group(3)),
            "scores": scores,
            "spectral": float(ownership_match.group(5)),
            "pitch": float(ownership_match.group(6)),
            "periodicity": float(ownership_match.group(7)),
            "harmonicity": float(ownership_match.group(8)),
            "fit": float(ownership_match.group(9)),
            "centroid": float(ownership_match.group(10)),
            "slope": float(ownership_match.group(11)),
            "noise": float(ownership_match.group(12)),
        })
    return candidates


def main() -> int:
    rows = []
    for sample in misses():
        completed = subprocess.run(
            ["sh", str(DEBUG_SCRIPT), sample], cwd=ROOT, text=True, capture_output=True, check=True
        )
        expected_match = EXPECTED.search(completed.stdout)
        if not expected_match:
            raise SystemExit(f"{sample}: no expected pitch in debug output")
        candidates = parse_candidates(completed.stdout, expected_match.group(1))
        if candidates:
            best = max(candidates, key=lambda item: item["scores"][3])
            rows.append((sample, best))
        else:
            rows.append((sample, None))

    owner_counts = Counter("none" if item is None else item["owner"] for _, item in rows)
    direct_vocal = [item for _, item in rows if item is not None and item["scores"][3] > 0.0]
    print(f"misses={len(rows)} expected-candidate={len(rows) - owner_counts['none']} direct-vocal-score={len(direct_vocal)}")
    print("best-owner=" + " ".join(f"{name}:{count}" for name, count in sorted(owner_counts.items())))
    for sample, item in rows:
        if item is None:
            print(f"{sample} no-expected-candidate")
            continue
        scores = item["scores"]
        print(
            f"{sample} owner={item['owner']} conf={item['confidence']:.3f} "
            f"bkvo={scores[0]:.3f},{scores[1]:.3f},{scores[2]:.3f},{scores[3]:.3f},{scores[4]:.3f} "
            f"spec={item['spectral']:.3f} pitch={item['pitch']:.3f} per={item['periodicity']:.3f} "
            f"fit={item['fit']:.3f} cent={item['centroid']:.3f} slope={item['slope']:.3f} noise={item['noise']:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
