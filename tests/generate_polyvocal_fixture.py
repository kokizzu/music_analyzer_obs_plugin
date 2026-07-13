#!/usr/bin/env python3
import csv
import json
import math
import os
import struct
import sys
import wave


SAMPLE_RATE = 44100
PIECE_COUNT = 20
VOICE_NAMES = ("soprano", "alto", "tenor", "bass")
SEGMENT_SECONDS = 0.55
GAP_SECONDS = 0.10

PROGRESSIONS = (
    (("C", (72, 67, 60, 48)), ("F", (72, 65, 60, 53)), ("G7", (71, 67, 62, 55)), ("C", (72, 64, 60, 48))),
    (("Am", (72, 69, 64, 57)), ("Dm", (74, 69, 62, 50)), ("G", (74, 67, 62, 55)), ("C", (72, 67, 64, 48))),
    (("F", (77, 69, 65, 53)), ("Bb", (77, 70, 65, 58)), ("C7", (76, 70, 64, 48)), ("F", (77, 69, 65, 53))),
    (("G", (74, 67, 62, 55)), ("Em", (76, 67, 64, 52)), ("C", (76, 67, 60, 48)), ("D7", (78, 66, 62, 50))),
)


def join_path(lhs, *children):
    path = lhs
    for child in children:
        path = os.path.join(path, child)
    return path


def midi_hz(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in samples:
            frames.extend(struct.pack("<h", int(max(-0.95, min(0.95, sample)) * 32767.0)))
        audio.writeframes(bytes(frames))


def voice_samples(piece_index, voice_index):
    progression = PROGRESSIONS[piece_index % len(PROGRESSIONS)]
    total_seconds = len(progression) * (SEGMENT_SECONDS + GAP_SECONDS) + 0.2
    frame_count = int(round(total_seconds * SAMPLE_RATE))
    samples = [0.0] * frame_count
    phase = 0.0
    amplitude = 0.20 - voice_index * 0.018
    for segment_index, (_, notes) in enumerate(progression):
        start = int(round((0.1 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS)) * SAMPLE_RATE))
        end = int(round((0.1 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS) + SEGMENT_SECONDS) * SAMPLE_RATE))
        freq = midi_hz(notes[voice_index])
        phase_step = 2.0 * math.pi * freq / SAMPLE_RATE
        for frame in range(start, min(end, frame_count)):
            age = frame - start
            remaining = end - frame
            attack = min(1.0, age / float(max(1, int(0.025 * SAMPLE_RATE))))
            release = min(1.0, remaining / float(max(1, int(0.040 * SAMPLE_RATE))))
            envelope = min(attack, release)
            samples[frame] = math.sin(phase) * amplitude * envelope
            phase += phase_step
    return samples


def mix_voices(voices):
    frame_count = max(len(samples) for samples in voices)
    mixed = []
    gain = 1.0 / math.sqrt(len(voices))
    for frame in range(frame_count):
        sample = 0.0
        for voice in voices:
            if frame < len(voice):
                sample += voice[frame]
        mixed.append(sample * gain)
    return mixed


def write_f0_csv(path, piece_index, voice_index):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    progression = PROGRESSIONS[piece_index % len(PROGRESSIONS)]
    with open(path, "w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["time", "frequency"])
        for segment_index, (_, notes) in enumerate(progression):
            start = 0.1 + segment_index * (SEGMENT_SECONDS + GAP_SECONDS)
            freq = midi_hz(notes[voice_index])
            frame = 0
            while True:
                time_value = start + frame * 0.05
                if time_value > start + SEGMENT_SECONDS - 0.025:
                    break
                writer.writerow([f"{time_value:.3f}", f"{freq:.6f}"])
                frame += 1


def main(argv):
    if len(argv) != 2:
        print("usage: generate_polyvocal_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = argv[1]
    audio_dir = join_path(root, "audiomixtures")
    source_audio_dir = join_path(root, "voice_audio")
    annotation_dir = join_path(root, "annotations")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(source_audio_dir, exist_ok=True)
    os.makedirs(annotation_dir, exist_ok=True)

    mtracks = {}
    for piece in range(1, PIECE_COUNT + 1):
        base = f"PV{piece:03d}_satb.wav"
        voices = []
        source_audio_files = []
        annotation_files = []
        for voice_index, voice_name in enumerate(VOICE_NAMES):
            voice = voice_samples(piece - 1, voice_index)
            voices.append(voice)
            source_audio_name = f"PV{piece:03d}_{voice_name}.wav"
            source_audio_files.append(source_audio_name)
            write_wav(join_path(source_audio_dir, source_audio_name), voice)
            annotation_name = f"PV{piece:03d}_{voice_name}.csv"
            annotation_files.append(annotation_name)
            write_f0_csv(join_path(annotation_dir, annotation_name), piece - 1, voice_index)
        write_wav(join_path(audio_dir, base), mix_voices(voices))
        mtracks[base] = {
            "audiopath": "audiomixtures",
            "source_audio_folder": "voice_audio",
            "source_audio_files": source_audio_files,
            "annot_folder": "annotations",
            "annot_files": annotation_files,
            "source": "generated-polyvocal-fixture",
        }

    with open(join_path(root, "mtracks_info.json"), "w", encoding="utf-8") as output:
        json.dump(mtracks, output, indent=2, sort_keys=True)

    print(f"generate_polyvocal_fixture: wrote {PIECE_COUNT} vocal ensemble mixes to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
