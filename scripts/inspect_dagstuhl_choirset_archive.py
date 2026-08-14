#!/usr/bin/env python3
"""Print a compact, deterministic Dagstuhl ChoirSet archive inventory."""

import argparse
import collections
import zipfile


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--contains", default="")
    parser.add_argument("--read", default="")
    args = parser.parse_args(argv)
    with zipfile.ZipFile(args.archive) as archive:
        files = sorted(info.filename for info in archive.infolist() if not info.is_dir())
        if args.read:
            with archive.open(args.read) as source:
                print(source.read().decode("utf-8", errors="replace"))
            return 0
    extensions = collections.Counter(name.rsplit(".", 1)[-1].lower() if "." in name else "(none)" for name in files)
    roots = collections.Counter(name.split("/", 1)[0] for name in files)
    print(f"inspect_dagstuhl_choirset_archive: files={len(files)}")
    print("roots=" + ", ".join(f"{name}={count}" for name, count in sorted(roots.items())))
    print("extensions=" + ", ".join(f"{name}={count}" for name, count in sorted(extensions.items())))
    selected = [name for name in files if args.contains.lower() in name.lower()]
    for name in selected[: max(0, args.limit)]:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
