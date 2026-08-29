#!/usr/bin/env bash
# Download the official NSynth test JSON/WAV archive outside the repository.
set -euo pipefail

mode="${1:-plan}"
fixture_root="${MUSIC_ANALYZER_FIXTURE_CACHE:-/media/kyz/sshflashtor/InstrumentSamples}"
archive="${fixture_root}/nsynth-test.jsonwav.tar.gz"
dataset_dir="${fixture_root}/nsynth-test"
link_path="build/nsynth_test_samples"
# Magenta's historic HTTPS hostname currently serves a mismatched certificate,
# so use a public mirror of the unchanged test archive by default. Callers can
# override this with a future canonical endpoint without changing the workflow.
url="${MUSIC_ANALYZER_NSYNTH_TEST_URL:-https://huggingface.co/datasets/confit/nsynth/resolve/main/nsynth-test.jsonwav.tar.gz?download=true}"

case "${mode}" in
plan)
  printf 'fixture-root=%s\n' "${fixture_root}"
  printf 'archive=%s\n' "${archive}"
  printf 'dataset=%s\n' "${dataset_dir}"
  printf 'symlink=%s\n' "${link_path}"
  printf 'url=%s\n' "${url}"
  ;;
apply)
  mkdir -p "${fixture_root}"
  if [ ! -d "${dataset_dir}/audio" ] || [ ! -f "${dataset_dir}/examples.json" ]; then
    curl --fail --location --continue-at - --output "${archive}" "${url}"
    tar -xzf "${archive}" -C "${fixture_root}"
  fi
  ln -sfn "${dataset_dir}" "${link_path}"
  ;;
verify)
  test -d "${dataset_dir}/audio"
  test -f "${dataset_dir}/examples.json"
  test -L "${link_path}"
  test "$(readlink "${link_path}")" = "${dataset_dir}"
  ;;
*)
  printf 'usage: %s [plan|apply|verify]\n' "$0" >&2
  exit 2
  ;;
esac
