#!/usr/bin/env bash
# Relocate large, reproducible sample/corpus directories out of build/ while
# retaining the paths consumed by the Makefile as symlinks.
set -euo pipefail

mode="${1:---dry-run}"
link_name=""
case "$mode" in
  --dry-run|--apply) ;;
  --ensure-link)
    link_name="${2:-}"
    if [[ -z "$link_name" || "$link_name" == */* || "$link_name" == "." || "$link_name" == ".." ]]; then
      echo "usage: $0 --ensure-link <build-directory-name>" >&2
      exit 2
    fi
    ;;
  *)
    echo "usage: $0 [--dry-run|--apply|--ensure-link <build-directory-name>]" >&2
    exit 2
    ;;
esac

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
build_dir="$repo_root/build"
storage_root="/media/kyz/sshflashtor/InstrumentSamples"

if [[ ! -d "$build_dir" ]]; then
  echo "error: missing build directory: $build_dir" >&2
  exit 1
fi

if [[ -e "$build_dir/InstrumentSamples" && ! -L "$build_dir/InstrumentSamples" ]]; then
  echo "error: build/InstrumentSamples must be a symlink before relocation" >&2
  exit 1
fi

# Prepare a single future output directory before a fixture generator runs.
# This keeps all generated audio outside the workspace from its first write,
# rather than briefly creating a local build/*_samples directory and moving it
# afterwards.
if [[ "$mode" == "--ensure-link" ]]; then
  source="$build_dir/$link_name"
  destination="$storage_root/$link_name"
  if [[ -L "$source" ]]; then
    resolved="$(readlink -f "$source")"
    if [[ "$resolved" != "$destination" ]]; then
      echo "error: build/$link_name points at $resolved (expected $destination)" >&2
      exit 1
    fi
    echo "LINKED    build/$link_name -> $resolved"
    exit 0
  fi
  if [[ -e "$source" ]]; then
    echo "error: build/$link_name already exists and is not a symlink" >&2
    exit 1
  fi
  mkdir -p "$destination"
  ln -s "$destination" "$source"
  echo "LINKED    build/$link_name -> $destination"
  exit 0
fi

matches=()
while IFS= read -r -d '' path; do
  [[ -d "$path" ]] || continue
  name="${path##*/}"
  # Android tooling is a build dependency, not corpus data.
  # Lock directories are short-lived build coordination state, not corpus data.
  [[ "$name" == "InstrumentSamples" || "$name" == "android-sdk" || "$name" == *.lock ]] && continue
  normalized="${name,,}"
  if [[ "$normalized" =~ (^|_)(sample|samples|corpus|dataset)(_|$) ]] || \
      find -L "$path" -type f \( -iname '*.wav' -o -iname '*.flac' -o -iname '*.mp3' -o -iname '*.ogg' -o -iname '*.opus' -o -iname '*.aif' -o -iname '*.aiff' -o -iname '*.m4a' \) -print -quit | grep -q .; then
    matches+=("$path")
  fi
done < <(find "$build_dir" -mindepth 1 -maxdepth 1 -print0 | sort -z)

if [[ -L "$build_dir/InstrumentSamples" ]]; then
  echo "ROOTLINK  build/InstrumentSamples -> $(readlink -f "$build_dir/InstrumentSamples")"
else
  echo "ROOTLINK  build/InstrumentSamples is absent"
fi

if (( ${#matches[@]} == 0 )); then
  echo "No direct build sample/corpus directories require relocation."
  exit 0
fi

for source in "${matches[@]}"; do
  name="${source##*/}"
  destination="$storage_root/$name"
  if [[ -L "$source" ]]; then
    resolved="$(readlink -f "$source")"
    if [[ "$resolved" == "$storage_root" || "$resolved" == "$storage_root/"* ]]; then
      echo "LINKED    build/$name -> $resolved"
    else
      echo "MISLINK   build/$name -> $resolved (expected $destination)"
    fi
    continue
  fi
  if [[ -e "$destination" || -L "$destination" ]]; then
    echo "CONFLICT  build/$name -> $destination (destination already exists)"
    continue
  fi
  if [[ "$mode" == "--dry-run" ]]; then
    echo "MOVE      build/$name -> $destination"
    echo "SYMLINK   build/$name -> $destination"
    continue
  fi
  mkdir -p "$storage_root"
  mv "$source" "$destination"
  ln -s "$destination" "$source"
  echo "MOVED     build/$name -> $destination"
done
