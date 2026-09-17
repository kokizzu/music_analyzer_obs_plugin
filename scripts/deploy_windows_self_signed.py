#!/usr/bin/env python3
"""Plan, copy, and verify the self-signed Windows build on the CIFS share."""

from __future__ import annotations

import argparse
import errno
import hashlib
import shutil
import subprocess
import sys
import time
from pathlib import Path


SOURCE_ROOT = Path("build/windows-x64-self-signed/portable")
CERTIFICATE = Path("build/windows-self-signing/music-analyzer-local-dev.crt")
TRUST_SCRIPT = Path("scripts/trust_music_analyzer.ps1")
MOUNTPOINT = Path("/media/kyz/aigenshared")
COPY_RETRIES = 5
COPY_RETRY_DELAY_SECONDS = 1.0


def run_findmnt() -> str:
    result = subprocess.run(
        ["findmnt", "-T", str(MOUNTPOINT), "-o", "SOURCE,TARGET,FSTYPE"],
        check=False,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise RuntimeError(f"cannot inspect {MOUNTPOINT}: {output}")
    return output


def destination() -> Path:
    return MOUNTPOINT


def source_files() -> list[Path]:
    if not SOURCE_ROOT.is_dir():
        raise RuntimeError(f"signed portable build is missing: {SOURCE_ROOT}")
    files = sorted(path for path in SOURCE_ROOT.rglob("*") if path.is_file())
    if not files:
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


def smb_credentials(options: dict[str, str]) -> Path:
    credentials = tempfile.NamedTemporaryFile(
        mode="w", prefix="music-analyzer-smb-", delete=False
    )
    try:
        credentials.write(f"username = {options['username']}\n")
        credentials.write(f"password = {options['password']}\n")
        if options.get("domain"):
            credentials.write(f"domain = {options['domain']}\n")
    finally:
        credentials.close()
    os.chmod(credentials.name, 0o600)
    return Path(credentials.name)


def smb_command(share: str, credentials: Path, command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["smbclient", share, "-A", str(credentials), "-c", command],
        check=False,
        capture_output=True,
        text=True,
    )


def smb_share() -> tuple[str, Path] | None:
    entry = smb_entry()
    if entry is None or shutil.which("smbclient") is None:
        return None
    share, options = entry
    credentials = smb_credentials(options)
    return share, credentials


def smb_error(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout + result.stderr).strip() or f"smbclient exited with {result.returncode}"


def smb_put(share: str, credentials: Path, source: Path, remote_name: str) -> None:
    temporary_name = f".{remote_name}.music-analyzer-deploying"
    uploaded = smb_command(
        share,
        credentials,
        f'put "{source.resolve()}" "{temporary_name}"',
    )
    if uploaded.returncode != 0:
        raise RuntimeError(f"SMB upload failed for {remote_name}: {smb_error(uploaded)}")
    renamed = smb_command(share, credentials, f'rename "{temporary_name}" "{remote_name}"')
    if renamed.returncode != 0:
        raise RuntimeError(f"SMB rename failed for {remote_name}: {smb_error(renamed)}")


def smb_get(share: str, credentials: Path, remote_name: str, local_path: Path) -> None:
    result = smb_command(share, credentials, f'get "{remote_name}" "{local_path}"')
    if result.returncode != 0:
        raise RuntimeError(f"SMB download failed for {remote_name}: {smb_error(result)}")


def accessible_mount_info() -> str | None:
    try:
        mount_info = run_findmnt()
        if "192.168.1.132/shared" not in mount_info or "cifs" not in mount_info:
            return None
        probe = subprocess.run(
            ["stat", "-c", "%F", str(MOUNTPOINT)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if probe.returncode != 0:
            return None
        return mount_info
    except (OSError, subprocess.TimeoutExpired):
        return None


def deployment_files() -> list[Path]:
    return source_files() + [CERTIFICATE, TRUST_SCRIPT]


def compare_downloaded(source: Path, share: str, credentials: Path, temporary_directory: Path) -> str | None:
    downloaded = temporary_directory / source.name
    try:
        smb_get(share, credentials, source.name, downloaded)
    except RuntimeError as error:
        return str(error)
    if downloaded.stat().st_size != source.stat().st_size:
        return f"size mismatch: {source.name}"
    if sha256(downloaded) != sha256(source):
        return f"hash mismatch: {source.name}"
    return None


        raise RuntimeError(f"signed portable build is empty: {SOURCE_ROOT}")
    return files


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_with_retry(source: Path, target: Path) -> None:
    for attempt in range(COPY_RETRIES):
        try:
            shutil.copy2(source, target)
            return
        except OSError as error:
            retryable = error.errno in {errno.EBUSY, errno.ETXTBSY}
            if not retryable or attempt + 1 >= COPY_RETRIES:
                raise
            print(
                f"busy deployment target: {target}; retrying in "
                f"{COPY_RETRY_DELAY_SECONDS:.0f}s ({attempt + 1}/{COPY_RETRIES - 1})"
            )
            time.sleep(COPY_RETRY_DELAY_SECONDS)


def plan() -> None:
    files = source_files()
    mount_info = run_findmnt()
    if "192.168.1.132/shared" not in mount_info or "cifs" not in mount_info:
        raise RuntimeError(
            f"{MOUNTPOINT} is not mounted from //192.168.1.132/shared as CIFS:\n{mount_info}"
        )
    print(f"mounted share: {mount_info}")
    print(f"source: {SOURCE_ROOT.resolve()}")
    print(f"destination: {destination()}")
    print(f"certificate to copy: {CERTIFICATE.resolve()}")
    print(f"trust script to copy: {TRUST_SCRIPT.resolve()}")
    print(f"files to copy directly: {len(files)}")
    for path in files:
        relative = path.relative_to(SOURCE_ROOT)
        target = destination() / relative
        conflict = " [overwrite]" if target.exists() else ""
        print(f"  {relative} -> {target}{conflict} ({path.stat().st_size} bytes)")


def apply() -> None:
    files = source_files()
    mount_info = run_findmnt()
    if "192.168.1.132/shared" not in mount_info or "cifs" not in mount_info:
        raise RuntimeError(
            f"{MOUNTPOINT} is not mounted from //192.168.1.132/shared as CIFS:\n{mount_info}"
        )
    if not CERTIFICATE.is_file():
        raise RuntimeError(f"public certificate is missing: {CERTIFICATE}")
    if not TRUST_SCRIPT.is_file():
        raise RuntimeError(f"trust script is missing: {TRUST_SCRIPT}")
    target = destination()
    for source_path in files:
        target_path = target / source_path.relative_to(SOURCE_ROOT)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        copy_with_retry(source_path, target_path)
    copy_with_retry(CERTIFICATE, target / CERTIFICATE.name)
    copy_with_retry(TRUST_SCRIPT, target / TRUST_SCRIPT.name)
    print(f"deployed {len(files)} portable files directly to {target}")
    print(f"deployed public certificate and trust script to {target}")


def verify() -> None:
    source = source_files()
    target = destination()
    if not target.is_dir():
        raise RuntimeError(f"deployment directory is missing: {target}")
    mismatches: list[str] = []
    for source_path in source:
        target_path = target / source_path.relative_to(SOURCE_ROOT)
        if not target_path.is_file():
            mismatches.append(f"missing: {target_path}")
            continue
        if source_path.stat().st_size != target_path.stat().st_size:
            mismatches.append(f"size mismatch: {target_path}")
            continue
        if sha256(source_path) != sha256(target_path):
            mismatches.append(f"hash mismatch: {target_path}")
    for source_path in (CERTIFICATE, TRUST_SCRIPT):
        target_path = target / source_path.name
        if not target_path.is_file():
            mismatches.append(f"missing: {target_path}")
        elif sha256(source_path) != sha256(target_path):
            mismatches.append(f"hash mismatch: {target_path}")
    if mismatches:
        raise RuntimeError("deployment verification failed:\n" + "\n".join(mismatches))
    print(f"verified {len(source)} portable files plus certificate and trust script")
    print(f"deployment: {target}")


    mount_info = accessible_mount_info()
    if not mount_info:
        connection = smb_share()
        if connection is None:
            raise RuntimeError(f"{MOUNTPOINT} is inaccessible and no usable smbclient fallback was found")
        share, credentials = connection
        mismatches: list[str] = []
        try:
            with tempfile.TemporaryDirectory(prefix="music-analyzer-smb-verify-") as directory:
                temporary_directory = Path(directory)
                for source_path in deployment_files():
                    mismatch = compare_downloaded(source_path, share, credentials, temporary_directory)
                    if mismatch:
                        mismatches.append(mismatch)
        finally:
            credentials.unlink(missing_ok=True)
        if mismatches:
            raise RuntimeError("SMB deployment verification failed:\n" + "\n".join(mismatches))
        print(f"verified {len(source)} portable files plus certificate and trust script through SMB fallback")
        print(f"deployment: {share}")
        return

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("plan", "apply", "verify"), required=True)
    options = parser.parse_args()
    try:
        {"plan": plan, "apply": apply, "verify": verify}[options.mode]()
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
