#!/usr/bin/env python3
"""Plan or stop only the newer duplicate analyzer-cases runner."""

from pathlib import Path
from signal import SIGTERM
from os import kill
import sys


PLAN = Path("build/analyzer_cases_duplicate_stop_plan.tsv")


def processes() -> dict[int, tuple[int, str]]:
    found: dict[int, tuple[int, str]] = {}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace"
            ).strip()
            stat = (proc / "stat").read_text(encoding="utf-8", errors="replace").split()
        except OSError:
            continue
        if command == "build/analyzer_cases":
            found[int(proc.name)] = (int(stat[3]), command)
    return found


def plan() -> int:
    runners = processes()
    if len(runners) < 2:
        print("No duplicate analyzer-case runner to stop.")
        PLAN.unlink(missing_ok=True)
        return 0
    child_pid = max(runners)
    parent_pid = runners[child_pid][0]
    parent_command = ""
    try:
        parent_command = (Path("/proc") / str(parent_pid) / "cmdline").read_bytes().replace(
            b"\0", b" "
        ).decode("utf-8", "replace").strip()
    except OSError:
        pass
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(
        "pid\trole\tcommand\n"
        f"{child_pid}\tnewer-runner\t{runners[child_pid][1]}\n"
        f"{parent_pid}\tnewer-wrapper\t{parent_command}\n",
        encoding="utf-8",
    )
    print(PLAN.read_text(encoding="utf-8"), end="")
    return 0


def apply() -> int:
    if not PLAN.exists():
        raise SystemExit("No reviewed duplicate-stop plan exists. Run the plan target first.")
    rows = PLAN.read_text(encoding="utf-8").splitlines()[1:]
    for row in rows:
        pid_text, role, command = row.split("\t", 2)
        if role == "newer-runner" and command != "build/analyzer_cases":
            raise SystemExit("Refusing a plan whose runner is not analyzer_cases.")
        pid = int(pid_text)
        try:
            kill(pid, SIGTERM)
            print(f"Sent SIGTERM to {role} pid {pid}.")
        except ProcessLookupError:
            print(f"{role} pid {pid} has already exited.")
    return 0


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        raise SystemExit("usage: manage_duplicate_analyzer_cases.py plan|apply")
    raise SystemExit(plan() if sys.argv[1] == "plan" else apply())


if __name__ == "__main__":
    main()
