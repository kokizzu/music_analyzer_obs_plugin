#!/usr/bin/env python3
"""Print source around standalone self-test assertions."""

from pathlib import Path


lines = (Path(__file__).resolve().parents[1] / "src" / "standalone.cpp").read_text(encoding="utf-8").splitlines()
matches = [i for i, line in enumerate(lines) if "bad live source order" in line]
if not matches:
    raise SystemExit("self-test assertion not found")
start = max(0, matches[0] - 35)
end = min(len(lines), matches[0] + 20)
for number, line in enumerate(lines[start:end], start=start + 1):
    print(f"{number}: {line}")
