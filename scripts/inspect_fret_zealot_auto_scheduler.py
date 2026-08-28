#!/usr/bin/env python3
"""Print the AUTO-root Fret Zealot scheduling and legacy-frame methods."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def print_region(path: Path, start_marker: str, end_marker: str | None = None) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if start_marker in line)
    end = (
        next(i for i in range(start + 1, len(lines)) if end_marker in lines[i])
        if end_marker
        else min(start + 360, len(lines))
    )
    print(f"=== {path.relative_to(ROOT)} ({start + 1}-{end})")
    for line_number, line in enumerate(lines[start:end], start + 1):
        print(f"{line_number:4}: {line}")


def main() -> None:
    manager = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java"
    controller = ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java"
    print_region(manager, "private void refreshFretZealotOutput", "private void retryFretZealotAutoRecovery")
    print()
    print_region(controller, "void sendPacket")


if __name__ == "__main__":
    main()
