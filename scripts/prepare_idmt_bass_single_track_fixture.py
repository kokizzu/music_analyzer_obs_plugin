#!/usr/bin/env python3
"""Create isolated, ground-truth bass-note fixtures from IDMT bass-line audio."""

from __future__ import annotations

import shutil
from pathlib import Path
import wave
import xml.etree.ElementTree as ElementTree


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "build/InstrumentSamples/idmt_smt_bass_single_track/source"
OUTPUT = ROOT / "build/idmt_bass_single_track_fixture"
MIN_DURATION_SECONDS = 0.120
MAX_CLIP_SECONDS = 0.900
MIN_CLIP_SECONDS = 0.900


def event_values(event: ElementTree.Element) -> dict[str, str]:
    return {child.tag: (child.text or "").strip() for child in event}


def copy_clip(source: Path, destination: Path, onset: float, duration: float) -> None:
    with wave.open(str(source), "rb") as reader:
        params = reader.getparams()
        if params.comptype != "NONE":
            raise ValueError(f"unsupported compressed WAV: {source}")
        sample_rate = reader.getframerate()
        start = max(0, int(round(onset * sample_rate)))
        frames = min(reader.getnframes() - start, int(round(min(duration, MAX_CLIP_SECONDS) * sample_rate)))
        if frames <= 0:
            raise ValueError(f"empty clip at {onset:.3f}s: {source}")
        reader.setpos(start)
        payload = reader.readframes(frames)
        target_frames = max(frames, int(round(MIN_CLIP_SECONDS * sample_rate)))
        padding = b"\0" * ((target_frames - frames) * params.sampwidth * params.nchannels)
    with wave.open(str(destination), "wb") as writer:
        writer.setparams(params)
        writer.writeframes(payload)
        writer.writeframes(padding)


def main() -> int:
    annotation_dir = SOURCE / "annotation"
    audio_dir = SOURCE / "audio"
    if not annotation_dir.is_dir() or not audio_dir.is_dir():
        raise SystemExit("missing extracted IDMT bass source; run make import-idmt-bass-single-track-archive")

    temporary = OUTPUT.with_name(OUTPUT.name + ".tmp")
    shutil.rmtree(temporary, ignore_errors=True)
    clips = temporary / "clips"
    clips.mkdir(parents=True)
    rows: list[tuple[str, int, str, str, str, str]] = []
    metadata: list[tuple[str, str, float, float, int, str, str, str]] = []
    for annotation_path in sorted(annotation_dir.glob("*.xml")):
        recording = annotation_path.stem
        source_audio = audio_dir / f"{recording}.wav"
        if not source_audio.is_file():
            raise SystemExit(f"missing source audio for {annotation_path.name}")
        for event_index, event in enumerate(ElementTree.parse(annotation_path).iter("event"), start=1):
            values = event_values(event)
            try:
                onset = float(values["onsetSec"])
                offset = float(values["offsetSec"])
                midi = int(values["pitch"])
            except (KeyError, ValueError) as error:
                raise SystemExit(f"invalid event {annotation_path.name}#{event_index}: {error}") from error
            duration = offset - onset
            if duration < MIN_DURATION_SECONDS:
                continue
            sample_id = f"idmt_bass_{recording}_{event_index:03d}"
            relative_clip = f"clips/{sample_id}.wav"
            copy_clip(source_audio, temporary / relative_clip, onset, duration)
            rows.append((sample_id, midi, relative_clip, values.get("excitationStyle", ""),
                         values.get("expressionStyle", ""), values.get("stringNumber", "")))
            metadata.append((sample_id, recording, onset, offset, midi, values.get("excitationStyle", ""),
                             values.get("expressionStyle", ""), values.get("stringNumber", "")))

    if not rows:
        raise SystemExit("no usable IDMT bass note events")
    with (temporary / "manifest.tsv").open("w", encoding="utf-8") as manifest:
        manifest.write("id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\n")
        for sample_id, midi, relative_clip, _excitation, _expression, _string in rows:
            manifest.write(f"{sample_id}\tbass\tbass\tIDMT bass\t{midi}\tmidi-{midi}\t{relative_clip}\n")
    with (temporary / "metadata.tsv").open("w", encoding="utf-8") as output:
        output.write("id\trecording\tonset\toffset\tmidi\texcitation\texpression\tstring\n")
        for row in metadata:
            output.write("\t".join(map(str, row)) + "\n")
    (temporary / ".complete").write_text(f"samples={len(rows)}\n", encoding="ascii")
    previous = OUTPUT.with_name(OUTPUT.name + ".previous")
    shutil.rmtree(previous, ignore_errors=True)
    if OUTPUT.exists():
        OUTPUT.replace(previous)
    temporary.replace(OUTPUT)
    shutil.rmtree(previous, ignore_errors=True)
    print(f"prepared {len(rows)} IDMT bass note clips: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
