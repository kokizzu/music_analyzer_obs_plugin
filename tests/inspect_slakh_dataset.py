#!/usr/bin/env python3
import os
import sys
import wave


AUDIO_EXTENSIONS = (".wav", ".wave", ".flac")
MIDI_EXTENSIONS = (".mid", ".midi")
METADATA_NAMES = ("metadata.yaml", "metadata.yml")
SLAKH_CHILD_NAMES = (
    "Slakh2100_flac_redux",
    "slakh2100_flac_redux",
    "Slakh2100",
    "slakh2100",
    "Slakh",
    "slakh",
    "BabySlakh",
    "babyslakh",
    "baby_slakh",
    "baby-slakh",
)
SPLIT_NAMES = ("train", "validation", "valid", "test")
DEFAULT_REQUIRED_CLASSES = ("piano", "bass", "guitar", "drum")


def positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


def positive_float_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = float(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0.0 else fallback


def required_classes():
    value = os.environ.get("MUSIC_ANALYZER_SLAKH_REQUIRED_CLASSES", "")
    if not value:
        return DEFAULT_REQUIRED_CLASSES
    classes = [item.strip().lower() for item in value.replace(";", ",").split(",")]
    return tuple(item for item in classes if item)


def join_path(lhs, *children):
    path = lhs
    for child in children:
        path = os.path.join(path, child)
    return path


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_SLAKH_ROOT") or os.environ.get("SLAKH_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in SLAKH_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def lower_name(path):
    return os.path.basename(path).lower()


def is_audio(path):
    return lower_name(path).endswith(AUDIO_EXTENSIONS)


def is_midi(path):
    return lower_name(path).endswith(MIDI_EXTENSIONS)


def read_wav_summary(path):
    try:
        with wave.open(path, "rb") as audio:
            frames = audio.getnframes()
            sample_rate = audio.getframerate()
            return {
                "channels": audio.getnchannels(),
                "sample_rate": sample_rate,
                "frames": frames,
                "duration": frames / float(max(1, sample_rate)),
            }
    except (OSError, EOFError, wave.Error):
        return None


def read_flac_summary(path):
    try:
        with open(path, "rb") as audio:
            if audio.read(4) != b"fLaC":
                return None
            while True:
                header = audio.read(4)
                if len(header) != 4:
                    return None
                block_type = header[0] & 0x7F
                length = int.from_bytes(header[1:4], "big")
                data = audio.read(length)
                if len(data) != length:
                    return None
                if block_type == 0:
                    if length < 34:
                        return None
                    packed = int.from_bytes(data[10:18], "big")
                    sample_rate = (packed >> 44) & 0xFFFFF
                    channels = ((packed >> 41) & 0x7) + 1
                    total_samples = packed & 0xFFFFFFFFF
                    if sample_rate <= 0 or total_samples <= 0:
                        return None
                    return {
                        "channels": channels,
                        "sample_rate": sample_rate,
                        "frames": total_samples,
                        "duration": total_samples / float(sample_rate),
                    }
    except OSError:
        return None


def audio_summary(path):
    if lower_name(path).endswith(".flac"):
        return read_flac_summary(path)
    return read_wav_summary(path)


def midi_header_is_readable(path):
    try:
        with open(path, "rb") as midi:
            return midi.read(4) == b"MThd"
    except OSError:
        return False


def direct_child_dirs(path):
    try:
        children = sorted(os.scandir(path), key=lambda item: item.name)
    except OSError:
        return []
    return [entry.path for entry in children if entry.is_dir()]


def candidate_track_dirs(root):
    candidates = []
    for split in SPLIT_NAMES:
        split_dir = join_path(root, split)
        if not os.path.isdir(split_dir):
            continue
        candidates.extend(direct_child_dirs(split_dir))
    if candidates:
        return candidates
    return direct_child_dirs(root)


def walk_files(path):
    for current, _, files in os.walk(path):
        for filename in files:
            yield join_path(current, filename)


def find_metadata(path):
    for name in METADATA_NAMES:
        candidate = join_path(path, name)
        if os.path.isfile(candidate):
            return candidate
    return ""


def read_metadata_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as metadata:
            return metadata.read().lower()
    except OSError:
        return ""


def metadata_has_class(text, instrument_class):
    if instrument_class == "drum":
        return "drum" in text or "is_drum: true" in text or "is_drum: yes" in text
    return instrument_class in text


def find_audio_files(path):
    return [item for item in walk_files(path) if is_audio(item)]


def find_mix_audio(audio_files):
    for audio in audio_files:
        name = lower_name(audio)
        stem = os.path.splitext(name)[0]
        if stem in ("mix", "mixture", "all_src", "allsrc"):
            return audio
    return ""


def find_stem_audio(track_dir, audio_files, mix_audio):
    stems_dir = join_path(track_dir, "stems")
    if os.path.isdir(stems_dir):
        return [item for item in walk_files(stems_dir) if is_audio(item)]
    return [item for item in audio_files if item != mix_audio]


def find_midi_files(path):
    return [item for item in walk_files(path) if is_midi(item)]


def inspect_track_dir(path, min_stems, min_audio_seconds, required):
    metadata = find_metadata(path)
    metadata_text = read_metadata_text(metadata) if metadata else ""
    present_classes = [item for item in required if metadata_has_class(metadata_text, item)]
    audio_files = find_audio_files(path)
    mix_audio = find_mix_audio(audio_files)
    stem_audio = find_stem_audio(path, audio_files, mix_audio)
    midi_files = find_midi_files(path)
    readable_midi = [item for item in midi_files if midi_header_is_readable(item)]
    audio_summaries = []
    unreadable_audio = []
    for audio in [mix_audio] + stem_audio:
        if not audio:
            continue
        summary = audio_summary(audio)
        if summary:
            audio_summaries.append(summary)
        else:
            unreadable_audio.append(audio)

    short_audio = [summary for summary in audio_summaries if summary["duration"] < min_audio_seconds]
    missing_classes = [item for item in required if item not in present_classes]
    complete = (
        bool(metadata)
        and not missing_classes
        and bool(mix_audio)
        and len(stem_audio) >= min_stems
        and bool(readable_midi)
        and not unreadable_audio
        and not short_audio
    )

    return {
        "path": path,
        "complete": complete,
        "metadata": metadata,
        "missing_classes": missing_classes,
        "mix_audio": mix_audio,
        "stem_count": len(stem_audio),
        "midi_count": len(readable_midi),
        "audio_summaries": audio_summaries,
        "unreadable_audio": unreadable_audio,
        "short_audio": short_audio,
    }


def range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0/0.00/0"
    return f"{label} min/avg/max {min(values)}/{sum(values) / len(values):.2f}/{max(values)}"


def float_range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0.00/0.00/0.00"
    return f"{label} min/avg/max {min(values):.2f}/{sum(values) / len(values):.2f}/{max(values):.2f}"


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_slakh_dataset: set MUSIC_ANALYZER_SLAKH_ROOT, SLAKH_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_slakh_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_tracks = positive_int_env("MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS", 20)
    min_stems = positive_int_env("MUSIC_ANALYZER_SLAKH_MIN_STEMS", 4)
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_SLAKH_MIN_AUDIO_SECONDS", 1.0)
    required = required_classes()

    inspected = [inspect_track_dir(path, min_stems, min_audio_seconds, required) for path in candidate_track_dirs(root)]
    complete = [track for track in inspected if track["complete"]]
    stem_counts = [track["stem_count"] for track in complete]
    midi_counts = [track["midi_count"] for track in complete]
    durations = [summary["duration"] for track in complete for summary in track["audio_summaries"]]
    channels = [summary["channels"] for track in complete for summary in track["audio_summaries"]]
    sample_rate_counts = [
        len({summary["sample_rate"] for summary in track["audio_summaries"]}) for track in complete
    ]

    print(
        "inspect_slakh_dataset: "
        f"root={root} discovered_tracks={len(inspected)} complete_tracks={len(complete)} "
        f"required_classes={','.join(required)} "
        f"{range_summary(stem_counts, 'stems per track')} "
        f"{range_summary(midi_counts, 'readable MIDI files per track')} "
        f"{range_summary(channels, 'channels')} "
        f"{range_summary(sample_rate_counts, 'sample-rate variants per track')} "
        f"{float_range_summary(durations, 'audio seconds per file')}"
    )

    if len(complete) < required_tracks:
        print(
            f"inspect_slakh_dataset: expected at least {required_tracks} complete tracks with mix audio, "
            f"{min_stems}+ stem audio files, readable MIDI, metadata classes {','.join(required)}, "
            f"and audio of at least {min_audio_seconds:.2f}s; got {len(complete)}",
            file=sys.stderr,
        )
        for track in inspected[:10]:
            if track["complete"]:
                continue
            missing = ",".join(track["missing_classes"]) if track["missing_classes"] else "-"
            mix = "yes" if track["mix_audio"] else "no"
            metadata = "yes" if track["metadata"] else "no"
            print(
                f"inspect_slakh_dataset: incomplete {track['path']} metadata={metadata} "
                f"mix={mix} stems={track['stem_count']} midi={track['midi_count']} "
                f"missing_classes={missing} unreadable_audio={len(track['unreadable_audio'])} "
                f"short_audio={len(track['short_audio'])}",
                file=sys.stderr,
            )
        return 1

    print(
        "inspect_slakh_dataset: Slakh2100 gives 20+ same-song rendered stems plus MIDI truth; "
        "use it as synthesized multitrack note/chord coverage, not as a replacement for the "
        "real-recorded URMP gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
