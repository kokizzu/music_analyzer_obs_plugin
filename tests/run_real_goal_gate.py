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


def configured_musdb(env):
    if env_has_any(env, ("MUSIC_ANALYZER_MUSDB_ROOT", "MUSDB_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("MUSDB18-HQ", "musdb18-hq", "musdb18hq", "MUSDB18", "musdb18"):
        candidate = child_path(dataset_root, child)
        if is_dir(candidate):
            return True
    return False


def configured_slakh(env):
    if env_has_any(env, ("MUSIC_ANALYZER_SLAKH_ROOT", "SLAKH_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("Slakh2100_flac_redux", "slakh2100_flac_redux", "Slakh2100", "slakh2100", "Slakh", "slakh"):
        candidate = child_path(dataset_root, child)
        if is_dir(candidate):
            return True
    return False


def configured_choralsynth(env):
    if env_has_any(env, ("MUSIC_ANALYZER_CHORALSYNTH_ROOT", "CHORALSYNTH_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("ChoralSynth", "choralsynth", "MTG-ChoralSynth", "ChoralSynth-main", "ChoralSynth-master"):
        candidate = child_path(dataset_root, child)
        if is_dir(candidate):
            return True
    return False


def configured_cocochorales(env):
    if env_has_any(env, ("MUSIC_ANALYZER_COCOCHORALES_ROOT", "COCOCHORALES_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("CocoChorales", "cocochorales", "CocoChorales-v1", "coco_chorales", "ceg-cocochorales"):
        candidate = child_path(dataset_root, child)
        if is_dir(candidate):
            return True
    return False


def configured_polyvocal(env):
    if env_has_any(env, ("MUSIC_ANALYZER_POLYVOCAL_ROOT", "POLYVOCAL_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in (
        "polyvocal",
        "PolyVocal",
        "vocal_ensemble_f0",
        "vocal-ensemble-f0",
        "multif0-estimation-vocals-data",
        "multif0-estimation-vocals",
    ):
        candidate = child_path(dataset_root, child)
        if is_dir(candidate):
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


def configured_guitarset(env):
    if env_has_any(env, ("MUSIC_ANALYZER_GUITARSET_ROOT", "GUITARSET_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("GuitarSet", "guitarset", "GuitarSet-1.1.0", "guitarset-1.1.0"):
        if is_dir(child_path(dataset_root, child)):
            return True
    return False


def configured_maestro(env):
    if env_has_any(env, ("MUSIC_ANALYZER_MAESTRO_ROOT", "MAESTRO_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("maestro-v3.0.0", "maestro-v2.0.0", "MAESTRO", "maestro"):
        candidate = child_path(dataset_root, child)
        if is_dir(candidate):
            return True
    return False


def configured_egmd(env):
    if env_has_any(env, ("MUSIC_ANALYZER_EGMD_ROOT", "EGMD_PATH")):
        return True

    dataset_root = env.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return False

    for child in ("e-gmd-v1.0.0", "e-gmd", "EGMD", "E-GMD"):
        if is_dir(child_path(dataset_root, child)):
            return True
    return False


TARGET_PLANS = {
    "20": {
        "inspect_only": False,
        "multitrack_target": "test-real-multitrack-20",
        "musicnet_target": "test-real-musicnet-20",
        "medleydb_target": "test-real-medleydb-20",
        "musdb_target": "inspect-real-musdb",
        "slakh_target": "test-real-slakh-20",
        "choralsynth_target": "test-real-choralsynth-20",
        "cocochorales_target": "test-real-cocochorales-20",
        "polyvocal_target": "test-real-polyvocal-20",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "test-real-multtipop-20",
        "spheres_target": "inspect-real-spheres",
        "guitarset_target": "test-real-guitarset-20",
        "maestro_target": "test-real-maestro-20",
        "egmd_target": "test-real-egmd-20",
    },
    "full": {
        "inspect_only": False,
        "multitrack_target": "test-real-multitrack-full",
        "musicnet_target": "test-real-musicnet-full",
        "medleydb_target": "test-real-medleydb-20",
        "musdb_target": "inspect-real-musdb",
        "slakh_target": "test-real-slakh-full",
        "choralsynth_target": "test-real-choralsynth-20",
        "cocochorales_target": "test-real-cocochorales-20",
        "polyvocal_target": "test-real-polyvocal-20",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "test-real-multtipop-full",
        "spheres_target": "inspect-real-spheres",
        "guitarset_target": "test-real-guitarset-full",
        "maestro_target": "test-real-maestro-full",
        "egmd_target": "test-real-egmd-full",
    },
    "inspect-20": {
        "inspect_only": True,
        "multitrack_target": "inspect-real-multitrack-20",
        "musicnet_target": "inspect-real-musicnet",
        "medleydb_target": "inspect-real-medleydb",
        "musdb_target": "inspect-real-musdb",
        "slakh_target": "inspect-real-slakh",
        "choralsynth_target": "inspect-real-choralsynth",
        "cocochorales_target": "inspect-real-cocochorales",
        "polyvocal_target": "inspect-real-polyvocal",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "inspect-real-multtipop",
        "spheres_target": "inspect-real-spheres",
        "guitarset_target": "inspect-real-guitarset",
        "maestro_target": "inspect-real-maestro",
        "egmd_target": "inspect-real-egmd",
    },
    "inspect-full": {
        "inspect_only": True,
        "multitrack_target": "inspect-real-multitrack-full",
        "musicnet_target": "inspect-real-musicnet-full",
        "medleydb_target": "inspect-real-medleydb",
        "musdb_target": "inspect-real-musdb",
        "slakh_target": "inspect-real-slakh",
        "choralsynth_target": "inspect-real-choralsynth",
        "cocochorales_target": "inspect-real-cocochorales",
        "polyvocal_target": "inspect-real-polyvocal",
        "multtipop_target": "inspect-real-multtipop",
        "multtipop_audio_target": "inspect-real-multtipop",
        "spheres_target": "inspect-real-spheres",
        "guitarset_target": "inspect-real-guitarset",
        "maestro_target": "inspect-real-maestro",
        "egmd_target": "inspect-real-egmd",
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
            "run_real_goal_gate: skipping optional MedleyDB summed-stem melody-F0 analyzer gate; set "
            "MUSIC_ANALYZER_MEDLEYDB_ROOT/MEDLEYDB_PATH or place a MedleyDB directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_musdb(env):
        failed = run(make_cmd, plan["musdb_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MUSDB18 stem preflight; set "
            "MUSIC_ANALYZER_MUSDB_ROOT/MUSDB_PATH or place a MUSDB18/MUSDB18-HQ directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_slakh(env):
        failed = run(make_cmd, plan["slakh_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional Slakh2100 rendered multitrack analyzer gate; set "
            "MUSIC_ANALYZER_SLAKH_ROOT/SLAKH_PATH or place a Slakh2100 directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_choralsynth(env):
        failed = run(make_cmd, plan["choralsynth_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional ChoralSynth vocal multitrack analyzer gate; set "
            "MUSIC_ANALYZER_CHORALSYNTH_ROOT/CHORALSYNTH_PATH or place a ChoralSynth directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_cocochorales(env):
        failed = run(make_cmd, plan["cocochorales_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional CocoChorales chamber-ensemble analyzer gate; set "
            "MUSIC_ANALYZER_COCOCHORALES_ROOT/COCOCHORALES_PATH or place a CocoChorales directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_polyvocal(env):
        failed = run(make_cmd, plan["polyvocal_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional vocal-ensemble F0 analyzer gate; set "
            "MUSIC_ANALYZER_POLYVOCAL_ROOT/POLYVOCAL_PATH or place a polyvocal directory under "
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

    if configured_guitarset(env):
        failed = run(make_cmd, plan["guitarset_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional GuitarSet guitar/fretboard preflight; set "
            "MUSIC_ANALYZER_GUITARSET_ROOT/GUITARSET_PATH or place a GuitarSet directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_maestro(env):
        failed = run(make_cmd, plan["maestro_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional MAESTRO piano analyzer gate; set "
            "MUSIC_ANALYZER_MAESTRO_ROOT/MAESTRO_PATH or place a MAESTRO directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if configured_egmd(env):
        failed = run(make_cmd, plan["egmd_target"])
        if failed:
            return failed
    else:
        print(
            "run_real_goal_gate: skipping optional E-GMD drum analyzer gate; set "
            "MUSIC_ANALYZER_EGMD_ROOT/EGMD_PATH or place an E-GMD directory under "
            "MUSIC_ANALYZER_DATASET_ROOT"
        )

    if plan["inspect_only"]:
        print("run_real_goal_gate: passed required URMP multitrack preflight and all configured optional preflights")
    else:
        print("run_real_goal_gate: passed required URMP multitrack gate and all configured optional gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
