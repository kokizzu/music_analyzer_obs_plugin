#!/usr/bin/env python3
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="music-analyzer-worker-") as directory:
        binary = pathlib.Path(directory) / "windows_hardware_worker_runtime"
        subprocess.run(
            [
                "c++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-pthread",
                "-I.",
                "tests/windows_hardware_worker_runtime.cpp",
                "-o",
                str(binary),
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run([str(binary)], cwd=ROOT, check=True)
    print("Windows hardware worker runtime: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
