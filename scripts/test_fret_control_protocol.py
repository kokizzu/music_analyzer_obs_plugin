#!/usr/bin/env python3
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="music-analyzer-fret-control-") as directory:
        binary = pathlib.Path(directory) / "fret_control_protocol"
        subprocess.run(
            [
                "c++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-I.",
                "src/fret_control.cpp",
                "tests/fret_control_protocol.cpp",
                "-o",
                str(binary),
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run([str(binary)], cwd=ROOT, check=True)
    print("fret control protocol test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
