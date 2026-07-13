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


def main():
    test_explicit_musicnet_root_is_configured()
    test_generic_dataset_root_without_musicnet_layout_is_not_musicnet()
    test_generic_dataset_root_with_musicnet_layout_is_musicnet()
    test_explicit_medleydb_root_is_configured()
    test_generic_dataset_root_with_medleydb_child_is_medleydb()
    test_generic_dataset_root_without_medleydb_child_is_not_medleydb()
    print("test_run_real_goal_gate: 6 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
