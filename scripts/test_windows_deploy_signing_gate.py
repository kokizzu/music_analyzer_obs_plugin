#!/usr/bin/env python3
"""Verify that Windows deployment cannot copy unsigned executables."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY = REPO_ROOT / "scripts" / "deploy_windows_mounted.py"


def function_body(source: str, name: str, next_name: str) -> str:
    start = source.index(f"def {name}(")
    end = source.index(f"def {next_name}(", start)
    return source[start:end]


def main() -> None:
    source = DEPLOY.read_text(encoding="utf-8")
    assert "def ensure_signed_source()" in source
    assert "sign_windows_standalone.py" in source
    assert '"apply"' in source

    copy_body = function_body(source, "copy_atomically", "smb_entry")
    assert copy_body.index("ensure_signed_source()") < copy_body.index("for source")

    smb_body = function_body(source, "smb_upload_atomically", "main")
    assert smb_body.index("ensure_signed_source()") < smb_body.index("entry = smb_entry()")

    print("Windows deployment signing gate: PASS")


if __name__ == "__main__":
    main()
