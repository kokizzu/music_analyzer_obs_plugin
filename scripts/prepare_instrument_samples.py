#!/usr/bin/env python3

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys


SAMPLE_RATE = 48000
TICKS_PER_QUARTER = 480
TEMPO_US_PER_QUARTER = 500000
TICKS_PER_SECOND = TICKS_PER_QUARTER * 1000000 // TEMPO_US_PER_QUARTER

DEFAULT_SYSTEM_SOUNDFONTS = (
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/sounds/sf2/TimGM6mb.sf2",
    "/usr/share/sounds/sf2/default-GM.sf2",
)

FIXTURE_VERSION = "instrument-samples-v8-1000-per-family"

PIANO_NOTES = (24, 28, 31, 36, 40, 43, 48, 52, 55, 60, 64, 67, 72, 76, 79, 84)
GUITAR_NOTES = (40, 43, 45, 47, 52, 55, 59, 60, 64, 67, 71, 76, 79, 83, 88)
BASS_NOTES = (28, 31, 35, 36, 40, 43, 47, 48, 52, 55, 59, 60, 64)
SYNTH_NOTES = (36, 43, 48, 55, 60, 67, 72, 79)
STRING_NOTES = (36, 40, 43, 48, 52, 55, 60, 64, 67, 72, 76, 79)
VOCAL_NOTES = (55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76)
INSTRUMENT_VELOCITY_VARIANTS = (64, 76, 88, 100, 112)
INSTRUMENT_DURATION_VARIANTS = (0.9, 1.1, 1.4, 1.7)

# These FluidR3 GM cells are not reliable one-note pitch references. They are
# deliberately excluded from the one-note manifests rather than hidden in tests.
ONE_NOTE_EXCLUSIONS = {
    ("guitar", 28, 88): "FluidR3 muted guitar E6 renders mostly muted/noise energy with almost no E6 partial",
    ("synth", 86, None): "GM fifths_lead is a layered root+fifth patch, not a one-note source",
}

FAMILIES = {
    "piano": {
        "programs": ((0, "acoustic_grand"), (1, "bright_acoustic"), (2, "electric_grand"),
                     (3, "honky_tonk"), (4, "electric_piano_1"), (5, "electric_piano_2"),
                     (6, "harpsichord"), (7, "clavinet")),
        "notes": PIANO_NOTES,
        "channel": 0,
    },
    "guitar": {
        "programs": ((24, "nylon_guitar"), (25, "steel_guitar"), (26, "jazz_guitar"),
                     (27, "clean_guitar"), (28, "muted_guitar"), (29, "overdrive_guitar"),
                     (30, "distortion_guitar")),
        "notes": GUITAR_NOTES,
        "channel": 0,
    },
    "bass": {
        "programs": ((32, "acoustic_bass"), (33, "finger_bass"), (34, "pick_bass"),
                     (35, "fretless_bass"), (36, "slap_bass_1"), (37, "slap_bass_2"),
                     (38, "synth_bass_1"), (39, "synth_bass_2")),
        "notes": BASS_NOTES,
        "program_notes": {
            34: (31, 35, 36, 40, 43, 47, 48, 52, 55, 59, 60, 64),
        },
        "channel": 0,
    },
    "synth": {
        "programs": ((80, "square_lead"), (81, "saw_lead"), (82, "calliope_lead"),
                     (83, "chiff_lead"), (84, "charang_lead"), (85, "voice_lead"),
                     (86, "fifths_lead"), (87, "bass_and_lead"), (88, "new_age_pad"),
                     (89, "warm_pad"), (90, "polysynth_pad"), (91, "choir_pad"),
                     (92, "bowed_pad"), (93, "metallic_pad"), (94, "halo_pad"),
                     (95, "sweep_pad")),
        "notes": SYNTH_NOTES,
        "channel": 0,
    },
    "strings": {
        "programs": ((40, "violin"), (41, "viola"), (42, "cello"), (43, "contrabass"),
                     (44, "tremolo_strings"), (45, "pizzicato_strings"), (46, "orchestral_harp"),
                     (48, "string_ensemble_1"), (49, "string_ensemble_2"),
                     (50, "synth_strings_1"), (51, "synth_strings_2")),
        "notes": STRING_NOTES,
        "program_notes": {
            40: (55, 60, 64, 67, 72, 76, 79, 84, 88, 91),
            41: (48, 52, 55, 60, 64, 67, 72, 76, 79, 84),
            42: (36, 40, 43, 48, 52, 55, 60, 64, 67, 72),
            43: (28, 31, 35, 36, 40, 43, 47, 48, 52, 55),
        },
        "channel": 0,
    },
    "vocals": {
        "programs": ((52, "choir_aahs"), (53, "voice_oohs"), (54, "synth_voice"),
                     (85, "voice_lead")),
        "notes": VOCAL_NOTES,
        "program_notes": {
            53: (55, 57, 59, 60, 62, 64, 67, 69, 71, 72, 74, 76),
        },
        "channel": 0,
    },
}

DRUM_KITS = (
    (0, "standard"),
    (8, "room"),
    (16, "power"),
    (24, "electronic"),
    (25, "tr808"),
    (32, "jazz"),
    (40, "brush"),
    (48, "orchestra"),
)

DRUM_VELOCITIES = (36, 40, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 118, 122, 126)

DRUM_NOTES = (
    ("kick", 35, "acoustic_bass_drum"),
    ("snare", 38, "acoustic_snare"),
    ("rim", 37, "side_stick"),
    ("hihat", 42, "closed_hihat"),
    ("crash", 57, "crash_cymbal_2"),
    ("tom", 45, "low_tom"),
    ("ride", 51, "ride_cymbal_1"),
)


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def varlen(value):
    parts = [value & 0x7F]
    value >>= 7
    while value:
        parts.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(parts))


def midi_file(program, midi_note, channel, velocity, duration_seconds, percussion=False):
    track = bytearray()
    track.extend(b"\x00\xff\x51\x03")
    track.extend(struct.pack(">I", TEMPO_US_PER_QUARTER)[1:])
    track.extend(b"\x00\xc0")
    track.append(program & 0x7F)
    if percussion:
        channel = 9
        track[-2] = 0xC0 | channel
    track.extend(b"\x00\xb0")
    track.append(7)
    track.append(116)
    if percussion:
        track[-3] = 0xB0 | channel
    track.extend(b"\x00")
    track.append(0x90 | channel)
    track.append(midi_note & 0x7F)
    track.append(velocity & 0x7F)
    note_ticks = max(120, int(duration_seconds * TICKS_PER_SECOND))
    track.extend(varlen(note_ticks))
    track.append(0x80 | channel)
    track.append(midi_note & 0x7F)
    track.append(0)
    track.extend(varlen(int(0.20 * TICKS_PER_SECOND)))
    track.extend(b"\xff\x2f\x00")

    data = bytearray()
    data.extend(b"MThd")
    data.extend(struct.pack(">IHHH", 6, 0, 1, TICKS_PER_QUARTER))
    data.extend(b"MTrk")
    data.extend(struct.pack(">I", len(track)))
    data.extend(track)
    return bytes(data)


def run(command, cwd=None):
    subprocess.run(command, cwd=cwd, check=True)


def find_command(name):
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"prepare_instrument_samples: missing required tool `{name}`")
    return path


def extract_deb(package, download_dir):
    debs = sorted(download_dir.glob(f"{package}_*.deb"))
    if not debs:
        raise SystemExit(f"prepare_instrument_samples: apt-get did not download {package}")
    extract_dir = download_dir / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    run(["dpkg-deb", "-x", str(debs[-1]), str(extract_dir)])
    soundfonts = sorted(extract_dir.glob("usr/share/sounds/sf2/*.sf2"))
    if not soundfonts:
        raise SystemExit(f"prepare_instrument_samples: no .sf2 found in {debs[-1]}")
    return soundfonts[0]


def resolve_soundfont(args):
    candidates = []
    if args.soundfont:
        candidates.append(args.soundfont)
    candidates.extend(DEFAULT_SYSTEM_SOUNDFONTS)
    candidates.append(str(args.download_dir / "extracted/usr/share/sounds/sf2/FluidR3_GM.sf2"))
    candidates.append(str(args.download_dir / "extracted/usr/share/sounds/sf2/TimGM6mb.sf2"))

    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path

    args.download_dir.mkdir(parents=True, exist_ok=True)
    find_command("apt-get")
    find_command("dpkg-deb")
    run(["apt-get", "download", args.soundfont_package], cwd=args.download_dir)
    return extract_deb(args.soundfont_package, args.download_dir)


def manifest_complete(path, expected_signature):
    if not path.is_file():
        return False
    root = path.parent
    with path.open("r", encoding="utf-8") as file:
        header = file.readline()
        if "\tpath\t" not in header:
            return False
        for line in file:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                return False
            if not (root / fields[4]).is_file():
                return False
            if fields[7] != expected_signature:
                return False
    return True


def signature_text(soundfont, args):
    try:
        stat = soundfont.stat()
        soundfont_key = f"{soundfont}:{stat.st_size}:{int(stat.st_mtime)}"
    except OSError:
        soundfont_key = str(soundfont)
    payload = (
        f"{FIXTURE_VERSION}|{soundfont_key}|programs={args.programs_per_family}|"
        f"target={args.target_per_family}|drum_kits={args.drum_kits}|"
        f"duration={args.duration:.3f}|velocity={args.velocity}|"
        f"gain={args.gain:.3f}|drum_duration={args.drum_duration:.3f}|"
        f"drum_velocity={args.drum_velocity}|drum_gain={args.drum_gain:.3f}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def render_one(fluidsynth, soundfont, midi_path, wav_path, gain):
    run([
        fluidsynth,
        "-ni",
        "-q",
        "-g",
        f"{gain:.3f}",
        "-r",
        str(SAMPLE_RATE),
        "-F",
        str(wav_path),
        str(soundfont),
        str(midi_path),
    ])


def render_many(tasks, jobs):
    if not tasks:
        return
    workers = max(1, int(jobs))
    if workers == 1:
        for task in tasks:
            render_one(*task)
        return

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(render_one, *task) for task in tasks]
        for future in as_completed(futures):
            future.result()


def excluded_reason(family, program, midi_note):
    return ONE_NOTE_EXCLUSIONS.get((family, program, midi_note)) or ONE_NOTE_EXCLUSIONS.get((family, program, None))


def instrument_variants(args, base_count):
    variants = [(args.velocity, args.duration)]
    for duration in INSTRUMENT_DURATION_VARIANTS:
        for velocity in INSTRUMENT_VELOCITY_VARIANTS:
            variant = (velocity, duration)
            if variant not in variants:
                variants.append(variant)

    if args.target_per_family <= 0 or base_count <= 0:
        return variants[:1]
    needed = int(math.ceil(args.target_per_family / float(base_count)))
    if needed > len(variants):
        raise SystemExit(
            f"prepare_instrument_samples: need {needed} variants to reach {args.target_per_family} samples "
            f"from {base_count} base notes, but only {len(variants)} variants are configured"
        )
    return variants[:needed]


def prepare_family(args, fluidsynth, soundfont, family, spec, signature):
    out_dir = args.output_root / f"{family}_samples"
    manifest_path = out_dir / "manifest.tsv"
    if not args.refresh and manifest_complete(manifest_path, signature):
        print(f"prepare_instrument_samples: keeping existing {manifest_path}")
        return

    if out_dir.exists():
        shutil.rmtree(out_dir)
    midi_dir = out_dir / "_midi"
    midi_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    tasks = []
    exclusions = []
    programs = spec["programs"] if args.programs_per_family <= 0 else spec["programs"][:args.programs_per_family]
    base_notes = []
    for program, program_name in programs:
        notes = spec.get("program_notes", {}).get(program, spec["notes"])
        for midi_note in notes:
            reason = excluded_reason(family, program, midi_note)
            if reason:
                exclusions.append((family, str(program), program_name, str(midi_note), note_name(midi_note), reason))
                continue
            base_notes.append((program, program_name, midi_note))

    variants = instrument_variants(args, len(base_notes))
    for program, program_name, midi_note in base_notes:
        for velocity, duration in variants:
            note = note_name(midi_note)
            duration_tag = int(round(duration * 1000.0))
            stem = (
                f"{program:03d}_{program_name}_{midi_note:03d}_{note.replace('#', 's')}"
                f"_v{velocity:03d}_d{duration_tag:04d}"
            )
            midi_path = midi_dir / f"{stem}.mid"
            wav_path = out_dir / f"{stem}.wav"
            midi_path.write_bytes(midi_file(program, midi_note, spec["channel"], velocity, duration))
            tasks.append((fluidsynth, soundfont, midi_path, wav_path, args.gain))
            rows.append((family, str(program), program_name, str(midi_note), str(wav_path.relative_to(out_dir)),
                         note, str(soundfont), signature))

    render_many(tasks, args.jobs)

    with manifest_path.open("w", encoding="utf-8") as file:
        file.write("family\tprogram\tprogram_name\tmidi\tpath\tnote\tsoundfont\tsignature\n")
        for row in rows:
            file.write("\t".join(row) + "\n")
    append_exclusions(args.output_root, exclusions)
    print(f"prepare_instrument_samples: wrote {manifest_path} ({len(rows)} samples)")


def prepare_drums(args, fluidsynth, soundfont, signature):
    out_dir = args.output_root / "drum_kit_samples"
    manifest_path = out_dir / "manifest.tsv"
    if not args.refresh and manifest_complete(manifest_path, signature):
        print(f"prepare_instrument_samples: keeping existing {manifest_path}")
        return

    if out_dir.exists():
        shutil.rmtree(out_dir)
    midi_dir = out_dir / "_midi"
    midi_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    tasks = []
    kit_programs = DRUM_KITS if args.drum_kits <= 0 else DRUM_KITS[:args.drum_kits]
    target = max(0, args.target_per_family)
    base_count = max(1, len(kit_programs) * len(DRUM_NOTES))
    needed = len(DRUM_VELOCITIES) if target <= 0 else int(math.ceil(target / float(base_count)))
    if needed > len(DRUM_VELOCITIES):
        raise SystemExit(
            f"prepare_instrument_samples: need {needed} drum velocities for target {target}, "
            f"but only {len(DRUM_VELOCITIES)} are configured"
        )
    drum_velocities = DRUM_VELOCITIES[:needed]
    for kit_program, kit_name in kit_programs:
        for category, midi_note, note_name_text in DRUM_NOTES:
            for velocity in drum_velocities:
                stem = f"{kit_program:03d}_{kit_name}_{midi_note:03d}_{category}_v{velocity:03d}"
                midi_path = midi_dir / f"{stem}.mid"
                wav_path = out_dir / f"{stem}.wav"
                midi_path.write_bytes(
                    midi_file(kit_program, midi_note, 9, velocity, args.drum_duration, percussion=True)
                )
                tasks.append((fluidsynth, soundfont, midi_path, wav_path, args.drum_gain))
                rows.append((category, str(kit_program), kit_name, str(midi_note), str(wav_path.relative_to(out_dir)),
                             note_name_text, str(soundfont), signature))

    render_many(tasks, args.jobs)

    with manifest_path.open("w", encoding="utf-8") as file:
        file.write("family\tprogram\tprogram_name\tmidi\tpath\tnote\tsoundfont\tsignature\n")
        for row in rows:
            file.write("\t".join(row) + "\n")
    print(f"prepare_instrument_samples: wrote {manifest_path} ({len(rows)} samples)")


def append_exclusions(output_root, exclusions):
    if not exclusions:
        return
    path = output_root / "instrument_sample_exclusions.tsv"
    write_header = not path.is_file()
    with path.open("a", encoding="utf-8") as file:
        if write_header:
            file.write("family\tprogram\tprogram_name\tmidi\tnote\treason\n")
        for row in exclusions:
            file.write("\t".join(row) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Render build-local single-note WAV fixtures from a GM SoundFont."
    )
    parser.add_argument("--output-root", default=os.environ.get("INSTRUMENT_SAMPLE_BUILD_ROOT", "build"))
    parser.add_argument("--download-dir", default=os.environ.get("INSTRUMENT_SAMPLE_SOURCE_DIR",
                                                                 "build/instrument_sample_sources"))
    parser.add_argument("--soundfont", default=os.environ.get("INSTRUMENT_SAMPLE_SOUNDFONT", ""))
    parser.add_argument("--soundfont-package", default=os.environ.get("INSTRUMENT_SAMPLE_SOUNDFONT_PACKAGE",
                                                                      "fluid-soundfont-gm"))
    parser.add_argument("--programs-per-family", type=int,
                        default=int(os.environ.get("INSTRUMENT_SAMPLE_PROGRAMS_PER_FAMILY", "0")))
    parser.add_argument("--drum-kits", type=int, default=int(os.environ.get("INSTRUMENT_SAMPLE_DRUM_KITS", "8")))
    parser.add_argument("--target-per-family", type=int,
                        default=int(os.environ.get("INSTRUMENT_SAMPLE_TARGET_PER_FAMILY", "1000")))
    parser.add_argument("--jobs", type=int, default=int(os.environ.get("INSTRUMENT_SAMPLE_JOBS", "4")))
    parser.add_argument("--duration", type=float, default=float(os.environ.get("INSTRUMENT_SAMPLE_DURATION", "1.4")))
    parser.add_argument("--velocity", type=int, default=int(os.environ.get("INSTRUMENT_SAMPLE_VELOCITY", "112")))
    parser.add_argument("--gain", type=float, default=float(os.environ.get("INSTRUMENT_SAMPLE_GAIN", "0.75")))
    parser.add_argument("--drum-duration", type=float,
                        default=float(os.environ.get("INSTRUMENT_SAMPLE_DRUM_DURATION", "0.8")))
    parser.add_argument("--drum-velocity", type=int,
                        default=int(os.environ.get("INSTRUMENT_SAMPLE_DRUM_VELOCITY", "118")))
    parser.add_argument("--drum-gain", type=float, default=float(os.environ.get("INSTRUMENT_SAMPLE_DRUM_GAIN", "0.95")))
    parser.add_argument("--refresh", action="store_true", default=os.environ.get("INSTRUMENT_SAMPLE_REFRESH") == "1")
    args = parser.parse_args()

    args.output_root = Path(args.output_root)
    args.download_dir = Path(args.download_dir)
    args.output_root.mkdir(parents=True, exist_ok=True)
    exclusions_path = args.output_root / "instrument_sample_exclusions.tsv"
    if args.refresh and exclusions_path.exists():
        exclusions_path.unlink()

    fluidsynth = find_command("fluidsynth")
    soundfont = resolve_soundfont(args)
    signature = signature_text(soundfont, args)

    print(f"prepare_instrument_samples: using {soundfont}")
    for family, spec in FAMILIES.items():
        prepare_family(args, fluidsynth, soundfont, family, spec, signature)
    prepare_drums(args, fluidsynth, soundfont, signature)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"prepare_instrument_samples: command failed: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
