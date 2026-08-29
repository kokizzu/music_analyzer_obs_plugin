#!/usr/bin/env python3
"""Relocate generated audio fixture trees to the external fixture cache."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_CACHE = Path("/media/kyz/sshflashtor/InstrumentSamples/build-cache")
FIXTURES = (
    "idmt_bass_single_track_fixture",
    "mir1k_vocal_fixtures",
    "prepared-multitrack-musicnet-fixture",
)
BATCH_LIMIT = 24


def target_for(name: str) -> Path:
    return EXTERNAL_CACHE / name


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def inventory(path: Path) -> dict[str, tuple[int, str]]:
    return {
        str(item.relative_to(path)): (item.stat().st_size, file_digest(item))
        for item in sorted(path.rglob("*"))
        if item.is_file() and not item.name.endswith(".migrate-partial")
    }


def tree_difference(
    local: Path, external: Path
) -> tuple[list[str], list[str], list[str], dict[str, tuple[int, str]], dict[str, tuple[int, str]]]:
    local_inventory = inventory(local)
    external_inventory = inventory(external)
    local_only = sorted(set(local_inventory) - set(external_inventory))
    external_only = sorted(set(external_inventory) - set(local_inventory))
    changed = sorted(
        item
        for item in set(local_inventory) & set(external_inventory)
        if local_inventory[item] != external_inventory[item]
    )
    return local_only, external_only, changed, local_inventory, external_inventory


def compare_trees(local: Path, external: Path) -> str:
    local_only, external_only, changed, local_inventory, external_inventory = tree_difference(local, external)
    if not local_only and not external_only and not changed:
        return "identical"
    details = [
        f"local-files={len(local_inventory)}",
        f"external-files={len(external_inventory)}",
        f"local-only={','.join(local_only[:3]) or '-'}",
        f"external-only={','.join(external_only[:3]) or '-'}",
        f"changed={','.join(changed[:3]) or '-'}",
    ]
    return "different (" + "; ".join(details) + ")"


def copy_missing_batch(local: Path, external: Path) -> int:
    local_only, external_only, changed, _, _ = tree_difference(local, external)
    if external_only or changed:
        raise SystemExit("external tree diverged; refusing to resume copy")
    for relative in local_only[:BATCH_LIMIT]:
        source = local / relative
        destination = external / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".migrate-partial")
        if partial.exists():
            partial.unlink()
        shutil.copy2(source, partial)
        os.replace(partial, destination)
    return len(local_only)


def describe(name: str) -> tuple[Path, Path, str]:
    local = ROOT / "build" / name
    external = target_for(name)
    if local.is_symlink():
        resolved = local.resolve()
        if resolved == external:
            return local, external, "already linked"
        return local, external, f"unexpected symlink -> {resolved}"
    if not local.exists():
        if external.exists():
            return local, external, "link missing; external data present"
        return local, external, "no data yet"
    if external.exists():
        return local, external, f"both copies present: {compare_trees(local, external)}"
    return local, external, "move local data and create symlink"


def plan() -> int:
    print(f"external-cache={EXTERNAL_CACHE}")
    for name in FIXTURES:
        local, external, state = describe(name)
        print(f"{name}: {state}\n  local={local}\n  external={external}")
    return 0


def apply() -> int:
    if not EXTERNAL_CACHE.is_dir():
        raise SystemExit(f"external cache is unavailable: {EXTERNAL_CACHE}")
    for name in FIXTURES:
        local, external, state = describe(name)
        if state == "already linked":
            print(f"{name}: unchanged")
            continue
        if state == "no data yet":
            external.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(external, local)
            print(f"{name}: created empty-cache symlink")
            continue
        if state == "link missing; external data present":
            os.symlink(external, local)
            print(f"{name}: restored symlink")
            continue
        if state.startswith("both copies"):
            if state != "both copies present: identical":
                local_only, external_only, changed, _, _ = tree_difference(local, external)
                if external_only or changed:
                    raise SystemExit(f"{name}: {state}; resolve manually before migration")
                remaining = copy_missing_batch(local, external)
                copied = min(remaining, BATCH_LIMIT)
                print(f"{name}: resumed {copied} files; {remaining - copied} remain")
                continue
            shutil.rmtree(local)
            os.symlink(external, local)
            print(f"{name}: replaced identical local copy with symlink")
            continue
        if state.startswith("unexpected"):
            raise SystemExit(f"{name}: {state}; resolve manually before migration")

        external.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(local), str(external))
        os.symlink(external, local)
        print(f"{name}: moved and linked")
    return plan()


def verify() -> int:
    failed = False
    for name in FIXTURES:
        local, external, state = describe(name)
        print(f"{name}: {state}")
        if state != "already linked":
            failed = True
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply", "verify"))
    arguments = parser.parse_args()
    if arguments.mode == "plan":
        return plan()
    if arguments.mode == "apply":
        return apply()
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
