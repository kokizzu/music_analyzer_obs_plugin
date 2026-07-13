#!/usr/bin/env python3
import os
import shutil
import struct
import subprocess
import sys
import wave

import inspect_choralsynth_dataset
from prepare_slakh_musicnet_fixture import parse_midi_notes, write_labels


DEFAULT_OUTPUT_SAMPLE_RATE = 44100


def wav_audio(path):
    return inspect_choralsynth_dataset.lower_name(path).endswith((".wav", ".wave"))


def read_wav_samples(path):
    try:
        with wave.open(path, "rb") as audio:
            if audio.getsampwidth() != 2:
                return None
            sample_rate = audio.getframerate()
            channels = audio.getnchannels()
            frame_count = audio.getnframes()
            data = audio.readframes(frame_count)
    except (OSError, EOFError, wave.Error):
        return None

    samples = []
    stride = channels * 2
    for offset in range(0, len(data), stride):
        total = 0.0
        for channel in range(channels):
            sample_offset = offset + channel * 2
            if sample_offset + 2 > len(data):
                break
            value = struct.unpack_from("<h", data, sample_offset)[0]
            total += value / 32768.0
        samples.append(total / float(max(1, channels)))
    return sample_rate, samples


def write_wav_samples(path, samples, sample_rate):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    frames = bytearray()
    for sample in samples:
        frames.extend(struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767.0)))
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(bytes(frames))


def mix_wav_voices(voice_audio, output_path):
    decoded = []
    sample_rate = 0
    for path in voice_audio:
        result = read_wav_samples(path)
        if not result:
            return 0
        current_rate, samples = result
        if sample_rate and current_rate != sample_rate:
            return 0
        sample_rate = current_rate
        decoded.append(samples)

    if not decoded:
        return 0

    frame_count = max(len(samples) for samples in decoded)
    mixed = []
    for index in range(frame_count):
        sample = 0.0
        for voice in decoded:
            if index < len(voice):
                sample += voice[index]
        mixed.append(max(-0.95, min(0.95, sample)))
    write_wav_samples(output_path, mixed, sample_rate)
    return sample_rate


def mix_with_ffmpeg(voice_audio, output_path, ffmpeg):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    command = [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
    for audio in voice_audio:
        command.extend(["-i", audio])
    command.extend(
        [
            "-filter_complex",
            f"amix=inputs={len(voice_audio)}:duration=longest:normalize=1",
            "-ac",
            "1",
            "-ar",
            str(DEFAULT_OUTPUT_SAMPLE_RATE),
            output_path,
        ]
    )
    subprocess.check_call(command)
    return DEFAULT_OUTPUT_SAMPLE_RATE


def prepare_audio(voice_audio, output_path, ffmpeg):
    if all(wav_audio(path) for path in voice_audio):
        sample_rate = mix_wav_voices(voice_audio, output_path)
        if sample_rate:
            return sample_rate
    return mix_with_ffmpeg(voice_audio, output_path, ffmpeg)


def prepare_piece(piece, output_root, output_id, ffmpeg):
    voice_audio = inspect_choralsynth_dataset.find_voice_audio(piece["path"])
    if len(voice_audio) < 2:
        return False, "missing voice audio"

    score_midi = piece["score_midi"]
    try:
        notes = parse_midi_notes(score_midi, 64, track_stride=16)
    except ValueError as exc:
        return False, f"{score_midi}: {exc}"
    if not notes:
        return False, "no usable score MIDI notes"

    audio_out = inspect_choralsynth_dataset.join_path(output_root, "train_data", f"{output_id}.wav")
    label_out = inspect_choralsynth_dataset.join_path(output_root, "train_labels", f"{output_id}.csv")
    sample_rate = prepare_audio(voice_audio, audio_out, ffmpeg)
    write_labels(label_out, notes, sample_rate)
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_choralsynth_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = inspect_choralsynth_dataset.resolve_root()
    if not root:
        print(
            "prepare_choralsynth_musicnet_fixture: set MUSIC_ANALYZER_CHORALSYNTH_ROOT, "
            "CHORALSYNTH_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_choralsynth_musicnet_fixture: `{root}` is not a directory", file=sys.stderr)
        return 1

    output_root = argv[1]
    required_pieces = inspect_choralsynth_dataset.positive_int_env("MUSIC_ANALYZER_CHORALSYNTH_REQUIRED_PIECES", 20)
    prepare_pieces = inspect_choralsynth_dataset.positive_int_env(
        "MUSIC_ANALYZER_CHORALSYNTH_PREPARE_PIECES", required_pieces
    )
    min_voices = inspect_choralsynth_dataset.positive_int_env("MUSIC_ANALYZER_CHORALSYNTH_MIN_VOICES", 4)
    min_audio_seconds = inspect_choralsynth_dataset.positive_float_env(
        "MUSIC_ANALYZER_CHORALSYNTH_MIN_AUDIO_SECONDS", 1.0
    )
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_CHORALSYNTH_FFMPEG") or "ffmpeg"

    inspected = [
        inspect_choralsynth_dataset.inspect_piece_dir(path, min_voices, min_audio_seconds)
        for path in inspect_choralsynth_dataset.candidate_piece_dirs(root)
    ]
    complete = [piece for piece in inspected if piece["complete"]]
    if len(complete) < required_pieces:
        print(
            f"prepare_choralsynth_musicnet_fixture: expected at least {required_pieces} complete "
            f"ChoralSynth pieces, got {len(complete)}",
            file=sys.stderr,
        )
        return 1

    shutil.rmtree(output_root, ignore_errors=True)
    prepared = 0
    failures = []
    for piece in complete:
        if prepared >= prepare_pieces:
            break
        ok, error = prepare_piece(piece, output_root, prepared + 1, ffmpeg)
        if ok:
            prepared += 1
        else:
            failures.append(f"{piece['path']}: {error}")

    if prepared < required_pieces:
        print(
            f"prepare_choralsynth_musicnet_fixture: expected to prepare {required_pieces} "
            f"ChoralSynth pieces, prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_choralsynth_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_choralsynth_musicnet_fixture: wrote {prepared} MusicNet-shaped "
        f"ChoralSynth recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
