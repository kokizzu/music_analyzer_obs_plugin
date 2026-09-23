#!/usr/bin/env python3
from pathlib import Path


root = Path("build/windows-x64")
logs = sorted((path for path in root.rglob("*") if path.is_file() and path.suffix == ".log"),
              key=lambda path: path.stat().st_mtime, reverse=True)
if not logs:
    raise SystemExit(f"no Windows build log found below {root}")
path = logs[0]
lines = path.read_text(errors="replace").splitlines()
print(f"=== {path} (last 160 lines) ===")
for line in lines[-160:]:
    print(line)
