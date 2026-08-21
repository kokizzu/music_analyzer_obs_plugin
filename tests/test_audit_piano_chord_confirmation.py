import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_piano_chord_confirmation.py"
SPEC = importlib.util.spec_from_file_location("piano_chord_confirmation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PianoChordConfirmationAuditTest(unittest.TestCase):
    def write(self, path: Path, labels: list[str]):
        path.write_text(
            "recording\tanchor_sample\tframe\tkeyboard_chord\tchord_hit\n" +
            "\n".join(
                f"1\t1\t{frame}\t{label}\t{int(label == 'C')}"
                for frame, label in enumerate(labels)
            ) + "\n",
            encoding="utf-8",
        )

    def test_rejects_accuracy_gain_that_reintroduces_a_flicker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = [root / "baseline-a.tsv", root / "baseline-b.tsv"]
            trial = [root / "trial-a.tsv", root / "trial-b.tsv"]
            self.write(baseline[0], ["C", "C", "C"])
            self.write(baseline[1], ["D", "C", "C"])
            self.write(trial[0], ["C", "D", "C"])
            self.write(trial[1], ["C", "C", "C"])
            output = MODULE.render(baseline, trial)
        self.assertEqual(
            output,
            "piano_chord_confirmation_audit: baseline_correct=5/6 baseline_wrong=1 "
            "baseline_flickers=0 trial_correct=5/6 trial_wrong=1 trial_flickers=1 "
            "retained_confirm_frames=2 eligible=0",
        )


if __name__ == "__main__":
    unittest.main()
