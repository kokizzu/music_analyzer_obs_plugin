#!/usr/bin/env python3
import os
import subprocess
import sys


def env_has_any(env, names):
    return any(env.get(name, "") for name in names)


def is_dir(path):
    return bool(path) and os.path.isdir(path)


def child_path(parent, *children):
    return os.path.join(parent, *children)


def has_musicnet_layout(root):
    return is_dir(child_path(root, "train_data")) or is_dir(child_path(root, "test_data"))


def configured_musicnet(env):
    if env_has_any(env, ("MUSIC_ANALYZER_MUSICNET_ROOT", "MUSICNET_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    candidates = (
        dataset_root,
        child_path(dataset_root, "MusicNet"),
        child_path(dataset_root, "musicnet"),
        child_path(dataset_root, "MusicNet", "musicnet"),
        child_path(dataset_root, "musicnet", "musicnet"),
    )
    return any(has_musicnet_layout(candidate) for candidate in candidates)


def configured_medleydb(env):
    if env_has_any(
        env,
        (
            "MUSIC_ANALYZER_MEDLEYDB_ROOT",
            "MEDLEYDB_PATH",
            "MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT",
            "MEDLEYDB_ANNOTATIONS_PATH",
        ),
    ):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("MedleyDB", "medleydb", "MedleyDB_sample", "MedleyDB_2.0", "MedleyDB2"):
        if is_dir(child_path(dataset_root, child)):
            return True
    return False


def run(make_cmd, target):
    print(f"run_real_goal_gate: running {make_cmd} {target}", flush=True)
    return subprocess.call([make_cmd, target])


def main(argv):
    if len(argv) != 3 or argv[1] not in ("20", "full"):
        print("usage: run_real_goal_gate.py 20|full MAKE", file=sys.stderr)
        return 2

    mode = argv[1]
    make_cmd = argv[2]
    env = os.environ
    multitrack_target = "test-real-multitrack-full" if mode == "full" else "test-real-multitrack-20"
    musicnet_target = "test-real-musicnet-full" if mode == "full" else "test-real-musicnet-20"

    failed = run(make_cmd, multitrack_target)
    if failed:
        return failed

    if configured_musicnet(env):
        failed = run(make_cmd, musicnet_target)
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MusicNet real-mix gate; set "
            "MUSIC_ANALYZER_MUSICNET_ROOT/MUSICNET_PATH or place a MusicNet layout under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_medleydb(env):
        failed = run(make_cmd, "inspect-real-medleydb")
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MedleyDB stem preflight; set "
            "MUSIC_ANALYZER_MEDLEYDB_ROOT/MEDLEYDB_PATH or place a MedleyDB directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    print("run_real_goal_gate: passed required URMP multitrack gate and all configured optional gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
