#!/usr/bin/env python3
import os
import tempfile

import run_real_goal_gate


def touch_dir(path):
    os.makedirs(path, exist_ok=True)


def test_explicit_musicnet_root_is_configured():
    assert run_real_goal_gate.configured_musicnet({"MUSIC_ANALYZER_MUSICNET_ROOT": "/tmp/musicnet"})
    assert run_real_goal_gate.configured_musicnet({"MUSICNET_PATH": "/tmp/musicnet"})


def test_generic_dataset_root_without_musicnet_layout_is_not_musicnet():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_musicnet({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_with_musicnet_layout_is_musicnet():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "musicnet", "train_data"))
        assert run_real_goal_gate.configured_musicnet({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_medleydb_root_is_configured():
    assert run_real_goal_gate.configured_medleydb({"MUSIC_ANALYZER_MEDLEYDB_ROOT": "/tmp/MedleyDB"})
    assert run_real_goal_gate.configured_medleydb({"MEDLEYDB_PATH": "/tmp/MedleyDB"})
    assert run_real_goal_gate.configured_medleydb(
        {"MUSIC_ANALYZER_MEDLEYDB_ANNOTATIONS_ROOT": "/tmp/Annotations"}
    )


def test_generic_dataset_root_with_medleydb_child_is_medleydb():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "MedleyDB"))
        assert run_real_goal_gate.configured_medleydb({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_medleydb_child_is_not_medleydb():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_medleydb({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_spheres_root_is_configured():
    assert run_real_goal_gate.configured_spheres({"MUSIC_ANALYZER_SPHERES_ROOT": "/tmp/Spheres"})
    assert run_real_goal_gate.configured_spheres({"SPHERES_PATH": "/tmp/Spheres"})


def test_generic_dataset_root_with_spheres_child_is_spheres():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "TheSpheresDataset"))
        assert run_real_goal_gate.configured_spheres({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_spheres_child_is_not_spheres():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_spheres({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_twenty_piece_test_plan_targets_real_gates():
    plan = run_real_goal_gate.resolve_plan("20")
    assert plan
    assert not plan["inspect_only"]
    assert plan["multitrack_target"] == "test-real-multitrack-20"
    assert plan["musicnet_target"] == "test-real-musicnet-20"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["spheres_target"] == "inspect-real-spheres"


def test_full_test_plan_targets_full_real_gates():
    plan = run_real_goal_gate.resolve_plan("full")
    assert plan
    assert not plan["inspect_only"]
    assert plan["multitrack_target"] == "test-real-multitrack-full"
    assert plan["musicnet_target"] == "test-real-musicnet-full"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["spheres_target"] == "inspect-real-spheres"


def test_twenty_piece_inspect_plan_targets_preflights():
    plan = run_real_goal_gate.resolve_plan("inspect-20")
    assert plan
    assert plan["inspect_only"]
    assert plan["multitrack_target"] == "inspect-real-multitrack-20"
    assert plan["musicnet_target"] == "inspect-real-musicnet"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["spheres_target"] == "inspect-real-spheres"


def test_full_inspect_plan_targets_full_preflights():
    plan = run_real_goal_gate.resolve_plan("inspect-full")
    assert plan
    assert plan["inspect_only"]
    assert plan["multitrack_target"] == "inspect-real-multitrack-full"
    assert plan["musicnet_target"] == "inspect-real-musicnet-full"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["spheres_target"] == "inspect-real-spheres"


def test_invalid_plan_is_rejected():
    assert run_real_goal_gate.resolve_plan("inspect") is None
    assert run_real_goal_gate.resolve_plan("quick") is None


def main():
    test_explicit_musicnet_root_is_configured()
    test_generic_dataset_root_without_musicnet_layout_is_not_musicnet()
    test_generic_dataset_root_with_musicnet_layout_is_musicnet()
    test_explicit_medleydb_root_is_configured()
    test_generic_dataset_root_with_medleydb_child_is_medleydb()
    test_generic_dataset_root_without_medleydb_child_is_not_medleydb()
    test_explicit_spheres_root_is_configured()
    test_generic_dataset_root_with_spheres_child_is_spheres()
    test_generic_dataset_root_without_spheres_child_is_not_spheres()
    test_twenty_piece_test_plan_targets_real_gates()
    test_full_test_plan_targets_full_real_gates()
    test_twenty_piece_inspect_plan_targets_preflights()
    test_full_inspect_plan_targets_full_preflights()
    test_invalid_plan_is_rejected()
    print("test_run_real_goal_gate: 14 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
