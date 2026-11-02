#!/usr/bin/env python3
"""Capture performer-disjoint recorded chord controls for the routing filter."""
import array
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

from routing_duration_baseline import ROOT, atomic_json, digest, primary_build


def selection():
    selected = []
    manifests = {}
    for corpus, folder in (('GuitarTECHS', 'guitar_techs_chord_samples'), ('ChordMix', 'guitar_chord_mix_samples')):
        base = ROOT / 'build' / folder
        manifest = base / 'manifest.tsv'
        manifests[str(manifest.relative_to(ROOT))] = digest(manifest)
        groups = {}
        for line in manifest.read_text().splitlines():
            values = line.split('\t')
            if values[0] != 'AUDIO':
                continue
            _, name, filename = values
            if corpus == 'GuitarTECHS':
                group = 'P1' if 'chords_P1_' in name else 'P2' if 'chords_P2_' in name else None
                if group is None:
                    continue
                path = base / 'audio' / Path(filename).name
            else:
                if 'isolated-chords' not in name or 'acoustic_guitar' not in name:
                    continue
                group = 'independent-acoustic'
                path = base / 'clips/isolated-chords' / Path(filename).name
            assert path.resolve(strict=True) == Path(filename).resolve(strict=True), 'Fixture points to another recording'
            groups.setdefault(group, []).append((name, path))
        for group, candidates in sorted(groups.items()):
            limit = 16 if corpus == 'ChordMix' else 32
            assert len(candidates) >= limit
            for name, path in sorted(candidates, key=lambda row: hashlib.sha256(row[0].encode()).hexdigest())[:limit]:
                selected.append(dict(id=name, audio=str(path.relative_to(ROOT)), audio_sha256=digest(path),
                    group=corpus + '-' + group, cohort='training' if group == 'P1' else 'heldout', protect_entire_guitar_row=True))
    assert len({row['audio_sha256'] for row in selected}) == len(selected)
    return selected, manifests


def main():
    _, build = primary_build()
    matches = []
    for path in (ROOT / 'build/routing_candidate_evidence').glob('*/report.json'):
        state = json.loads(path.read_text())
        if state['complete'] and state['inputs']['build'] == build:
            matches.append((path, state))
    assert len(matches) == 1
    exporter_path, exporter = matches[0]
    binary = exporter_path.parent / 'replay'
    assert digest(binary) == exporter['binary_sha256']
    selected, manifests = selection()
    inputs = dict(selection=selected, manifests=manifests, exporter_sha256=digest(exporter_path), script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/routing_polycontrols' / key
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = output / 'report.json'
    report = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False,
        scope='Actual recorded Guitar chords; P1 training/P2 heldout plus independent acoustic chords; every Guitar display pitch is conservatively protected, including annotation-unsupported pitches')
    assert report['inputs'] == inputs
    atomic_json(checkpoint, report)
    for sample in selected:
        source = ROOT / sample['audio']
        raw, destination = output / (sample['id'] + '.f32'), output / (sample['id'] + '.tsv')
        with wave.open(str(source), 'rb') as audio:
            assert audio.getsampwidth() == 2 and audio.getcomptype() == 'NONE'
            rate, channels = audio.getframerate(), audio.getnchannels()
            values = array.array('h', audio.readframes(min(audio.getnframes(), rate * 4)))
        if sys.byteorder != 'little':
            values.byteswap()
        mono = array.array('f', (sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)))
        if sys.byteorder != 'little':
            mono.byteswap()
        raw.write_bytes(mono.tobytes())
        if sample['id'] in report['recordings']:
            assert digest(destination) == report['recordings'][sample['id']]['sha256']
        else:
            subprocess.run([str(binary), str(raw), str(rate), str(destination)], check=True, timeout=180)
        with destination.open() as stream:
            seen = {int(row['end_sample']) for row in csv.DictReader(stream, delimiter='\t')}
        hop = int(rate * .05 + .5)
        assert seen == set(range(hop, len(mono) // hop * hop + 1, hop))
        assert digest(source) == sample['audio_sha256']
        report['recordings'][sample['id']] = dict(sha256=digest(destination), prefix_sha256=digest(raw), rate=rate, windows=len(seen))
        atomic_json(checkpoint, report)
        print(sample['group'], len(seen), 'windows', flush=True)
    assert all(digest(ROOT / p) == checksum for p, checksum in manifests.items())
    assert digest(Path(__file__)) == inputs['script_sha256']
    report['complete'] = True
    atomic_json(checkpoint, report)
    print(checkpoint.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
