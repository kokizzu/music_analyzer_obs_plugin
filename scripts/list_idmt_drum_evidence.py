#!/usr/bin/env python3
"""List cached IDMT drum measurement and attribute outputs."""

from pathlib import Path


def main() -> None:
    paths = sorted(path for path in Path("build").glob("**/*idmt*") if path.is_file())
    print(f"files={len(paths)}")
    for path in paths[:300]:
        print(path)


if __name__ == "__main__":
    main()
