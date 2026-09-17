#!/usr/bin/env python3
"""Test the signed Windows deployment's SMB fallback without contacting the share."""

from pathlib import Path
import importlib.util
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "deploy_windows_self_signed.py"


def load_module():
    spec = importlib.util.spec_from_file_location("deploy_windows_self_signed", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_module()
    with tempfile.TemporaryDirectory(prefix="music-analyzer-deploy-test-") as directory:
        root = Path(directory)
        portable = root / "portable"
        portable.mkdir()
        (portable / "MusicAnalyzer.exe").write_bytes(b"signed-exe")
        (portable / "MusicAnalyzer.log").write_bytes(b"runtime-log")
        certificate = root / "music-analyzer-local-dev.crt"
        trust_script = root / "trust_music_analyzer.ps1"
        certificate.write_bytes(b"public-certificate")
        trust_script.write_bytes(b"trust-script")

        module.SOURCE_ROOT = portable
        module.CERTIFICATE = certificate
        module.TRUST_SCRIPT = trust_script

        selected = module.source_files()
        if [path.name for path in selected] != ["MusicAnalyzer.exe"]:
            raise AssertionError(f"deployment source selection changed: {selected}")
        deployed = module.deployment_files()
        if [path.name for path in deployed] != [
            "MusicAnalyzer.exe",
            certificate.name,
            trust_script.name,
        ]:
            raise AssertionError(f"deployment file set changed: {deployed}")

        commands: list[str] = []

        def fake_command(share, credentials, command):
            del share, credentials
            commands.append(command)
            return subprocess.CompletedProcess([], 0, "", "")

        module.smb_command = fake_command
        module.smb_put("//server/shared", root / "credentials", selected[0], "MusicAnalyzer.exe")
        if commands != [
            f'put "{selected[0].resolve()}" ".MusicAnalyzer.exe.music-analyzer-deploying"',
            'rename ".MusicAnalyzer.exe.music-analyzer-deploying" "MusicAnalyzer.exe"',
        ]:
            raise AssertionError(f"SMB upload was not atomic: {commands}")

        def fake_get(share, credentials, remote_name, local_path):
            del share, credentials
            shutil.copy2({path.name: path for path in deployed}[remote_name], local_path)

        module.smb_get = fake_get
        with tempfile.TemporaryDirectory(prefix="music-analyzer-deploy-verify-") as verify_dir:
            for path in deployed:
                mismatch = module.compare_downloaded(
                    path, "//server/shared", root / "credentials", Path(verify_dir)
                )
                if mismatch is not None:
                    raise AssertionError(mismatch)

    print("Windows signed deployment SMB fallback: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
