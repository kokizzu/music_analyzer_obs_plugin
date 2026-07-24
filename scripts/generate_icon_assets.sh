#!/bin/sh
set -eu

if [ "$#" -gt 2 ]; then
	printf '%s\n' 'usage: generate_icon_assets.sh [complete-source.png] [bass-guitar-source.png]' >&2
	exit 2
fi

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
complete_source=${1:-"$root/assets/music-analyzer-icon.png"}
bass_guitar_source=${2:-"$root/assets/music-analyzer-bass-guitar-icon.png"}
complete_master="$root/assets/music-analyzer-icon.png"
bass_guitar_master="$root/assets/music-analyzer-bass-guitar-icon.png"
complete_header="$root/src/app_icon_rgba.hpp"
bass_guitar_header="$root/src/app_icon_bass_guitar_rgba.hpp"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

for source_image in "$complete_source" "$bass_guitar_source"; do
	if [ ! -f "$source_image" ]; then
		printf 'icon source not found: %s\n' "$source_image" >&2
		exit 1
	fi
done

mkdir -p "$root/assets"
convert "$complete_source" -auto-orient -resize '1024x1024^' -gravity center \
	-extent 1024x1024 -strip "PNG32:$tmp_dir/complete-master.png"
mv "$tmp_dir/complete-master.png" "$complete_master"
convert "$bass_guitar_source" -auto-orient -resize '1024x1024^' -gravity center \
	-extent 1024x1024 -strip "PNG32:$tmp_dir/bass-guitar-master.png"
mv "$tmp_dir/bass-guitar-master.png" "$bass_guitar_master"

generate_launcher_icons() {
	launcher_master=$1
	launcher_source_set=$2
	for entry in mdpi:48 hdpi:72 xhdpi:96 xxhdpi:144 xxxhdpi:192; do
		density=${entry%%:*}
		size=${entry##*:}
		destination="$root/android/app/src/$launcher_source_set/res/mipmap-$density/ic_launcher.png"
		mkdir -p "$(dirname -- "$destination")"
		convert "$launcher_master" -filter Lanczos -resize "${size}x${size}" -strip "PNG32:$destination"
	done
}

generate_header() {
	header_master=$1
	header_rgba=$2
	header_output=$3
	convert "$header_master" -filter Lanczos -resize '64x64' -depth 8 "RGBA:$header_rgba"
	byte_count=$(wc -c < "$header_rgba" | tr -d ' ')
	if [ "$byte_count" -ne 16384 ]; then
		printf 'unexpected standalone icon byte count: %s\n' "$byte_count" >&2
		exit 1
	fi

	{
		printf '%s\n' '#pragma once' '' '#include <array>' '#include <cstdint>' '' 'namespace mao::generated {' ''
		printf '%s\n' 'inline constexpr int kAppIconWidth = 64;' 'inline constexpr int kAppIconHeight = 64;'
		printf '%s\n' 'inline constexpr std::array<std::uint8_t, 16384> kAppIconRgba = {'
		od -An -v -t u1 "$header_rgba" | awk '
		{
			for (i = 1; i <= NF; ++i) {
				if (column == 0)
					printf "\t";
				printf "%s,", $i;
				column++;
				if (column == 24) {
					printf "\n";
					column = 0;
				} else {
					printf " ";
				}
			}
		}
		END {
			if (column != 0)
				printf "\n";
		}'
		printf '%s\n' '};' '' '} // namespace mao::generated'
	} > "$header_output"
	sed -i 's/[[:space:]]*$//' "$header_output"
}

generate_launcher_icons "$complete_master" main
generate_launcher_icons "$bass_guitar_master" bassGuitar
generate_header "$complete_master" "$tmp_dir/complete-icon.rgba" "$tmp_dir/app_icon_rgba.hpp"
generate_header "$bass_guitar_master" "$tmp_dir/bass-guitar-icon.rgba" "$tmp_dir/app_icon_bass_guitar_rgba.hpp"
mv "$tmp_dir/app_icon_rgba.hpp" "$complete_header"
mv "$tmp_dir/app_icon_bass_guitar_rgba.hpp" "$bass_guitar_header"

printf 'generated complete icon assets from %s\n' "$complete_source"
printf 'generated bass-guitar icon assets from %s\n' "$bass_guitar_source"
