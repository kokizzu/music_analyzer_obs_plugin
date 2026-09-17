#!/usr/bin/env python3
"""Report whether the Windows release has a signing path or signature."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTABLE = ROOT / "build" / "windows-x64" / "portable"


def tool(name: str) -> str:
    return shutil.which(name) or "(not installed)"


def main() -> int:
    print(f"portable directory: {PORTABLE}")
    print(f"osslsigncode: {tool('osslsigncode')}")
    print(f"signtool: {tool('signtool')}")
    for variable in (
        "WINDOWS_SIGN_CERT",
        "WINDOWS_SIGN_PASSWORD",
        "WINDOWS_SIGN_TIMESTAMP_URL",
    ):
        print(f"{variable}: {'set' if os.environ.get(variable) else 'unset'}")

    executables = sorted(PORTABLE.glob("*.exe"))
    if not executables:
        print("executables: none")
        return 0

    for executable in executables:
        print(f"\n{executable.name}:")
        file_tool = shutil.which("file")
        if file_tool:
            result = subprocess.run(
                [file_tool, str(executable)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            print(result.stdout.rstrip())
        verifier = shutil.which("osslsigncode")
        if verifier:
            result = subprocess.run(
                [verifier, "verify", "-in", str(executable)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            print(result.stdout.rstrip() or f"osslsigncode exit={result.returncode}")
        else:
            signtool = shutil.which("signtool")
            if signtool:
                result = subprocess.run(
                    [signtool, "verify", "/pa", "/v", str(executable)],
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                print(result.stdout.rstrip() or f"signtool exit={result.returncode}")
            else:
                print("signature check unavailable: install osslsigncode or use signtool on Windows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
