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


def test_explicit_musdb_root_is_configured():
    assert run_real_goal_gate.configured_musdb({"MUSIC_ANALYZER_MUSDB_ROOT": "/tmp/MUSDB18-HQ"})
    assert run_real_goal_gate.configured_musdb({"MUSDB_PATH": "/tmp/MUSDB18-HQ"})


def test_generic_dataset_root_with_musdb_child_is_musdb():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "MUSDB18-HQ"))
        assert run_real_goal_gate.configured_musdb({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_musdb_child_is_not_musdb():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_musdb({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_slakh_root_is_configured():
    assert run_real_goal_gate.configured_slakh({"MUSIC_ANALYZER_SLAKH_ROOT": "/tmp/Slakh2100"})
    assert run_real_goal_gate.configured_slakh({"SLAKH_PATH": "/tmp/Slakh2100"})


def test_generic_dataset_root_with_slakh_child_is_slakh():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "Slakh2100_flac_redux"))
        assert run_real_goal_gate.configured_slakh({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_slakh_child_is_not_slakh():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_slakh({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_choralsynth_root_is_configured():
    assert run_real_goal_gate.configured_choralsynth({"MUSIC_ANALYZER_CHORALSYNTH_ROOT": "/tmp/ChoralSynth"})
    assert run_real_goal_gate.configured_choralsynth({"CHORALSYNTH_PATH": "/tmp/ChoralSynth"})


def test_generic_dataset_root_with_choralsynth_child_is_choralsynth():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "ChoralSynth"))
        assert run_real_goal_gate.configured_choralsynth({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_choralsynth_child_is_not_choralsynth():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_choralsynth({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_polyvocal_root_is_configured():
    assert run_real_goal_gate.configured_polyvocal({"MUSIC_ANALYZER_POLYVOCAL_ROOT": "/tmp/polyvocal"})
    assert run_real_goal_gate.configured_polyvocal({"POLYVOCAL_PATH": "/tmp/polyvocal"})


def test_generic_dataset_root_with_polyvocal_child_is_polyvocal():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "vocal_ensemble_f0"))
        assert run_real_goal_gate.configured_polyvocal({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_polyvocal_child_is_not_polyvocal():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_polyvocal({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_multtipop_root_is_configured():
    assert run_real_goal_gate.configured_multtipop({"MUSIC_ANALYZER_MULTTIPOP_ROOT": "/tmp/multtipop"})
    assert run_real_goal_gate.configured_multtipop({"MULTTIPOP_PATH": "/tmp/multtipop"})


def test_generic_dataset_root_with_multtipop_child_is_multtipop():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "gclef-cmu", "multtipop", "dev"))
        assert run_real_goal_gate.configured_multtipop({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_multtipop_child_is_not_multtipop():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_multtipop({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_multtipop_audio_is_configured_by_env_or_local_wav():
    assert run_real_goal_gate.multtipop_audio_configured({"MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO": "1"})
    assert run_real_goal_gate.multtipop_audio_configured({"MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT": "/tmp/audio"})

    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "dev", "fixture001"))
        with open(os.path.join(temp, "dev", "fixture001", "audio.wav"), "wb") as audio_file:
            audio_file.write(b"")
        assert run_real_goal_gate.multtipop_audio_configured({"MUSIC_ANALYZER_MULTTIPOP_ROOT": temp})

    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "dev", "fixture001"))
        assert not run_real_goal_gate.multtipop_audio_configured({"MUSIC_ANALYZER_MULTTIPOP_ROOT": temp})


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


def test_explicit_guitarset_root_is_configured():
    assert run_real_goal_gate.configured_guitarset({"MUSIC_ANALYZER_GUITARSET_ROOT": "/tmp/GuitarSet"})
    assert run_real_goal_gate.configured_guitarset({"GUITARSET_PATH": "/tmp/GuitarSet"})


def test_generic_dataset_root_with_guitarset_child_is_guitarset():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "GuitarSet"))
        assert run_real_goal_gate.configured_guitarset({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_guitarset_child_is_not_guitarset():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_guitarset({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_maestro_root_is_configured():
    assert run_real_goal_gate.configured_maestro({"MUSIC_ANALYZER_MAESTRO_ROOT": "/tmp/MAESTRO"})
    assert run_real_goal_gate.configured_maestro({"MAESTRO_PATH": "/tmp/MAESTRO"})


def test_generic_dataset_root_with_maestro_child_is_maestro():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "maestro-v3.0.0"))
        assert run_real_goal_gate.configured_maestro({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_maestro_child_is_not_maestro():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_maestro({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_explicit_egmd_root_is_configured():
    assert run_real_goal_gate.configured_egmd({"MUSIC_ANALYZER_EGMD_ROOT": "/tmp/e-gmd"})
    assert run_real_goal_gate.configured_egmd({"EGMD_PATH": "/tmp/e-gmd"})


def test_generic_dataset_root_with_egmd_child_is_egmd():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "e-gmd-v1.0.0"))
        assert run_real_goal_gate.configured_egmd({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_generic_dataset_root_without_egmd_child_is_not_egmd():
    with tempfile.TemporaryDirectory() as temp:
        touch_dir(os.path.join(temp, "URMP", "01_Jupiter"))
        assert not run_real_goal_gate.configured_egmd({"MUSIC_ANALYZER_DATASET_ROOT": temp})


def test_twenty_piece_test_plan_targets_real_gates():
    plan = run_real_goal_gate.resolve_plan("20")
    assert plan
    assert not plan["inspect_only"]
    assert plan["multitrack_target"] == "test-real-multitrack-20"
    assert plan["musicnet_target"] == "test-real-musicnet-20"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["musdb_target"] == "inspect-real-musdb"
    assert plan["slakh_target"] == "test-real-slakh-20"
    assert plan["choralsynth_target"] == "test-real-choralsynth-20"
    assert plan["polyvocal_target"] == "test-real-polyvocal-20"
    assert plan["multtipop_target"] == "inspect-real-multtipop"
    assert plan["multtipop_audio_target"] == "test-real-multtipop-20"
    assert plan["spheres_target"] == "inspect-real-spheres"
    assert plan["guitarset_target"] == "test-real-guitarset-20"
    assert plan["maestro_target"] == "test-real-maestro-20"
    assert plan["egmd_target"] == "test-real-egmd-20"


def test_full_test_plan_targets_full_real_gates():
    plan = run_real_goal_gate.resolve_plan("full")
    assert plan
    assert not plan["inspect_only"]
    assert plan["multitrack_target"] == "test-real-multitrack-full"
    assert plan["musicnet_target"] == "test-real-musicnet-full"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["musdb_target"] == "inspect-real-musdb"
    assert plan["slakh_target"] == "test-real-slakh-full"
    assert plan["choralsynth_target"] == "test-real-choralsynth-20"
    assert plan["polyvocal_target"] == "test-real-polyvocal-20"
    assert plan["multtipop_target"] == "inspect-real-multtipop"
    assert plan["multtipop_audio_target"] == "test-real-multtipop-full"
    assert plan["spheres_target"] == "inspect-real-spheres"
    assert plan["guitarset_target"] == "test-real-guitarset-full"
    assert plan["maestro_target"] == "test-real-maestro-full"
    assert plan["egmd_target"] == "test-real-egmd-full"


def test_twenty_piece_inspect_plan_targets_preflights():
    plan = run_real_goal_gate.resolve_plan("inspect-20")
    assert plan
    assert plan["inspect_only"]
    assert plan["multitrack_target"] == "inspect-real-multitrack-20"
    assert plan["musicnet_target"] == "inspect-real-musicnet"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["musdb_target"] == "inspect-real-musdb"
    assert plan["slakh_target"] == "inspect-real-slakh"
    assert plan["choralsynth_target"] == "inspect-real-choralsynth"
    assert plan["polyvocal_target"] == "inspect-real-polyvocal"
    assert plan["multtipop_target"] == "inspect-real-multtipop"
    assert plan["multtipop_audio_target"] == "inspect-real-multtipop"
    assert plan["spheres_target"] == "inspect-real-spheres"
    assert plan["guitarset_target"] == "inspect-real-guitarset"
    assert plan["maestro_target"] == "inspect-real-maestro"
    assert plan["egmd_target"] == "inspect-real-egmd"


def test_full_inspect_plan_targets_full_preflights():
    plan = run_real_goal_gate.resolve_plan("inspect-full")
    assert plan
    assert plan["inspect_only"]
    assert plan["multitrack_target"] == "inspect-real-multitrack-full"
    assert plan["musicnet_target"] == "inspect-real-musicnet-full"
    assert plan["medleydb_target"] == "inspect-real-medleydb"
    assert plan["musdb_target"] == "inspect-real-musdb"
    assert plan["slakh_target"] == "inspect-real-slakh"
    assert plan["choralsynth_target"] == "inspect-real-choralsynth"
    assert plan["polyvocal_target"] == "inspect-real-polyvocal"
    assert plan["multtipop_target"] == "inspect-real-multtipop"
    assert plan["multtipop_audio_target"] == "inspect-real-multtipop"
    assert plan["spheres_target"] == "inspect-real-spheres"
    assert plan["guitarset_target"] == "inspect-real-guitarset"
    assert plan["maestro_target"] == "inspect-real-maestro"
    assert plan["egmd_target"] == "inspect-real-egmd"


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
    test_explicit_musdb_root_is_configured()
    test_generic_dataset_root_with_musdb_child_is_musdb()
    test_generic_dataset_root_without_musdb_child_is_not_musdb()
    test_explicit_slakh_root_is_configured()
    test_generic_dataset_root_with_slakh_child_is_slakh()
    test_generic_dataset_root_without_slakh_child_is_not_slakh()
    test_explicit_choralsynth_root_is_configured()
    test_generic_dataset_root_with_choralsynth_child_is_choralsynth()
    test_generic_dataset_root_without_choralsynth_child_is_not_choralsynth()
    test_explicit_polyvocal_root_is_configured()
    test_generic_dataset_root_with_polyvocal_child_is_polyvocal()
    test_generic_dataset_root_without_polyvocal_child_is_not_polyvocal()
    test_explicit_multtipop_root_is_configured()
    test_generic_dataset_root_with_multtipop_child_is_multtipop()
    test_generic_dataset_root_without_multtipop_child_is_not_multtipop()
    test_multtipop_audio_is_configured_by_env_or_local_wav()
    test_explicit_spheres_root_is_configured()
    test_generic_dataset_root_with_spheres_child_is_spheres()
    test_generic_dataset_root_without_spheres_child_is_not_spheres()
    test_explicit_guitarset_root_is_configured()
    test_generic_dataset_root_with_guitarset_child_is_guitarset()
    test_generic_dataset_root_without_guitarset_child_is_not_guitarset()
    test_explicit_maestro_root_is_configured()
    test_generic_dataset_root_with_maestro_child_is_maestro()
    test_generic_dataset_root_without_maestro_child_is_not_maestro()
    test_explicit_egmd_root_is_configured()
    test_generic_dataset_root_with_egmd_child_is_egmd()
    test_generic_dataset_root_without_egmd_child_is_not_egmd()
    test_twenty_piece_test_plan_targets_real_gates()
    test_full_test_plan_targets_full_real_gates()
    test_twenty_piece_inspect_plan_targets_preflights()
    test_full_inspect_plan_targets_full_preflights()
    test_invalid_plan_is_rejected()
    print("test_run_real_goal_gate: 39 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
