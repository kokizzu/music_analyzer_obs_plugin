#!/usr/bin/env python3
"""Test the timestamped zero-byte Windows deployment marker contract."""

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from deploy_windows_mounted import deployment_changelog, deployment_changelog_name, write_deployment_changelog


expected = "changelog-2026-09-17_214500.txt"
actual = deployment_changelog_name(datetime(2026, 9, 17, 21, 45))
if actual != expected:
    raise SystemExit(f"unexpected changelog name: {actual}")

content = deployment_changelog(datetime(2026, 9, 17, 21, 45))
for section in ("Latest 3 committed changes:", "Uncommitted changes:", "Staged diff summary:", "Unstaged diff summary:"):
    if section not in content:
        raise SystemExit(f"missing changelog section: {section}")

with TemporaryDirectory() as directory:
    changelog = write_deployment_changelog(Path(directory), datetime(2026, 9, 17, 21, 45))
    if changelog.name != expected or changelog.stat().st_size == 0:
        raise SystemExit("deployment changelog was not written")

print("Windows deployment changelog checks: ok")
