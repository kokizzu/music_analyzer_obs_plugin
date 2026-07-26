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

    print("test_build_sharded_tsv: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
