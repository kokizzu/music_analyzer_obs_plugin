#!/usr/bin/env python3
"""Plan, create, and verify a self-signed Authenticode Windows build."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path


SOURCE_ROOT = Path("build/windows-x64/portable")
SIGNED_ROOT = Path("build/windows-x64-self-signed/portable")
STAGING_ROOT = Path("build/.windows-x64-self-signed-staging")
SIGNING_ROOT = Path("build/windows-self-signing")
CERT_PATH = SIGNING_ROOT / "music-analyzer-local-dev.crt"
KEY_PATH = SIGNING_ROOT / "music-analyzer-local-dev.key"
ARCHIVE_PATH = Path("build/music-analyzer-windows-x64-self-signed.zip")
STAGING_ARCHIVE = Path("build/.music-analyzer-windows-x64-self-signed.zip.staging")
LOCAL_SIGNER = Path("build/windows-signing-tool/usr/bin/osslsigncode")


def exe_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() == ".exe"
    )


def signer_path() -> str | None:
    system_signer = shutil.which("osslsigncode")
    if system_signer:
        return system_signer
    if LOCAL_SIGNER.is_file():
        return str(LOCAL_SIGNER)
    return None


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}")
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    if check and result.returncode:
        raise RuntimeError(f"command failed with exit code {result.returncode}")
    return result


def require_source() -> list[Path]:
    if not SOURCE_ROOT.is_dir():
        raise RuntimeError(f"Windows build directory is missing: {SOURCE_ROOT}")
    files = exe_files(SOURCE_ROOT)
    if not files:
        raise RuntimeError(f"no .exe files found below {SOURCE_ROOT}")
    return files


def plan() -> None:
    files = require_source()
    print(f"source: {SOURCE_ROOT.resolve()}")
    print(f"signed copy: {SIGNED_ROOT.resolve()}")
    print(f"certificate: {CERT_PATH.resolve()}")
    print(f"archive: {ARCHIVE_PATH.resolve()}")
    print(f"openssl: {shutil.which('openssl') or 'missing'}")
    print(f"osslsigncode: {signer_path() or 'missing'}")
    print("executables:")
    for path in files:
        print(f"  {path.relative_to(SOURCE_ROOT)} ({path.stat().st_size} bytes)")
    if SIGNED_ROOT.exists():
        print("warning: signed output directory already exists; apply will refresh it")
    if ARCHIVE_PATH.exists():
        print("warning: signed archive already exists; apply will refresh it")


def create_certificate() -> None:
    SIGNING_ROOT.mkdir(parents=True, exist_ok=True)
    if CERT_PATH.exists() != KEY_PATH.exists():
        raise RuntimeError("certificate and private key must either both exist or both be absent")
    if not CERT_PATH.exists():
        run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:3072",
                "-sha256",
                "-nodes",
                "-days",
                "3650",
                "-keyout",
                str(KEY_PATH),
                "-out",
                str(CERT_PATH),
                "-subj",
                "/CN=Music Analyzer Local Development/O=Kokizzu/OU=Code Signing",
                "-addext",
                "basicConstraints=critical,CA:FALSE",
                "-addext",
                "keyUsage=critical,digitalSignature",
                "-addext",
                "extendedKeyUsage=codeSigning",
            ]
        )
    os.chmod(KEY_PATH, stat.S_IRUSR | stat.S_IWUSR)


def apply() -> None:
    source_files = require_source()
    if shutil.which("openssl") is None:
        raise RuntimeError("openssl is required but not installed")
    signer = signer_path()
    if signer is None:
        raise RuntimeError("osslsigncode is required; run make fetch-windows-signing-tool")
    if STAGING_ROOT.exists():
        raise RuntimeError(f"refusing to reuse stale staging directory: {STAGING_ROOT}")
    if STAGING_ARCHIVE.exists():
        raise RuntimeError(f"refusing to reuse stale staging archive: {STAGING_ARCHIVE}")

    create_certificate()
    shutil.copytree(SOURCE_ROOT, STAGING_ROOT)
    for source_file in source_files:
        target = STAGING_ROOT / source_file.relative_to(SOURCE_ROOT)
        temporary = target.with_name(f".{target.name}.signed.tmp")
        run(
            [
                signer,
                "sign",
                "-certs",
                str(CERT_PATH),
                "-key",
                str(KEY_PATH),
                "-h",
                "sha256",
                "-n",
                "Music Analyzer Local Development",
                "-in",
                str(target),
                "-out",
                str(temporary),
            ]
        )
        os.replace(temporary, target)

    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(STAGING_ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(STAGING_ROOT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(STAGING_ROOT.parent))

    previous_root = SIGNED_ROOT.with_name(f".{SIGNED_ROOT.name}.previous")
    if previous_root.exists():
        raise RuntimeError(f"refusing to reuse stale previous directory: {previous_root}")
    if SIGNED_ROOT.exists():
        os.replace(SIGNED_ROOT, previous_root)
    try:
        os.replace(STAGING_ROOT, SIGNED_ROOT)
    except OSError:
        if previous_root.exists() and not SIGNED_ROOT.exists():
            os.replace(previous_root, SIGNED_ROOT)
        raise
    if previous_root.exists():
        shutil.rmtree(previous_root)
    os.replace(STAGING_ARCHIVE, ARCHIVE_PATH)
    print(f"created signed build: {SIGNED_ROOT}")
    print(f"created signed archive: {ARCHIVE_PATH}")
    print(f"install this public certificate on Windows if needed: {CERT_PATH}")


def verify() -> None:
    files = exe_files(SIGNED_ROOT)
    if not files:
        raise RuntimeError(f"no signed .exe files found below {SIGNED_ROOT}")
    signer = signer_path()
    if signer is None:
        raise RuntimeError("osslsigncode is required; run make fetch-windows-signing-tool")
    if not CERT_PATH.is_file():
        raise RuntimeError(f"signing certificate is missing: {CERT_PATH}")
    run(
        [
            "openssl",
            "x509",
            "-in",
            str(CERT_PATH),
            "-noout",
            "-subject",
            "-issuer",
            "-fingerprint",
            "-sha256",
            "-dates",
        ]
    )
    for path in files:
        result = run(
            [signer, "verify", "-CAfile", str(CERT_PATH), "-in", str(path)],
            check=False,
        )
        if result.returncode:
            raise RuntimeError(f"signature verification failed: {path}")
    if not ARCHIVE_PATH.is_file():
        raise RuntimeError(f"signed archive is missing: {ARCHIVE_PATH}")
    print(f"verified {len(files)} signed executable(s)")


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
