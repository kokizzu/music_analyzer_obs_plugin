#!/usr/bin/env python3

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_sharded_tsv.sh"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        target = tmp / "combined.tsv"
        part_a = tmp / "part-a.tsv"
        part_b = tmp / "part-b.tsv"
        fake_make = tmp / "fake-make.sh"
        fake_make.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    "set -eu",
                    "for arg in \"$@\"; do",
                    "  case \"$arg\" in -j*) continue ;; esac",
                    "  sleep 0.05",
                    "  case \"$arg\" in",
                    "    *part-a.tsv) printf 'name\\nalpha\\n' > \"$arg\" ;;",
                    "    *part-b.tsv) printf 'name\\nbeta\\n' > \"$arg\" ;;",
                    "    *) printf 'unexpected target %s\\n' \"$arg\" >&2; exit 3 ;;",
                    "  esac",
                    "done",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        fake_make.chmod(0o755)

        command = [
            "sh",
            str(SCRIPT),
            str(target),
            str(fake_make),
            "-j2",
            str(part_a),
            str(part_b),
        ]
        first = subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        first_out, first_err = first.communicate(timeout=10)
        second_out, second_err = second.communicate(timeout=10)
        if first.returncode != 0:
            raise AssertionError(f"first builder failed:\nstdout={first_out}\nstderr={first_err}")
        if second.returncode != 0:
            raise AssertionError(f"second builder failed:\nstdout={second_out}\nstderr={second_err}")

        combined = target.read_text(encoding="utf-8").splitlines()
        if combined != ["name", "alpha", "beta"]:
            raise AssertionError(f"unexpected combined TSV: {combined!r}")
        if (tmp / "combined.tsv.lock").exists():
            raise AssertionError("lock directory was not cleaned up")
        leftovers = list(tmp.glob("combined.tsv.*.tmp"))
        if leftovers:
            raise AssertionError(f"temporary files were not cleaned up: {leftovers}")

        stale_target = tmp / "stale-combined.tsv"
        stale_part_a = tmp / "stale-part-a.tsv"
        stale_part_b = tmp / "stale-part-b.tsv"
        stale_part_a.write_text("name\nold-a\n", encoding="utf-8")
        stale_part_b.write_text("name\nold-b\n", encoding="utf-8")
        fake_missing_make = tmp / "fake-missing-make.sh"
        fake_missing_make.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    "set -eu",
                    "for arg in \"$@\"; do",
                    "  case \"$arg\" in -j*) continue ;; esac",
                    "done",
                    "exit 0",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        fake_missing_make.chmod(0o755)

        stale_command = [
            "sh",
            str(SCRIPT),
            str(stale_target),
            str(fake_missing_make),
            "",
            str(stale_part_a),
            str(stale_part_b),
        ]
        stale = subprocess.run(stale_command, cwd=ROOT, text=True, capture_output=True, timeout=10)
        if stale.returncode == 0:
            raise AssertionError("builder reused stale shard files instead of failing")
        if stale_part_a.exists() or stale_part_b.exists():
            raise AssertionError("stale shard files were not removed before rebuilding")
        if stale_target.exists():
            raise AssertionError("target was published from stale shard files")

    print("test_build_sharded_tsv: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
