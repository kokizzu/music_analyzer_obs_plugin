#!/usr/bin/env python3

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import time


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "refresh_analyzer_detected_attribute_rows.py"


def write(path: pathlib.Path, text: str = "source\n") -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_helper(path: pathlib.Path, call_log: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import pathlib
            import sys

            pathlib.Path({str(call_log)!r}).open("a", encoding="utf-8").write(pathlib.Path(sys.argv[0]).name + " " + " ".join(sys.argv[1:]) + "\\n")
            print("generated_by\\targs")
            print(pathlib.Path(sys.argv[0]).name + "\\t" + " ".join(sys.argv[1:]))
            """
        ),
        encoding="utf-8",
    )


def run_refresh(script_root: pathlib.Path, build_dir: pathlib.Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--script-root",
            str(script_root),
            "--build-dir",
            str(build_dir),
            "--python",
            sys.executable,
        ],
        cwd=ROOT,
        check=True,
    )


def calls(path: pathlib.Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        build = root / "build"
        call_log = root / "calls.log"
        for helper in (
            "inspect_instrument_sample_owner_buckets.py",
            "inspect_real_note_attribute_buckets.py",
            "inspect_guitarset_attribute_buckets.py",
            "analyze_drum_primary_debug.py",
        ):
            write_helper(root / "scripts" / helper, call_log)

        write(build / "instrument_sample_attributes.tsv")
        write(build / "real_note_full_mix_attributes.tsv")
        write(build / "guitar_chord_mix_attributes.tsv")
        for drum in ("kick", "tom", "snare", "hihat", "crash", "ride", "rim"):
            write(build / f"{drum}_primary_debug.err")
        for drum in ("kick", "snare", "tom", "rim"):
            write(build / f"full_{drum}_debug.err")

        run_refresh(root, build)
        first_calls = calls(call_log)
        assert len(first_calls) == 7, first_calls
        for output in (
            "instrument_detected_attribute_rows.tsv",
            "real_note_detected_attribute_rows.tsv",
            "real_note_miss_attribute_rows.tsv",
            "guitar_chord_detected_attribute_rows.tsv",
            "guitar_chord_miss_attribute_rows.tsv",
            "drum_primary_miss_attribute_rows.tsv",
            "drum_full_attribute_rows.tsv",
        ):
            assert (build / output).exists(), output
        assert "--include-debug-rows" in (build / "drum_primary_miss_attribute_rows.tsv").read_text(
            encoding="utf-8"
        )

        call_log.write_text("", encoding="utf-8")
        run_refresh(root, build)
        assert calls(call_log) == []

        future = time.time() + 10.0
        os.utime(build / "real_note_full_mix_attributes.tsv", (future, future))
        run_refresh(root, build)
        second_calls = calls(call_log)
        assert len(second_calls) == 2, second_calls
        assert all(call.startswith("inspect_real_note_attribute_buckets.py ") for call in second_calls), second_calls

    print("test_refresh_analyzer_detected_attribute_rows: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
