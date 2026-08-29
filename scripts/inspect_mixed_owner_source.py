#!/usr/bin/env python3
"""Print the generic full-mix ownership scorer and its candidate builders."""

from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source = root / "src" / "analyzer.cpp"
    lines = source.read_text(encoding="utf-8").splitlines()
    names = ("choose_full_mix_owner", "build_full_mix_ownership")
    for name in names:
        start = next(index for index, line in enumerate(lines) if f"{name}(" in line)
        print(f"--- {source}:{start + 1} {name} ---")
        for index, line in enumerate(lines[start:start + 480], start + 1):
            print(f"{index:6}  {line}")
            if index > start + 20 and line == "}":
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
