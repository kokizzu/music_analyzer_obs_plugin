#!/usr/bin/env python3
import os
import sys
import wave


AUDIO_EXTENSIONS = (".wav", ".wave", ".flac", ".mp3", ".m4a", ".ogg")
MIDI_EXTENSIONS = (".mid", ".midi")
MUSICXML_EXTENSIONS = (".musicxml", ".xml", ".mxl")
CHORALSYNTH_CHILD_NAMES = (
    "ChoralSynth",
    "choralsynth",
    "MTG-ChoralSynth",
    "ChoralSynth-main",
    "ChoralSynth-master",
)


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


def join_path(lhs, *children):
    path = lhs
    for child in children:
        path = os.path.join(path, child)
    return path


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_CHORALSYNTH_ROOT") or os.environ.get("CHORALSYNTH_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in CHORALSYNTH_CHILD_NAMES:
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


def is_musicxml(path):
    return lower_name(path).endswith(MUSICXML_EXTENSIONS)


def walk_files(path):
    for current, _, files in os.walk(path):
        for filename in files:
            yield join_path(current, filename)


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
    name = lower_name(path)
    if name.endswith(".flac"):
        return read_flac_summary(path)
    if name.endswith((".wav", ".wave")):
        return read_wav_summary(path)
    return None


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


def find_score_midi(path):
    for name in ("score.midi", "score.mid"):
        candidate = join_path(path, name)
        if os.path.isfile(candidate):
            return candidate
    midi_files = sorted(item for item in walk_files(path) if is_midi(item))
    return midi_files[0] if midi_files else ""


def find_musicxml(path):
    for name in ("score.musicxml", "score.xml", "score.mxl"):
        candidate = join_path(path, name)
        if os.path.isfile(candidate):
            return candidate
    musicxml_files = sorted(item for item in walk_files(path) if is_musicxml(item))
    return musicxml_files[0] if musicxml_files else ""


def find_voice_audio(path):
    voices_dir = join_path(path, "voices")
    if os.path.isdir(voices_dir):
        return sorted(item for item in walk_files(voices_dir) if is_audio(item))
    return sorted(item for item in walk_files(path) if is_audio(item))


def candidate_piece_dirs(root):
    pieces = []
    for child in direct_child_dirs(root):
        if find_score_midi(child) or os.path.isdir(join_path(child, "voices")):
            pieces.append(child)
    if pieces:
        return pieces
    return [root] if find_score_midi(root) or os.path.isdir(join_path(root, "voices")) else []


def inspect_piece_dir(path, min_voices, min_audio_seconds):
    score_midi = find_score_midi(path)
    musicxml = find_musicxml(path)
    voice_audio = find_voice_audio(path)
    readable_midi = bool(score_midi) and midi_header_is_readable(score_midi)
    audio_summaries = []
    compressed_voice_count = 0
    unreadable_audio = []
    for audio in voice_audio:
        summary = audio_summary(audio)
        if summary:
            audio_summaries.append(summary)
        elif lower_name(audio).endswith((".mp3", ".m4a", ".ogg")):
            compressed_voice_count += 1
        else:
            unreadable_audio.append(audio)

    short_audio = [summary for summary in audio_summaries if summary["duration"] < min_audio_seconds]
    complete = (
        bool(musicxml)
        and readable_midi
        and len(voice_audio) >= min_voices
        and not unreadable_audio
        and not short_audio
    )

    return {
        "path": path,
        "complete": complete,
        "score_midi": score_midi,
        "musicxml": musicxml,
        "readable_midi": readable_midi,
        "voice_count": len(voice_audio),
        "compressed_voice_count": compressed_voice_count,
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
            "inspect_choralsynth_dataset: set MUSIC_ANALYZER_CHORALSYNTH_ROOT, CHORALSYNTH_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_choralsynth_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_pieces = positive_int_env("MUSIC_ANALYZER_CHORALSYNTH_REQUIRED_PIECES", 20)
    min_voices = positive_int_env("MUSIC_ANALYZER_CHORALSYNTH_MIN_VOICES", 4)
    min_audio_seconds = positive_float_env("MUSIC_ANALYZER_CHORALSYNTH_MIN_AUDIO_SECONDS", 1.0)

    inspected = [inspect_piece_dir(path, min_voices, min_audio_seconds) for path in candidate_piece_dirs(root)]
    complete = [piece for piece in inspected if piece["complete"]]
    voice_counts = [piece["voice_count"] for piece in complete]
    compressed_voice_counts = [piece["compressed_voice_count"] for piece in complete]
    durations = [summary["duration"] for piece in complete for summary in piece["audio_summaries"]]
    channels = [summary["channels"] for piece in complete for summary in piece["audio_summaries"]]
    sample_rate_counts = [
        len({summary["sample_rate"] for summary in piece["audio_summaries"]}) for piece in complete
    ]

    print(
        "inspect_choralsynth_dataset: "
        f"root={root} discovered_pieces={len(inspected)} complete_pieces={len(complete)} "
        f"{range_summary(voice_counts, 'voices per piece')} "
        f"{range_summary(compressed_voice_counts, 'compressed voices per piece')} "
        f"{range_summary(channels, 'channels')} "
        f"{range_summary(sample_rate_counts, 'sample-rate variants per piece')} "
        f"{float_range_summary(durations, 'readable audio seconds per voice')}"
    )

    if len(complete) < required_pieces:
        print(
            f"inspect_choralsynth_dataset: expected at least {required_pieces} complete pieces with "
            f"score.musicxml, readable score MIDI, {min_voices}+ voice audio files, and readable WAV/FLAC "
            f"voices of at least {min_audio_seconds:.2f}s when duration is available; got {len(complete)}",
            file=sys.stderr,
        )
        for piece in inspected[:10]:
            if piece["complete"]:
                continue
            print(
                f"inspect_choralsynth_dataset: incomplete {piece['path']} "
                f"musicxml={'yes' if piece['musicxml'] else 'no'} "
                f"midi={'yes' if piece['readable_midi'] else 'no'} "
                f"voices={piece['voice_count']} unreadable_audio={len(piece['unreadable_audio'])} "
                f"short_audio={len(piece['short_audio'])}",
                file=sys.stderr,
            )
        return 1

    print(
        "inspect_choralsynth_dataset: ChoralSynth gives 20 synthetic same-song choral voice tracks "
        "plus score MIDI truth; use it as synthesized vocal multitrack note/chord coverage, not as a "
        "replacement for the real-recorded URMP gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
