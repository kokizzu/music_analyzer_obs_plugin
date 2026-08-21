#!/bin/sh
# Download the isolated Rimshot source, verify the observed delivered checksum,
# and make a local WAV fixture without adding samples to the repository.
set -eu

if [ "$#" -ne 4 ]; then
    printf '%s\n' "download_pixabay_rimshot_candidate: usage: MP3 WAV URL SHA256" >&2
    exit 2
fi

mp3_path=$1
wav_path=$2
download_url=$3
expected_sha256=$4
case "$download_url" in
    https://cdn.pixabay.com/download/audio/2022/03/26/audio_98d9528d9c.mp3\?filename=freesound_community-rimshot-sweet-107111.mp3) ;;
    *)
        printf '%s\n' "download_pixabay_rimshot_candidate: refusing unverified URL=$download_url" >&2
        exit 1
        ;;
esac

mkdir -p "$(dirname "$mp3_path")" "$(dirname "$wav_path")"
if [ ! -s "$mp3_path" ] || ! printf '%s  %s\n' "$expected_sha256" "$mp3_path" | sha256sum -c - >/dev/null 2>&1; then
    partial_path="$mp3_path.part"
    curl -fL -C - -o "$partial_path" "$download_url"
    printf '%s  %s\n' "$expected_sha256" "$partial_path" | sha256sum -c -
    mv "$partial_path" "$mp3_path"
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
    printf '%s\n' "download_pixabay_rimshot_candidate: ffmpeg is required to create the WAV fixture" >&2
    exit 2
fi
temporary_wav="$wav_path.part.wav"
ffmpeg -nostdin -loglevel error -y -i "$mp3_path" -ac 1 -ar 48000 -c:a pcm_s16le "$temporary_wav"
mv "$temporary_wav" "$wav_path"
fixture_dir=$(dirname "$mp3_path")
manifest="$fixture_dir/manifest.tsv"
temporary_manifest="$manifest.part"
printf '%s\n' 'category	path	duration_seconds	source' > "$temporary_manifest"
printf 'rim\trim/%s\t1.072\tPixabay/Sajmund-Freesound-Rimshot-sweet\n' "$(basename "$wav_path")" >> "$temporary_manifest"
mv "$temporary_manifest" "$manifest"
printf '%s\n' "download_pixabay_rimshot_candidate: verified $mp3_path and created $wav_path"
