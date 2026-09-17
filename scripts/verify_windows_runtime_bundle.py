#!/usr/bin/env python3
"""Verify the files and imported DLLs in the portable Windows bundle."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTABLE = ROOT / "build/windows-x64/portable"
SYSTEM_DLLS = {
    "advapi32.dll",
    "bluetoothapis.dll",
    "gdi32.dll",
    "imm32.dll",
    "kernel32.dll",
    "msvcrt.dll",
    "ntdll.dll",
    "ole32.dll",
    "oleaut32.dll",
    "psapi.dll",
    "rpcrt4.dll",
    "sechost.dll",
    "setupapi.dll",
    "shell32.dll",
    "user32.dll",
    "version.dll",
    "winmm.dll",
    "ws2_32.dll",
}


def main() -> int:
    verification_path = PORTABLE / "verification.json"
    if not PORTABLE.is_dir() or not verification_path.is_file():
        raise SystemExit("Windows portable bundle is missing; run make package-windows-standalone")

    evidence = json.loads(verification_path.read_text(encoding="utf-8"))
    missing = []
    imported = set()
    for binary_name in ("MusicAnalyzer.exe", "HalfMusicAnalyzer.exe", "SDL2.dll"):
        binary = PORTABLE / binary_name
        if not binary.is_file():
            missing.append(binary_name)
        for name in evidence.get(binary_name, {}).get("imports", []):
            imported.add(name.lower())

    for name in sorted(imported):
        if name not in SYSTEM_DLLS and not (PORTABLE / name).exists():
            matching = [path for path in PORTABLE.glob("*.dll") if path.name.lower() == name]
            if not matching:
                missing.append(name)

    if not (PORTABLE / "SDL2.dll").is_file():
        missing.append("SDL2.dll")
    if missing:
        raise SystemExit("Missing Windows bundle files: " + ", ".join(sorted(set(missing))))

    bundled_dlls = sorted(path.name for path in PORTABLE.glob("*.dll"))
    print("Windows portable bundle: ok")
    print("Executables: MusicAnalyzer.exe, HalfMusicAnalyzer.exe")
    print("Bundled DLLs: " + (", ".join(bundled_dlls) if bundled_dlls else "none"))
    print("System DLL imports: " + (", ".join(sorted(imported & SYSTEM_DLLS)) if imported & SYSTEM_DLLS else "none"))
    print("Non-system imports: " + (", ".join(sorted(imported - SYSTEM_DLLS)) if imported - SYSTEM_DLLS else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
