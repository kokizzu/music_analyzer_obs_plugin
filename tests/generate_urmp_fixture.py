#!/usr/bin/env python3
import math
import os
import shutil
import struct
import subprocess
import sys
import wave


SAMPLE_RATE = 48000
SECONDS = 4
PIECES = 20
FIXTURE_MARKER = ".music_analyzer_generated_urmp_fixture"
WINDOWS = (
    (0.20, 0.60, 0, False),
    (1.05, 0.60, 5, False),
    (1.90, 0.60, 9, True),
    (2.75, 0.60, 7, False),
)


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def midi_at_or_above(min_midi, pitch_class):
    return min_midi + ((pitch_class - min_midi % 12 + 12) % 12)


def harmonic_sample(midi, amp, index):
    value = 0.0
    for harmonic, scale in ((1, 1.0), (2, 0.42), (3, 0.22), (4, 0.12), (5, 0.06)):
        value += (
            amp
            * scale
            * math.sin(
                2.0
                * math.pi
                * midi_frequency(midi)
                * harmonic
                * index
                / SAMPLE_RATE
            )
        )
    return value


def write_wav(path, channels):
    frames = []
    for index in range(SAMPLE_RATE * SECONDS):
        value = sum(channel[index] for channel in channels)
        value = max(-0.95, min(0.95, value))
        frames.append(struct.pack("<h", int(value * 32767.0)))

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(b"".join(frames))


def write_flac(path, channels):
    temp_path = path + ".tmp.wav"
    write_wav(temp_path, channels)
    ffmpeg = os.environ.get("FFMPEG", "ffmpeg")
    try:
        subprocess.run(
            [
                ffmpeg,
                "-nostdin",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                temp_path,
                "-map_metadata",
                "-1",
                "-compression_level",
                "12",
                path,
            ],
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"{ffmpeg} is required to generate the FLAC fixture") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"{ffmpeg} failed while encoding {path}") from exc
    finally:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass


def write_var_len(value):
    bytes_out = [value & 0x7F]
    value >>= 7
    while value:
        bytes_out.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(bytes_out))


def write_score_midi(path, events):
    ticks_per_quarter = 480
    ticks_per_second = 960
    midi_events = []
    for onset, duration, midi in events:
        start_tick = int(round(onset * ticks_per_second))
        end_tick = int(round((onset + duration) * ticks_per_second))
        midi_events.append((start_tick, 1, midi))
        midi_events.append((end_tick, 0, midi))
    midi_events.sort()

    track = bytearray()
    last_tick = 0
    for tick, on, midi in midi_events:
        track.extend(write_var_len(tick - last_tick))
        last_tick = tick
        if on:
            track.extend((0x90, midi, 72))
        else:
            track.extend((0x80, midi, 0))
    track.extend(write_var_len(0))
    track.extend((0xFF, 0x2F, 0x00))

    with open(path, "wb") as midi_file:
        midi_file.write(b"MThd")
        midi_file.write(struct.pack(">IHHH", 6, 0, 1, ticks_per_quarter))
        midi_file.write(b"MTrk")
        midi_file.write(struct.pack(">I", len(track)))
        midi_file.write(track)


def write_piece(root, index):
    root_pitch_class = (index * 5) % 12
    instruments = ["vn", "va", "vc"]
    floors = [72, 67, 60]
    piece_name = f"{index:02d}_Fixture_vn_va_vc"
    piece_dir = os.path.join(root, piece_name)
    os.makedirs(piece_dir, exist_ok=True)

    parts = []
    score_events = []
    for track_index, (instrument, floor) in enumerate(zip(instruments, floors), start=1):
        channel = [0.0 for _ in range(SAMPLE_RATE * SECONDS)]
        note_rows = []
        for onset, duration, root_offset, minor in WINDOWS:
            intervals = [0, 3 if minor else 4, 7]
            midi = midi_at_or_above(
                floor, (root_pitch_class + root_offset + intervals[track_index - 1]) % 12
            )
            start = int(onset * SAMPLE_RATE)
            end = int((onset + duration) * SAMPLE_RATE)
            for sample_index in range(start, min(end, len(channel))):
                channel[sample_index] += harmonic_sample(midi, 0.13, sample_index)
            note_rows.append((onset, duration, midi))
            score_events.append((onset, duration, midi))
        parts.append(channel)

        write_flac(
            os.path.join(
                piece_dir,
                f"AuSep_{track_index}_{instrument}_{index:02d}_Fixture.flac",
            ),
            [channel],
        )
        with open(
            os.path.join(
                piece_dir,
                f"Notes_{track_index}_{instrument}_{index:02d}_Fixture.txt",
            ),
            "w",
            encoding="utf-8",
        ) as notes_file:
            for onset, duration, midi in note_rows:
                notes_file.write(f"{onset:.3f} {midi_frequency(midi):.6f} {duration:.3f}\n")

    write_flac(os.path.join(piece_dir, f"AuMix_{index:02d}_Fixture_vn_va_vc.flac"), parts)
    write_score_midi(os.path.join(piece_dir, f"Sco_{index:02d}_Fixture_vn_va_vc.mid"), score_events)


def main():
    if len(sys.argv) != 2:
        print("usage: generate_urmp_fixture.py OUTPUT_DIR", file=sys.stderr)
        return 2

    output_dir = sys.argv[1]
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)
    with open(os.path.join(output_dir, FIXTURE_MARKER), "w", encoding="utf-8") as marker:
        marker.write("generated by tests/generate_urmp_fixture.py\n")
    try:
        for index in range(1, PIECES + 1):
            write_piece(output_dir, index)
    except RuntimeError as exc:
        print(f"generate_urmp_fixture.py: {exc}", file=sys.stderr)
        return 1
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
