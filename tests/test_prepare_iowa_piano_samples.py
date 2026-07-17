#!/usr/bin/env python3
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prepare_iowa_piano_samples


def write_executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_fake_curl(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
import shutil
import sys
import urllib.parse

args = sys.argv[1:]
out = args[args.index("-o") + 1]
url = args[-1]
parsed = urllib.parse.urlparse(url)
if parsed.scheme == "file":
    source = urllib.parse.unquote(parsed.path)
else:
    source = urllib.parse.unquote(url)
shutil.copyfile(source, out)
""",
    )


def write_flaky_curl(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
import urllib.parse

args = sys.argv[1:]
out = Path(args[args.index("-o") + 1])
url = args[-1]
parsed = urllib.parse.urlparse(url)
if parsed.scheme == "file":
    source = urllib.parse.unquote(parsed.path)
else:
    source = urllib.parse.unquote(url)
state = Path(str(sys.argv[0]) + ".state")
if not state.exists():
    out.write_bytes(b"partial")
    state.write_text("failed", encoding="utf-8")
    raise SystemExit(28)
shutil.copyfile(source, out)
""",
    )


def write_fake_ffmpeg(path):
    write_executable(
        path,
        """#!/usr/bin/env python3
import shutil
import sys

args = sys.argv[1:]
source = args[args.index("-i") + 1]
dest = args[-1]
shutil.copyfile(source, dest)
""",
    )


def manifest_rows(path):
    with path.open("r", encoding="utf-8") as file:
        return [line.rstrip("\n").split("\t") for line in file.readlines()[1:]]


def make_fixture(root):
    served = root / "served"
    audio = served / "audio"
    audio.mkdir(parents=True)
    filenames = ["Piano.mf.C1.aiff", "Piano.mf.D1.aiff", "Piano.mf.E1.aiff"]
    for filename in filenames:
        (audio / filename).write_bytes(b"fake-aiff")
    links = "\n".join(f'<a href="audio/{filename}">{filename}</a>' for filename in filenames)
    (served / "MISpiano.html").write_text(f"<html>{links}</html>", encoding="utf-8")
    return served


def run_prepare(base, output_name, min_samples, extra_args=None, flaky_curl=False):
    served = make_fixture(base / output_name)
    cache = base / output_name / "cache"
    output = base / output_name / "out"
    curl = base / output_name / "fake-curl"
    ffmpeg = base / output_name / "fake-ffmpeg"
    if flaky_curl:
        write_flaky_curl(curl)
    else:
        write_fake_curl(curl)
    write_fake_ffmpeg(ffmpeg)
    page_url = (served / "MISpiano.html").resolve().as_uri()
    audio_url = (served / "audio").resolve().as_uri() + "/"
    args = [
        "--page-url",
        page_url,
        "--file-base-url",
        audio_url,
        "--source-dir",
        str(cache),
        "--output",
        str(output),
        "--limit",
        "3",
        "--min-samples",
        str(min_samples),
        "--ffmpeg",
        str(ffmpeg),
        "--curl",
        str(curl),
    ]
    if extra_args:
        args.extend(extra_args)
    prepare_iowa_piano_samples.main(args)
    return output


def test_writes_manifest_when_minimum_is_met():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(Path(temp), "ok", min_samples=3)
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 3:
            raise AssertionError("expected three prepared Iowa piano rows")
        if {row[1] for row in rows} != {"piano"}:
            raise AssertionError("expected Iowa rows to be piano family")
        if {row[2] for row in rows} != {"keyboard"}:
            raise AssertionError("expected Iowa rows to map to keyboard detector family")
        if not prepare_iowa_piano_samples.manifest_complete(output / "manifest.tsv", rows[0][7], 3):
            raise AssertionError("complete manifest should satisfy matching minimum")
        if prepare_iowa_piano_samples.manifest_complete(output / "manifest.tsv", rows[0][7], 4):
            raise AssertionError("three-row manifest must not satisfy a four-row minimum")


def test_retries_partial_download_before_skipping_sample():
    with tempfile.TemporaryDirectory() as temp:
        output = run_prepare(
            Path(temp),
            "retry",
            min_samples=3,
            extra_args=["--download-retries", "1"],
            flaky_curl=True,
        )
        rows = manifest_rows(output / "manifest.tsv")
        if len(rows) != 3:
            raise AssertionError("retrying a partial download should still prepare all rows")


def test_writes_partial_manifest_when_minimum_is_not_met():
    with tempfile.TemporaryDirectory() as temp:
        try:
            run_prepare(Path(temp), "partial", min_samples=4)
        except SystemExit as exc:
            if exc.code == 0:
                raise AssertionError("minimum shortfall should fail")
        else:
            raise AssertionError("minimum shortfall should raise SystemExit")
        output = Path(temp) / "partial" / "out"
        if (output / "manifest.tsv").exists():
            raise AssertionError("shortfall must not publish a complete manifest")
        if len(manifest_rows(output / "manifest.tsv.partial")) != 3:
            raise AssertionError("shortfall should write a diagnostic partial manifest")


def main():
    test_writes_manifest_when_minimum_is_met()
    test_retries_partial_download_before_skipping_sample()
    test_writes_partial_manifest_when_minimum_is_not_met()
    print("test_prepare_iowa_piano_samples: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
