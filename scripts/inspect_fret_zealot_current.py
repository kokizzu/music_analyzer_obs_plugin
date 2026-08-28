#!/usr/bin/env python3
"""Print the Fret Zealot transport methods needed for a focused review."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/FretZealotSdkController.java",
    ROOT / "android/app/src/main/java/dev/benalu/musicanalyzer/ExternalDeviceManager.java",
    ROOT / "tests/check_android_project.py",
    ROOT / "android/fz-android-sdk/src/main/java/com/fz/blelib/LEDBLELib.java",
)
RANGES = {
    "FretZealotSdkController.java": ((1, 110), (110, 430)),
    "ExternalDeviceManager.java": ((820, 865),),
    "check_android_project.py": ((260, 440),),
    "LEDBLELib.java": ((1, 560),),
}


def main() -> None:
    for path in FILES:
        print(f"--- {path.relative_to(ROOT)}")
        lines = path.read_text(encoding="utf-8").splitlines()
        for first, last in RANGES[path.name]:
            print(f"[{first}-{last}]")
            for line_number in range(first, min(last, len(lines)) + 1):
                print(f"{line_number}: {lines[line_number - 1]}")


if __name__ == "__main__":
    main()
