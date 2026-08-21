import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inspect_fsd50k_rim_metadata.py"
SPEC = importlib.util.spec_from_file_location("fsd50k_rim", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Fsd50kRimMetadataTest(unittest.TestCase):
    def write_labels(self, archive: zipfile.ZipFile, split: str, rows):
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=("fname", "labels"))
        writer.writeheader()
        writer.writerows(rows)
        archive.writestr(f"FSD50K.ground_truth/{split}.csv", out.getvalue())

    def test_requires_only_rimshot_ancestors_and_permissive_licence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            labels, metadata = root / "labels.zip", root / "metadata.zip"
            with zipfile.ZipFile(labels, "w") as archive:
                self.write_labels(archive, "dev", [
                    {"fname": "1", "labels": "Rimshot,Snare drum,Drum,Music"},
                    {"fname": "2", "labels": "Rimshot,Speech,Music"},
                ])
                self.write_labels(archive, "eval", [{"fname": "3", "labels": "Rimshot,Drum,Music"}])
                archive.writestr("FSD50K.ground_truth/vocabulary.csv", "index,label\n0,Rimshot\n")
            with zipfile.ZipFile(metadata, "w") as archive:
                archive.writestr("FSD50K.metadata/dev_clips_info_FSD50K.json", json.dumps({
                    "1": {"license": "CC BY 4.0"}, "2": {"license": "CC0"},
                }))
                archive.writestr("FSD50K.metadata/eval_clips_info_FSD50K.json", json.dumps({
                    "3": {"license": "CC BY-NC 3.0"},
                }))
            rendered = MODULE.render(labels, metadata)
        self.assertEqual(
            rendered,
            [
                "fsd50k_rim_metadata: rimshot_labelled_rows=3 pure_rimshot_candidates=2 permissive_cc_candidates=1 dev=1 eval=1",
                "fsd50k_rim_metadata: audio_requirement=FSD50K.eval_audio (6.2 GB) for any selected eval candidates; dev audio is 24.7 GB",
                "  vocabulary_rim_entry=0 Rimshot",
                "  labelled split=eval id=3 labels=Rimshot,Drum,Music",
                "  candidate split=eval id=3 permissive_cc=0 licence=CC BY-NC 3.0",
                "  labelled split=dev id=1 labels=Rimshot,Snare drum,Drum,Music",
                "  labelled split=dev id=2 labels=Rimshot,Speech,Music",
                "  candidate split=dev id=1 permissive_cc=1 licence=CC BY 4.0",
            ],
        )

    def test_does_not_mistake_marimba_for_rimshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            labels, metadata = root / "labels.zip", root / "metadata.zip"
            with zipfile.ZipFile(labels, "w") as archive:
                self.write_labels(archive, "dev", [{"fname": "1", "labels": "Marimba,Music"}])
                self.write_labels(archive, "eval", [])
                archive.writestr("FSD50K.ground_truth/vocabulary.csv", "index,label\n0,Marimba\n")
            with zipfile.ZipFile(metadata, "w") as archive:
                archive.writestr("FSD50K.metadata/dev_clips_info_FSD50K.json", json.dumps({"1": {}}))
                archive.writestr("FSD50K.metadata/eval_clips_info_FSD50K.json", json.dumps({}))
            rendered = MODULE.render(labels, metadata)
        self.assertEqual(
            rendered[:2],
            [
                "fsd50k_rim_metadata: rimshot_labelled_rows=0 pure_rimshot_candidates=0 permissive_cc_candidates=0 dev=0 eval=0",
                "fsd50k_rim_metadata: audio_requirement=FSD50K.eval_audio (6.2 GB) for any selected eval candidates; dev audio is 24.7 GB",
            ],
        )
        self.assertFalse(any("vocabulary_rim_entry" in line for line in rendered))


if __name__ == "__main__":
    unittest.main()
