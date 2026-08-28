#!/usr/bin/env python3
"""Run independent drum regression Make targets concurrently with retained logs."""

from pathlib import Path
import subprocess
import sys


TARGETS = (
    "test-drum-samples-spread",
    "test-mdb-drums-samples-parallel",
    "test-star-drums-samples-parallel",
)


def main() -> None:
    build = Path("build")
    build.mkdir(exist_ok=True)
    processes = []
    for target in TARGETS:
        path = build / f"{target}.log"
        stream = path.open("w", encoding="utf-8")
        process = subprocess.Popen(["make", target], stdout=stream, stderr=subprocess.STDOUT, text=True)
        processes.append((target, path, stream, process))

    failed = []
    for target, path, stream, process in processes:
        code = process.wait()
        stream.close()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        summary = next((line for line in reversed(lines) if "analyzer_" in line or "error:" in line.lower()), "no summary")
        print(f"{target}: exit={code} {summary}")
        if code:
            failed.append(target)
    if failed:
        raise SystemExit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
