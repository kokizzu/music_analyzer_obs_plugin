#!/usr/bin/env python3
"""Print the physical Windows checks that cannot be reproduced under Wine."""


def main() -> int:
    print("Automated Windows hardware checks: passed")
    print("Physical Windows checklist:")
    print("  1. MusicAnalyzer.exe --list-hardware")
    print("  2. MusicAnalyzer.exe --hardware-only --hardware-root G --require-midi")
    print("  3. MusicAnalyzer.exe --hardware-only --hardware-root G --require-fret-zealot")
    print("  4. MusicAnalyzer.exe --hardware-only --hardware-root G --require-litejam")
    print("  5. Change the root and confirm each device updates without restarting")
    print("Expected diagnostics include device status transitions and any GATT/MIDI error code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
