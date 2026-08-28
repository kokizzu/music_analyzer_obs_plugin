#!/usr/bin/env python3
"""List prepared real-audio manifests and detector attribute tables in build/."""

from pathlib import Path


def main() -> None:
    root = Path("build")
    manifests = sorted(root.glob("**/manifest.tsv"))
    attributes = sorted(root.glob("**/*attribute*.tsv"))
    print(f"manifests={len(manifests)}")
    for path in manifests[:120]:
        print(f"manifest\t{path}")
    print(f"attributes={len(attributes)}")
    for path in attributes[:160]:
        print(f"attribute\t{path}")


if __name__ == "__main__":
    main()
