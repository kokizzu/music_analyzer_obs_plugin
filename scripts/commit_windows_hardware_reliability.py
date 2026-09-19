#!/usr/bin/env python3
"""Plan or commit only the Windows hardware reliability change set."""

from __future__ import annotations

import argparse
import difflib
import subprocess
from pathlib import Path


FILES = (
    "src/windows_hardware_control.cpp",
    "scripts/report_fret_zealot_sdk.py",
    "scripts/report_windows_deploy_source.py",
    "scripts/report_windows_hardware_source.py",
    "scripts/report_windows_source_range.py",
    "scripts/test_windows_hardware_retry_contract.py",
    "scripts/test_windows_hardware_status.py",
    "scripts/windows_hardware_checklist.py",
    "scripts/inspect_scoped_windows_hardware_diff.py",
    "scripts/commit_windows_hardware_reliability.py",
)

MAKEFILE_BLOCK = """.PHONY: report-windows-hardware-source
report-windows-hardware-source:
\tpython3 scripts/report_windows_hardware_source.py

.PHONY: report-fret-zealot-sdk
report-fret-zealot-sdk:
\tpython3 scripts/report_fret_zealot_sdk.py

.PHONY: report-windows-litejam-source
report-windows-litejam-source:
\tpython3 scripts/report_windows_source_range.py

.PHONY: test-windows-hardware-retry-contract
test-windows-hardware-retry-contract:
\tpython3 scripts/test_windows_hardware_retry_contract.py

.PHONY: report-windows-deploy-source
report-windows-deploy-source:
\tpython3 scripts/report_windows_deploy_source.py

.PHONY: inspect-scoped-windows-hardware-diff
inspect-scoped-windows-hardware-diff:
\tpython3 scripts/inspect_scoped_windows_hardware_diff.py

.PHONY: verify-windows-hardware-checklist
verify-windows-hardware-checklist: test-windows-hardware-retry-contract test-windows-hardware-reconnect test-windows-hardware-status test-windows-hardware-status-runtime test-windows-diagnostic-output test-windows-midi-protocol verify-windows-standalone verify-windows-runtime-bundle
\tpython3 scripts/windows_hardware_checklist.py

.PHONY: plan-commit-windows-hardware-reliability commit-windows-hardware-reliability
plan-commit-windows-hardware-reliability:
\tpython3 scripts/commit_windows_hardware_reliability.py plan

commit-windows-hardware-reliability:
\tpython3 scripts/commit_windows_hardware_reliability.py apply
"""


def run(arguments: list[str], *, input_text: str | None = None) -> None:
    result = subprocess.run(arguments, check=False, text=True, input=input_text)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def staged_makefile_patch() -> str:
    head = subprocess.check_output(["git", "show", "HEAD:windows.mk"], text=True)
    anchor = "report-windows-share-inventory:\n\tpython3 scripts/report_windows_share_inventory.py\n"
    if anchor not in head:
        raise SystemExit("windows.mk anchor is missing from HEAD")
    desired = head.replace(anchor, anchor + "\n" + MAKEFILE_BLOCK, 1)
    patch = "".join(
        difflib.unified_diff(
            head.splitlines(keepends=True),
            desired.splitlines(keepends=True),
            fromfile="a/windows.mk",
            tofile="b/windows.mk",
        )
    )
    return patch


def plan() -> None:
    print("Windows hardware reliability files:")
    for path in (*FILES, "windows.mk"):
        print(f"  {path}")
    run(["git", "status", "--short", "--", *FILES, "windows.mk"])
    run(["git", "diff", "--stat", "--", *FILES, "windows.mk"])


def apply() -> None:
    run(["git", "apply", "--cached", "--whitespace=nowarn"], input_text=staged_makefile_patch())
    run(["git", "add", "--", *FILES])
    run(["git", "diff", "--cached", "--check"])
    run(["git", "commit", "-m", "Harden Windows hardware reconnect diagnostics"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    args = parser.parse_args()
    if args.mode == "plan":
        plan()
    else:
        apply()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
