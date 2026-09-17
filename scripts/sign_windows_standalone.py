#!/usr/bin/env python3
"""Sign the Windows standalone executables with a real Authenticode certificate."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTABLE = ROOT / "build" / "windows-x64" / "portable"
EXECUTABLES = (PORTABLE / "MusicAnalyzer.exe", PORTABLE / "HalfMusicAnalyzer.exe")


def configured_path(*names: str) -> Path | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return Path(value).expanduser().resolve()
    return None


def sign_tool() -> str | None:
    requested = os.environ.get("WINDOWS_SIGN_TOOL")
    return requested or shutil.which("osslsigncode") or shutil.which("signtool")


def command_preview(tool: str, certificate: Path, timestamp: str | None) -> list[str]:
    command = [tool, "sign", "-pkcs12", str(certificate), "-h", "sha256"]
    if timestamp:
        command += ["-t", timestamp]
    command += ["-in", "<input.exe>", "-out", "<temporary.exe>"]
    return command


def check_inputs() -> tuple[str, Path, str, str | None]:
    tool = sign_tool()
    if not tool:
        raise RuntimeError("no signing tool found; install osslsigncode or configure WINDOWS_SIGN_TOOL")
    certificate = configured_path("WINDOWS_SIGN_PFX", "WINDOWS_SIGN_CERT")
    if not certificate:
        raise RuntimeError("set WINDOWS_SIGN_PFX to a PKCS#12 certificate for Smart App Control compatible signing")
    if not certificate.is_file():
        raise RuntimeError(f"signing certificate does not exist: {certificate}")
    password = os.environ.get("WINDOWS_SIGN_PASSWORD", "")
    timestamp = os.environ.get("WINDOWS_SIGN_TIMESTAMP_URL")
    missing = [str(path) for path in EXECUTABLES if not path.is_file()]
    if missing:
        raise RuntimeError("missing Windows executable(s): " + ", ".join(missing))
    return tool, certificate, password, timestamp


def plan() -> int:
    print(f"portable directory: {PORTABLE}")
    print("executables:")
    for path in EXECUTABLES:
        print(f"  {path}")
    tool = sign_tool() or "(missing signing tool)"
    certificate = configured_path("WINDOWS_SIGN_PFX", "WINDOWS_SIGN_CERT")
    print(f"signing tool: {tool}")
    print(f"certificate: {certificate or '(unset; no files will be changed)'}")
    print(f"timestamp URL: {os.environ.get('WINDOWS_SIGN_TIMESTAMP_URL') or '(unset)'}")
    if tool != "(missing signing tool)" and certificate:
        print("command shape: " + " ".join(command_preview(tool, certificate, os.environ.get("WINDOWS_SIGN_TIMESTAMP_URL"))))
    return 0


def apply() -> int:
    tool, certificate, password, timestamp = check_inputs()
    for executable in EXECUTABLES:
        with tempfile.TemporaryDirectory(prefix="music-analyzer-sign-") as directory:
            output = Path(directory) / executable.name
            command = [tool, "sign", "-pkcs12", str(certificate), "-pass", password, "-h", "sha256"]
            if timestamp:
                command += ["-t", timestamp]
            command += ["-in", str(executable), "-out", str(output)]
            print(f"Signing {executable.name} with {Path(tool).name}")
            subprocess.run(command, cwd=ROOT, check=True)
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError(f"signing produced no output for {executable}")
            output.replace(executable)
    print("Signed Windows executables. Verify the certificate chain on the target Windows installation.")
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        print("usage: sign_windows_standalone.py plan|apply", file=sys.stderr)
        return 2
    try:
        return plan() if sys.argv[1] == "plan" else apply()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"windows signing failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
