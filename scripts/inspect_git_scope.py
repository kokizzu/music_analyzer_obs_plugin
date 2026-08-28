#!/usr/bin/env python3
"""Report the exact repository changes relevant before a scoped commit."""

from subprocess import run


def git(*args: str) -> str:
    result = run(("git", *args), check=True, text=True, capture_output=True)
    return result.stdout.rstrip()


def main() -> None:
    print("## status")
    print(git("status", "--short"))
    print("## unstaged names")
    print(git("diff", "--name-only"))
    print("## staged names")
    print(git("diff", "--cached", "--name-only"))


if __name__ == "__main__":
    main()
