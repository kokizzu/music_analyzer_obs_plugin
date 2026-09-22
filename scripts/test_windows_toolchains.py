#!/usr/bin/env python3
import pathlib
import shutil
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run_optional_compiler(name: str) -> bool:
    compiler = shutil.which(name)
    if compiler is None:
        print(f"{name}: not installed; compile smoke skipped")
        return True

    with tempfile.TemporaryDirectory(prefix="music-analyzer-toolchain-") as directory:
        output = pathlib.Path(directory) / "windows_hardware_control.obj"
        command = [
            compiler,
            "/nologo",
            "/std:c++17",
            "/EHsc",
            "/D_WIN32",
            "/Isrc",
            "/c",
            "src/windows_hardware_control.cpp",
            f"/Fo{output}",
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            print(f"{name}: compile smoke failed")
            print(result.stdout)
            print(result.stderr)
            return False
        print(f"{name}: compile smoke passed")
    return True


def main() -> int:
    if not run_optional_compiler("clang-cl"):
        return 1
    if not run_optional_compiler("cl"):
        return 1
    print("Windows toolchain compatibility check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
