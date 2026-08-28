#!/usr/bin/env python3
"""Plan or prepare a CC BY 4.0 NSynth acoustic-bass note fixture."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import zlib
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build" / "nsynth"
SPLIT = os.environ.get("NSYNTH_SPLIT", "test")
if SPLIT not in {"train", "valid", "test"}:
    raise RuntimeError(f"unsupported NSynth split: {SPLIT}")
ARCHIVE = BUILD_DIR / f"nsynth-{SPLIT}.jsonwav.tar.gz"
OUTPUT = BUILD_DIR / f"acoustic_bass_{SPLIT}"
# The original Magenta HTTPS hostname currently has a certificate mismatch in
# this environment. This public HTTPS mirror carries the same CC BY 4.0 files.
URL = f"https://huggingface.co/datasets/confit/nsynth/resolve/main/nsynth-{SPLIT}.jsonwav.tar.gz?download=true"
METADATA_URL = "https://huggingface.co/api/datasets/confit/nsynth/tree/main?recursive=false&expand=true"


def archive_size() -> int | None:
    try:
        with urlopen(METADATA_URL, timeout=20) as response:
            entries = json.load(response)
        expected_name = ARCHIVE.name
        for entry in entries:
            if entry.get("path") != expected_name:
                continue
            lfs = entry.get("lfs") or {}
            size = lfs.get("size", entry.get("size"))
            if size is not None:
                return int(size)
        raise RuntimeError(f"NSynth metadata has no {expected_name}")
    except OSError as error:
        print(f"archive_size_unavailable={error}")
        return None


def human_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024.0
    raise AssertionError("unreachable")


def plan() -> None:
    free_bytes = shutil.disk_usage(BUILD_DIR.parent if BUILD_DIR.parent.exists() else ROOT).free
    print(f"source=NSynth {SPLIT} json/wav")
    print("license=CC-BY-4.0")
    print("selection=instrument_family=bass instrument_source=acoustic")
    print(f"archive={ARCHIVE}")
    partial = ARCHIVE.with_suffix(ARCHIVE.suffix + ".part")
    if ARCHIVE.exists():
        actual_size = ARCHIVE.stat().st_size
        valid, detail = archive_is_complete(ARCHIVE)
        print(f"archive_state={'complete-cache' if valid else 'invalid-cache'} {human_bytes(actual_size)} {detail}")
    elif partial.exists():
        try:
            partial_size = partial.stat().st_size
            valid, detail = archive_is_complete(partial)
            print(
                f"archive_state={'complete-download-candidate' if valid else 'partial-download'} "
                f"{human_bytes(partial_size)} {detail}"
            )
        except FileNotFoundError:
            print("archive_state=promoting-cache")
    else:
        print("archive_state=not-downloaded")
    print(f"output={OUTPUT}")
    print(f"free_space={human_bytes(free_bytes)}")
    expected_size = archive_size()
    if expected_size is not None:
        print(f"download_size={human_bytes(expected_size)}")
        print(f"space_check={'ok' if free_bytes >= expected_size * 2 else 'insufficient'}")


def load_examples(archive: tarfile.TarFile) -> dict[str, dict]:
    member = next(member for member in archive.getmembers() if member.name.endswith("examples.json"))
    stream = archive.extractfile(member)
    if stream is None:
        raise RuntimeError("NSynth archive has no readable examples.json")
    return json.load(stream)


def selected_examples(examples: dict[str, dict]) -> list[tuple[str, dict]]:
    selected = [
        (note_id, value)
        for note_id, value in examples.items()
        if value.get("instrument_family_str") == "bass"
        and value.get("instrument_source_str") == "acoustic"
    ]
    return sorted(selected, key=lambda item: (item[1].get("pitch", -1), item[0]))


def archive_is_valid(path: Path) -> tuple[bool, str]:
    try:
        with tarfile.open(path, "r:gz") as archive:
            load_examples(archive)
    except (tarfile.TarError, OSError, RuntimeError, zlib.error) as error:
        return False, str(error)
    return True, "ok"


def archive_is_complete(path: Path) -> tuple[bool, str]:
    expected_size = archive_size()
    actual_size = path.stat().st_size
    if expected_size is not None and actual_size != expected_size:
        return False, f"size={actual_size} expected={expected_size}"
    return archive_is_valid(path)


def probe_range() -> None:
    partial = ARCHIVE.with_suffix(ARCHIVE.suffix + ".part")
    offset = partial.stat().st_size if partial.exists() else 0
    request = Request(URL, headers={"Range": f"bytes={offset}-{offset}"})
    try:
        with urlopen(request, timeout=20) as response:
            print(f"url={response.url}")
            print(f"status={response.status}")
            print(f"content_range={response.headers.get('Content-Range', '')}")
            print(f"content_length={response.headers.get('Content-Length', '')}")
    except HTTPError as error:
        print(f"status={error.code}")
        print(f"content_range={error.headers.get('Content-Range', '')}")


def download_archive(destination: Path) -> None:
    offset = destination.stat().st_size if destination.exists() else 0
    request = Request(URL)
    if offset:
        request.add_header("Range", f"bytes={offset}-")
    with urlopen(request, timeout=60) as response:
        append = offset > 0 and response.status == 206
        content_range = response.headers.get("Content-Range", "")
        if append and not content_range.startswith(f"bytes {offset}-"):
            raise RuntimeError(f"unexpected resume Content-Range: {content_range!r}")
        if content_range:
            print(f"content_range={content_range}")
        if offset and not append:
            print("resume_not_supported=restarting")
            offset = 0
        mode = "ab" if append else "wb"
        with destination.open(mode) as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    print(f"downloaded_bytes={destination.stat().st_size}")


def quarantine_invalid_archive() -> None:
    partial = ARCHIVE.with_suffix(ARCHIVE.suffix + ".part")
    source = ARCHIVE if ARCHIVE.exists() else partial
    if not source.exists():
        print("quarantine=not-needed")
        return
    valid, _ = archive_is_complete(source)
    if valid:
        print("quarantine=not-needed")
        return
    quarantine = source.with_suffix(source.suffix + ".invalid")
    suffix = 1
    while quarantine.exists():
        quarantine = source.with_suffix(source.suffix + f".invalid.{suffix}")
        suffix += 1
    os.replace(source, quarantine)
    print(f"quarantined={quarantine}")


def apply_locked() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists():
        valid, _ = archive_is_complete(ARCHIVE)
        if not valid:
            raise RuntimeError("invalid archive cache; run the quarantine target before retrying")
    if not ARCHIVE.exists():
        temporary = ARCHIVE.with_suffix(ARCHIVE.suffix + ".part")
        valid, _ = archive_is_complete(temporary) if temporary.exists() else (False, "missing")
        if not valid:
            print(f"download={URL}")
            download_archive(temporary)
        valid, _ = archive_is_complete(temporary)
        if not valid:
            raise RuntimeError("download is incomplete; rerun the prepare target to resume")
        os.replace(temporary, ARCHIVE)

    with tarfile.open(ARCHIVE, "r:gz") as archive:
        examples = load_examples(archive)
        selected = selected_examples(examples)
        if not selected:
            raise RuntimeError(f"NSynth {SPLIT} split has no acoustic bass samples")
        members = {member.name.rsplit("/", 1)[-1]: member for member in archive.getmembers()}
        with tempfile.TemporaryDirectory(prefix="nsynth-acoustic-bass-", dir=BUILD_DIR) as temporary:
            staged = Path(temporary) / OUTPUT.name
            audio_dir = staged / "audio"
            audio_dir.mkdir(parents=True)
            manifest_lines = ["id\tpitch\tvelocity\tinstrument\tpath"]
            for note_id, metadata in selected:
                filename = f"{note_id}.wav"
                member = members.get(filename)
                if member is None:
                    raise RuntimeError(f"missing audio member for {note_id}")
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError(f"unreadable audio member for {note_id}")
                destination = audio_dir / filename
                with destination.open("wb") as output:
                    shutil.copyfileobj(source, output)
                manifest_lines.append(
                    "\t".join((
                        note_id,
                        str(metadata["pitch"]),
                        str(metadata["velocity"]),
                        metadata["instrument_str"],
                        f"audio/{filename}",
                    ))
                )
            (staged / "manifest.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
            if OUTPUT.exists():
                shutil.rmtree(OUTPUT)
            os.replace(staged, OUTPUT)
    print(f"prepared_samples={len(selected)}")
    print(f"manifest={OUTPUT / 'manifest.tsv'}")


def apply() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = BUILD_DIR / f"nsynth-{SPLIT}.import.lock"
    with lock_path.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("another NSynth fixture import is already running") from error
        apply_locked()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply", "quarantine", "probe"))
    args = parser.parse_args()
    if args.mode == "plan":
        plan()
    elif args.mode == "apply":
        apply()
    elif args.mode == "quarantine":
        quarantine_invalid_archive()
    else:
        probe_range()


if __name__ == "__main__":
    main()
