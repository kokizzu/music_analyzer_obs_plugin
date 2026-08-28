#!/usr/bin/env python3
"""Report Basic Pitch compile guards and Android-relevant runtime dependencies."""

from __future__ import annotations

from pathlib import Path


SOURCES = (
    Path("src/basic_pitch_onnx_runtime.cpp"),
    Path("src/basic_pitch_onnx_worker.cpp"),
    Path("src/analyzer.cpp"),
)
TERMS = ("#if", "#ifdef", "#ifndef", "ONNX", "BasicPitchOnnxWorker", "__ANDROID__")


def main() -> int:
    for source in SOURCES:
        print(f"[{source}]")
        lines = source.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if any(term in line for term in TERMS):
                print(f"{index + 1}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
