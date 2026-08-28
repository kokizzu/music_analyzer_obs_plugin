#!/usr/bin/env python3
"""Report running HF drum test processes and completed shard summaries."""

from pathlib import Path
import subprocess


def main() -> None:
    process = subprocess.run(
        ["ps", "-eo", "pid=,stat=,args="], check=True, text=True, capture_output=True
    )
    running = [line for line in process.stdout.splitlines() if "analyzer_hf_drum_kit" in line]
    print(f"running={len(running)}")
    for line in running:
        print(line)

    for category in ("kick", "snare", "hihat", "crash", "tom", "ride", "rim"):
        path = Path(f"build/hf_drum_kit_samples_shard_{category}.out")
        if not path.exists():
            print(f"{category}: pending")
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        summary = next((line for line in reversed(lines) if "analyzer_drum_samples:" in line), "no summary")
        print(f"{category}: {summary}")


if __name__ == "__main__":
    main()
