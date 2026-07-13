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


def multtipop_candidate_roots(env):
    roots = []
    if env_has_any(env, ("MUSIC_ANALYZER_MULTTIPOP_ROOT", "MULTTIPOP_PATH")):
        roots.extend(
            root for root in (env.get("MUSIC_ANALYZER_MULTTIPOP_ROOT"), env.get("MULTTIPOP_PATH")) if root
        )

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if dataset_root:
        roots.extend(
            [
                child_path(dataset_root, "MulTTiPop"),
                child_path(dataset_root, "multtipop"),
                child_path(dataset_root, "gclef-cmu-multtipop"),
                child_path(dataset_root, "gclef-cmu_multtipop"),
                child_path(dataset_root, "gclef-cmu", "multtipop"),
            ]
        )
    return roots


def has_multtipop_layout(root):
    return is_dir(child_path(root, "dev")) or is_dir(child_path(root, "test"))


def configured_multtipop(env):
    if env_has_any(env, ("MUSIC_ANALYZER_MULTTIPOP_ROOT", "MULTTIPOP_PATH")):
        return True

    for root in multtipop_candidate_roots(env):
        if has_multtipop_layout(root):
            return True
    return False


def multtipop_audio_configured(env):
    if env_has_any(env, ("MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO", "MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT")):
        return True

    for root in multtipop_candidate_roots(env):
        for split in ("dev", "test"):
            split_dir = child_path(root, split)
            if not is_dir(split_dir):
                continue
            try:
                segment_names = sorted(os.listdir(split_dir))[:8]
            except OSError:
                continue
            for segment_name in segment_names:
                segment_dir = child_path(split_dir, segment_name)
                if not is_dir(segment_dir):
                    continue
                for filename in ("audio.wav", "segment.wav", f"{segment_name}.wav"):
                    if os.path.isfile(child_path(segment_dir, filename)):
                        return True
    return False


def configured_spheres(env):
    if env_has_any(env, ("MUSIC_ANALYZER_SPHERES_ROOT", "SPHERES_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("TheSpheresDataset", "The_Spheres_Dataset", "Spheres", "spheres", "TheSpheres"):
        if is_dir(child_path(dataset_root, child)):
            return True
    return False


TARGET_PLANS = {
    "20": {
        "inspect_only": False,
        "multitrack_target": "test-real-multitrack-20",
        "musicnet_target": "test-real-musicnet-20",
        "medleydb_target": "inspect-real-medleydb",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "test-real-multtipop-20",
        "spheres_target": "inspect-real-spheres",
    },
    "full": {
        "inspect_only": False,
        "multitrack_target": "test-real-multitrack-full",
        "musicnet_target": "test-real-musicnet-full",
        "medleydb_target": "inspect-real-medleydb",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "test-real-multtipop-full",
        "spheres_target": "inspect-real-spheres",
    },
    "inspect-20": {
        "inspect_only": True,
        "multitrack_target": "inspect-real-multitrack-20",
        "musicnet_target": "inspect-real-musicnet",
        "medleydb_target": "inspect-real-medleydb",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "inspect-real-multtipop",
        "spheres_target": "inspect-real-spheres",
    },
    "inspect-full": {
        "inspect_only": True,
        "multitrack_target": "inspect-real-multitrack-full",
        "musicnet_target": "inspect-real-musicnet-full",
        "medleydb_target": "inspect-real-medleydb",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "inspect-real-multtipop",
        "spheres_target": "inspect-real-spheres",
    },
}


def resolve_plan(mode):
    plan = TARGET_PLANS.get(mode)
    return dict(plan) if plan else None


def run(make_cmd, target):
    print(f"run_real_goal_gate: running {make_cmd} {target}", flush=True)
    return subprocess.call([make_cmd, target])


def main(argv):
    if len(argv) != 3:
        print("usage: run_real_goal_gate.py 20|full|inspect-20|inspect-full MAKE", file=sys.stderr)
        return 2

    plan = resolve_plan(argv[1])
    if not plan:
        print("usage: run_real_goal_gate.py 20|full|inspect-20|inspect-full MAKE", file=sys.stderr)
        return 2

    make_cmd = argv[2]
    env = os.environ

    failed = run(make_cmd, plan["multitrack_target"])
    if failed:
        return failed

    if configured_musicnet(env):
        failed = run(make_cmd, plan["musicnet_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MusicNet real-mix gate; set "
            "MUSIC_ANALYZER_MUSICNET_ROOT/MUSICNET_PATH or place a MusicNet layout under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_medleydb(env):
        failed = run(make_cmd, plan["medleydb_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MedleyDB stem preflight; set "
            "MUSIC_ANALYZER_MEDLEYDB_ROOT/MEDLEYDB_PATH or place a MedleyDB directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_multtipop(env):
        target = plan["multtipop_audio_target"] if multtipop_audio_configured(env) else plan["multtipop_target"]
        failed = run(make_cmd, target)
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MulTTiPop multitrack-MIDI preflight; set "
            "MUSIC_ANALYZER_MULTTIPOP_ROOT/MULTTIPOP_PATH or place a MulTTiPop directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_spheres(env):
        failed = run(make_cmd, plan["spheres_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional Spheres stem preflight; set "
            "MUSIC_ANALYZER_SPHERES_ROOT/SPHERES_PATH or place a Spheres directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if plan["inspect_only"]:
        print("run_real_goal_gate: passed required URMP multitrack preflight and all configured optional preflights")
    else:
        print("run_real_goal_gate: passed required URMP multitrack gate and all configured optional gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
