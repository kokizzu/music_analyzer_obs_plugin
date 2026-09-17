#!/usr/bin/env python3
"""Push the current branch through the repository's Windows workflow target."""

import subprocess


def main() -> int:
    completed = subprocess.run(["git", "push"], check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
