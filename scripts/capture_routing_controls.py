#!/usr/bin/env python3
"""Capture instrument/singer-disjoint controls using the unchanged primary engine."""
import array
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

from routing_duration_baseline import ROOT, atomic_json, digest, primary_build


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def selected_controls():
    selected = []
    base = ROOT / 'build/real_note_samples'
    manifest = rows(base / 'manifest.tsv')
    groups = {}
    for row in manifest:
        if row['family'] == 'guitar':
            group = row['id'].rsplit('-', 2)[0]
            groups.setdefault(group, []).append(row)
        elif row['family'] == 'vocals':
            selected.append((base, row, 'protected', 'NSynth-voice'))
    for group, candidates in sorted(groups.items()):
        cohort = 'heldout' if group in ('guitar_acoustic_015', 'guitar_electronic_028') else 'training'
        for row in sorted(candidates, key=lambda r: hashlib.sha256(r['id'].encode()).hexdigest())[:8]:
            selected.append((base, row, cohort, group))
    base = ROOT / 'build/vocalset_samples'
    singers = {}
    for row in rows(base / 'manifest.tsv'):
        qualities = dict(part.split('=', 1) for part in row['qualities'].split(',') if '=' in part)
        singers.setdefault(qualities['singer'], []).append(row)
    held = {'f8', 'f9', 'm8', 'm9', 'm10', 'm11'}
    for singer, candidates in sorted(singers.items()):
        used = set()
        for row in sorted(candidates, key=lambda r: hashlib.sha256(r['id'].encode()).hexdigest()):
            qualities = dict(part.split('=', 1) for part in row['qualities'].split(',') if '=' in part)
            if qualities['filename'] in used:
                continue
            selected.append((base, row, 'heldout' if singer in held else 'training', 'VocalSet-' + singer))
            used.add(qualities['filename'])
            if len(used) == 4:
                break
    result = []
    for base, row, cohort, group in selected:
        path = base / row['path']
        result.append(dict(id=row['id'], family=row['family'], midi=int(row['midi']), cohort=cohort,
                           group=group, audio=str(path.relative_to(ROOT)), audio_sha256=digest(path)))
    assert len({row['audio_sha256'] for row in result}) == len(result), 'Duplicate control audio'
    train = {row['group'] for row in result if row['cohort'] == 'training'}
    assert not train & {row['group'] for row in result if row['cohort'] != 'training'}
    return result


def main():
    directory, build = primary_build()
    matches = []
    for path in (ROOT / 'build/routing_candidate_evidence').glob('*/report.json'):
        state = json.loads(path.read_text())
        if state['complete'] and state['inputs']['build'] == build:
            matches.append((path, state))
    assert len(matches) == 1, 'Need one current, parity-checked candidate exporter'
    exporter_path, exporter = matches[0]
    binary = exporter_path.parent / 'replay'
    assert digest(binary) == exporter['binary_sha256']
    selected = selected_controls()
    inputs = dict(build=build, selection=selected, exporter_sha256=digest(exporter_path),
                  script_sha256=digest(Path(__file__)))
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
    output = ROOT / 'build/routing_controls' / key
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = output / 'report.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(inputs=inputs, recordings={}, complete=False)
    assert state['inputs'] == inputs
    atomic_json(checkpoint, state)
    for index, sample in enumerate(selected, 1):
        path = ROOT / sample['audio']
        raw, capture = output / (sample['id'] + '.f32'), output / (sample['id'] + '.tsv')
        with wave.open(str(path), 'rb') as audio:
            assert audio.getsampwidth() == 2 and audio.getcomptype() == 'NONE'
            rate, channels = audio.getframerate(), audio.getnchannels()
            values = array.array('h', audio.readframes(min(audio.getnframes(), rate * 4)))
        if sys.byteorder != 'little':
            values.byteswap()
        mono = array.array('f', (sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)))
        if sys.byteorder != 'little':
            mono.byteswap()
        raw.write_bytes(mono.tobytes())
        hop = int(rate * .05 + .5)
        assert len(mono) >= hop * 2, 'Control is too short'
        if sample['id'] in state['recordings']:
            assert digest(capture) == state['recordings'][sample['id']]['sha256']
        else:
            subprocess.run([str(binary), str(raw), str(rate), str(capture)], check=True, timeout=180)
        seen = set()
        eligible = correct_loss = 0
        with capture.open() as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                seen.add(int(row['end_sample']))
                row_name = 'guitar' if sample['family'] == 'guitar' else 'voice'
                if (row['midi'] not in row[row_name].split(',') or row['midi'] not in row['keys'].split(',') or
                        float(row['keyboard_score']) < .9 or float(row['guitar_score']) > .05 or
                        float(row['vocal_score']) > .05 or row['profile'] != '0'):
                    continue
                eligible += 1
                correct_loss += int(row['midi']) == sample['midi']
        assert seen == set(range(hop, len(mono) // hop * hop + 1, hop))
        assert digest(path) == sample['audio_sha256']
        state['recordings'][sample['id']] = dict(sha256=digest(capture), prefix_sha256=digest(raw), rate=rate,
                        windows=len(seen), strict_duplicate_proposals=eligible, strict_duplicate_correct_losses=correct_loss)
        atomic_json(checkpoint, state)
        print(index, '/', len(selected), sample['cohort'], sample['group'], 'proposals', eligible, 'correct losses', correct_loss, flush=True)
    assert digest(Path(__file__)) == inputs['script_sha256'] and digest(binary) == exporter['binary_sha256']
    state['complete'] = True
    atomic_json(checkpoint, state)
    print(checkpoint.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
