#!/usr/bin/env python3
"""Deploy the freshly built Windows standalone executable to the SMB mount."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MOUNTPOINT = Path("/media/kyz/aigenshared")
SOURCE_DIR = Path("build/windows-x64/portable")
FSTAB = Path("/etc/fstab")


def artifacts() -> tuple[tuple[Path, Path], ...]:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"missing Windows portable directory: {SOURCE_DIR}")
    return tuple(
        (source, MOUNTPOINT / source.name)
        for source in sorted(SOURCE_DIR.iterdir())
        if source.is_file()
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


REPO_ROOT = Path(__file__).resolve().parents[1]


def deployment_changelog_name(now: datetime | None = None) -> str:
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H%M%S")
    return f"changelog-{timestamp}.txt"


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return f"git command failed ({result.returncode}): {' '.join(args)}"
    return result.stdout.rstrip()


def deployment_changelog(now: datetime | None = None) -> str:
    deployed_at = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    commit = git_text("rev-parse", "--short", "HEAD")
    committed = git_text(
        "log",
        "-3",
        "--date=format:%Y-%m-%d %H:%M:%S",
        "--pretty=format:%h %ad %s",
    )
    status = git_text("status", "--short")
    staged_stat = git_text("diff", "--cached", "--stat")
    unstaged_stat = git_text("diff", "--stat")
    sections = [
        "Music Analyzer Windows deployment changelog",
        f"deployed_at={deployed_at}",
        f"commit={commit}",
        "",
        "Latest 3 committed changes:",
        committed or "(none)",
        "",
        "Uncommitted changes:",
        status or "(clean)",
        "",
        "Staged diff summary:",
        staged_stat or "(none)",
        "",
        "Unstaged diff summary:",
        unstaged_stat or "(none)",
        "",
    ]
    return "\n".join(sections)


def write_deployment_changelog(directory: Path, now: datetime | None = None) -> Path:
    changelog = directory / deployment_changelog_name(now)
    temporary = directory / f".{changelog.name}.deploying"
    try:
        temporary.write_text(deployment_changelog(now), encoding="utf-8")
        os.replace(temporary, changelog)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"deployed={changelog}")
    print(f"bytes={changelog.stat().st_size}")
    return changelog


def validate_paths() -> None:
    validate_source()
    if not mount_available():
        raise SystemExit(f"deployment directory is not an accessible mounted share: {MOUNTPOINT}")


def validate_source() -> None:
    selected = artifacts()
    if not selected:
        raise SystemExit(f"Windows portable directory is empty: {SOURCE_DIR}")


def ensure_signed_source() -> None:
    """Sign both Windows executables before any deployment copy is attempted."""
    signer = REPO_ROOT / "scripts" / "sign_windows_standalone.py"
    result = subprocess.run(
        [sys.executable, str(signer), "apply"],
        cwd=REPO_ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Windows deployment refused: executable signing failed")


def mount_available() -> bool:
    try:
        return MOUNTPOINT.is_dir() and os.path.ismount(MOUNTPOINT)
    except OSError:
        return False


def print_plan() -> None:
    validate_source()
    mounted = mount_available()
    if mounted:
        planned_artifacts = artifacts()
    else:
        entry = smb_entry()
        if entry is None:
            raise SystemExit(f"deployment share is unavailable and no fstab SMB entry was found: {MOUNTPOINT}")
        smb_source, _ = entry
        print(f"mount_unavailable={MOUNTPOINT}")
        print(f"fallback=smbclient:{smb_source}")
        planned_artifacts = tuple((source, Path(smb_source) / source.name) for source, _ in artifacts())
    for source, destination in planned_artifacts:
        source_stat = source.stat()
        print(f"source={source}")
        print(f"destination={destination}")
        print(f"source_bytes={source_stat.st_size}")
        print(f"source_sha256={sha256(source)}")
        if mounted and destination.exists():
            destination_stat = destination.stat()
            print(f"existing_bytes={destination_stat.st_size}")
            print(f"existing_sha256={sha256(destination)}")
            print("action=replace-existing")
        elif mounted:
            print("existing=absent")
            print("action=create")
        else:
            print("existing=unavailable")
            print("action=upload-atomically")


def copy_atomically() -> None:
    ensure_signed_source()
    for source, destination in artifacts():
        temporary = destination.with_name(f".{destination.name}.deploying")
        try:
            shutil.copy2(source, temporary)
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
        source_hash = sha256(source)
        destination_hash = sha256(destination)
        if source_hash != destination_hash:
            raise SystemExit(
                f"checksum mismatch after deployment: source={source_hash} destination={destination_hash}"
            )
        print(f"deployed={destination}")
        print(f"bytes={destination.stat().st_size}")
        print(f"sha256={destination_hash}")
    write_deployment_changelog(MOUNTPOINT)


def smb_entry() -> tuple[str, dict[str, str]] | None:
    try:
        lines = FSTAB.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            fields = shlex.split(line, comments=True)
        except ValueError:
            continue
        if len(fields) < 4 or fields[1] != str(MOUNTPOINT) or fields[2] != "cifs":
            continue
        options: dict[str, str] = {}
        for item in fields[3].split(","):
            key, separator, value = item.partition("=")
            if separator:
                options[key] = value
        if options.get("username") and options.get("password"):
            return fields[0], options
    return None


def smb_upload_atomically() -> bool:
    ensure_signed_source()
    entry = smb_entry()
    if entry is None:
        return False
    smb_source, options = entry
    credential_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", prefix="music-analyzer-smb-", delete=False
        ) as credentials:
            credential_path = credentials.name
            credentials.write(f"username = {options['username']}\n")
            credentials.write(f"password = {options['password']}\n")
            if options.get("domain"):
                credentials.write(f"domain = {options['domain']}\n")
        os.chmod(credential_path, 0o600)
        for source, _ in artifacts():
            temporary_name = f".{source.name}.deploying"
            upload = subprocess.run(
                [
                    "smbclient",
                    smb_source,
                    "-A",
                    credential_path,
                    "-c",
                    f"put {source.resolve()} {temporary_name}; rename {temporary_name} {source.name}",
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            if upload.returncode != 0:
                if upload.stdout:
                    print(upload.stdout.rstrip())
                if upload.stderr:
                    print(upload.stderr.rstrip())
                return False

            with tempfile.NamedTemporaryFile(prefix="music-analyzer-smb-", delete=False) as downloaded:
                download_path = downloaded.name
            try:
                download = subprocess.run(
                    [
                        "smbclient",
                        smb_source,
                        "-A",
                        credential_path,
                        "-c",
                        f"get {source.name} {download_path}",
                    ],
                    check=False,
                    text=True,
                    capture_output=True,
                )
                if download.returncode != 0:
                    if download.stdout:
                        print(download.stdout.rstrip())
                    if download.stderr:
                        print(download.stderr.rstrip())
                    return False
                source_hash = sha256(source)
                uploaded_hash = sha256(Path(download_path))
                if source_hash != uploaded_hash:
                    print(f"SMB checksum mismatch: source={source_hash} uploaded={uploaded_hash}")
                    return False
                print(f"deployed=//{smb_source.removeprefix('//')}/{source.name}")
                print(f"bytes={source.stat().st_size}")
                print(f"sha256={uploaded_hash}")
            finally:
                Path(download_path).unlink(missing_ok=True)
        changelog_name = deployment_changelog_name()
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="music-analyzer-smb-changelog-", delete=False
        ) as changelog:
            changelog.write(deployment_changelog())
            changelog_path = Path(changelog.name)
        try:
            temporary_name = f".{changelog_name}.deploying"
            upload = subprocess.run(
                [
                    "smbclient",
                    smb_source,
                    "-A",
                    credential_path,
                    "-c",
                    f"put {changelog_path.resolve()} {temporary_name}; rename {temporary_name} {changelog_name}",
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            if upload.returncode != 0:
                if upload.stdout:
                    print(upload.stdout.rstrip())
                if upload.stderr:
                    print(upload.stderr.rstrip())
                return False
            print(f"deployed=//{smb_source.removeprefix('//')}/{changelog_name}")
            print(f"bytes={changelog_path.stat().st_size}")
        finally:
            changelog_path.unlink(missing_ok=True)
        return True
    except FileNotFoundError:
        return False
    finally:
        if credential_path:
            Path(credential_path).unlink(missing_ok=True)


def apply_deployment(as_root: bool = False) -> None:
    validate_source()
    if not mount_available():
        if smb_upload_atomically():
            return
        raise SystemExit(f"deployment share is unavailable: {MOUNTPOINT}")
    try:
        copy_atomically()
    except OSError:
        if smb_upload_atomically():
            return
        if as_root:
            raise
        print("mounted share is not writable by the current user; retrying with sudo")
        command = ["sudo", "-n", sys.executable, str(Path(__file__).resolve()), "root-apply"]
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            raise SystemExit(
                "sudo deployment failed; run `sudo -v` once, then retry "
                "`make deploy-windows-mounted`"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply", "root-apply"))
    args = parser.parse_args()
    if args.mode == "plan":
        print_plan()
    elif args.mode == "apply":
        apply_deployment()
    else:
        apply_deployment(as_root=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
