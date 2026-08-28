#!/usr/bin/env python3
"""Report the MIR-1K fixture importer process and current archive size."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "build/mir1k_vocal_fixtures/MIR-1K.rar"
PARTIAL = ROOT / "build/mir1k_vocal_fixtures/MIR-1K.rar.partial"


def main() -> int:
    result = subprocess.run(["ps", "-eo", "pid=,args="], check=True, text=True,
                            capture_output=True)
    matches = [line.strip() for line in result.stdout.splitlines()
               if "import_mir1k_vocal_archive.py" in line]
    print("\n".join(matches) if matches else "no active MIR-1K importer")
    print(f"archive bytes: {ARCHIVE.stat().st_size if ARCHIVE.is_file() else 0}")
    print(f"partial bytes: {PARTIAL.stat().st_size if PARTIAL.is_file() else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
