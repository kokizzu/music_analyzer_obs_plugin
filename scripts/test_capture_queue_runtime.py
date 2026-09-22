#!/usr/bin/env python3
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="music-analyzer-capture-queue-") as directory:
        binary = pathlib.Path(directory) / "capture_queue_runtime"
        subprocess.run(
            [
                "c++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I.",
                "tests/capture_queue_runtime.cpp",
                "-o",
                str(binary),
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run([str(binary)], cwd=ROOT, check=True)
    print("capture queue runtime test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
