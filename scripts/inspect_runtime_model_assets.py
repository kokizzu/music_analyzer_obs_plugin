#!/usr/bin/env python3
"""Inspect checked-in model/runtime hooks relevant to real-time vocal separation."""

from __future__ import annotations

import pathlib


PATHS = (pathlib.Path("CMakeLists.txt"), pathlib.Path("src"), pathlib.Path("android/app/src/main/cpp"))
TERMS = ("onnx", "basic_pitch", "vocal", "separation", "tflite")


def main() -> int:
    for root in PATHS:
        files = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".cpp", ".hpp", ".txt"} and path.name != "CMakeLists.txt":
                continue
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            hits = [term for term in TERMS if term in text]
            if hits:
                print(f"{path}: {', '.join(hits)}")
    print("model files:")
    for path in sorted(pathlib.Path(".").rglob("*.onnx")):
        print(f"{path} bytes={path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
