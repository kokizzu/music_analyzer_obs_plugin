#!/usr/bin/env python3
import os
import subprocess
import sys


def env_has_any(names):
    return any(os.environ.get(name, "") for name in names)


def run(make_cmd, target):
    print(f"run_real_goal_gate: running {make_cmd} {target}", flush=True)
    return subprocess.call([make_cmd, target])


def main(argv):
    if len(argv) != 3 or argv[1] not in ("20", "full"):
        print("usage: run_real_goal_gate.py 20|full MAKE", file=sys.stderr)
        return 2

    mode = argv[1]
    make_cmd = argv[2]
    multitrack_target = "test-real-multitrack-full" if mode == "full" else "test-real-multitrack-20"
    musicnet_target = "test-real-musicnet-full" if mode == "full" else "test-real-musicnet-20"

    failed = run(make_cmd, multitrack_target)
    if failed:
        return failed

    if env_has_any(("MUSIC_ANALYZER_MUSICNET_ROOT", "MUSICNET_PATH", "MUSIC_ANALYZER_DATASET_ROOT")):
        failed = run(make_cmd, musicnet_target)
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MusicNet real-mix gate; set "
            "MUSIC_ANALYZER_MUSICNET_ROOT, MUSICNET_PATH, or MUSIC_ANALYZER_DATASET_ROOT"
        )

    if env_has_any(
        (
            "MUSIC_ANALYZER_MEDLEYDB_ROOT",
            "MEDLEYDB_PATH",
            "MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT",
            "MEDLEYDB_ANNOTATIONS_PATH",
        )
    ):
        failed = run(make_cmd, "inspect-real-medleydb")
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MedleyDB stem preflight; set "
            "MUSIC_ANALYZER_MEDLEYDB_ROOT or MEDLEYDB_PATH"
        )

    print("run_real_goal_gate: passed required URMP multitrack gate and all configured optional gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
