#!/usr/bin/env python3
"""Inspect the SMB artifact named by the Windows deployment investigation."""

from pathlib import Path
import hashlib


path = Path("/media/kyz/aigenshared/.__smbfile_silly1")
if not path.exists():
    print(f"missing={path}")
    raise SystemExit(0)

stat = path.stat()
print(f"path={path}")
print(f"bytes={stat.st_size}")
print(f"mode={oct(stat.st_mode)}")
print(f"mtime={stat.st_mtime}")
if path.is_file():
    data = path.read_bytes()
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    data = data[:256]
    print(f"prefix_hex={data.hex()}")
    print(f"prefix_text={data.decode('utf-8', errors='replace')}")
else:
    print("kind=not-regular-file")
