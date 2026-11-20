#!/usr/bin/env python3
"""Retain failure anchors by immutable external-file reference, without audio copies."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from analyzer_diagnostic import primary_tool
from detection_validation_store import Store
from routing_duration_baseline import ROOT,digest


def schema(store):
    store.connection.executescript('''
        create table if not exists regression_files (
            id text primary key,path text not null,sha256 text not null,rate integer not null);
        create table if not exists regression_cases (
            id text primary key,raw_id text not null references regression_files(id),
            reference_id text references regression_files(id),midi_id text references regression_files(id),
            metadata text not null references payloads(hash));
    ''')


def file_ref(store,path,rate):
    path=path.resolve();checksum=digest(path)
    key=hashlib.sha256((str(rate)+':'+checksum).encode()).hexdigest()
    location=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    store.connection.execute('insert or ignore into regression_files values(?,?,?,?)',(key,location,checksum,rate))
    return key


def register_case(store,name,raw,rate,metadata,reference=None,midi=None):
    schema(store)
    with store.connection:
        store.connection.execute('begin immediate')
        raw_id=file_ref(store,raw,rate);reference_id=file_ref(store,reference,0) if reference else None
        midi_id=file_ref(store,midi,0) if midi else None;payload=store.put(json.dumps(metadata,sort_keys=True).encode())
        store.connection.execute('insert into regression_cases values(?,?,?,?,?) on conflict(id) do update set raw_id=excluded.raw_id,reference_id=excluded.reference_id,midi_id=excluded.midi_id,metadata=excluded.metadata',
            (name,raw_id,reference_id,midi_id,payload))


def verify_files(store):
    schema(store)
    for location,checksum in store.connection.execute('select path,sha256 from regression_files'):
        if digest(ROOT/location)!=checksum:
            raise ValueError('Regression input changed: '+Path(location).name)


def register():
    baseline=ROOT/'build/routing_duration_baseline/f3c7f7a446eed267'
    manifest=json.loads((baseline/'report.json').read_text());sample=next(s for s in manifest['selection'] if s['id']=='training-1')
    raw=baseline/'training-1.f32';assert digest(raw)==manifest['recordings']['training-1']['prefix_sha256']
    audit_document=json.loads((ROOT/'build/keyboard_routing_gap_audit.json').read_text())
    assert all(digest(ROOT/p)==h for p,h in audit_document['inputs'].items())
    audit=audit_document['recordings']['training-1']['attacks']['cases']
    route=next(c for c in audit if c['category']=='guitar_or_voice_visible_by_deadline')
    repeat=next(c for c in audit if c['category']=='keyboard_already_visible_at_onset' and c['prior_note_sounding_at_onset'])
    reference=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541/training-1-primary.tsv'
    parity=json.loads((reference.parent/'parity.json').read_text())
    assert digest(reference)==parity['recordings']['training-1']['primary_sha256'] and digest(ROOT/sample['midi'])==sample['midi_sha256']
    pointer=json.loads((ROOT/'build/pitch_continuity_controls/current.json').read_text());plan_path=ROOT/pointer['plan'];assert digest(plan_path)==pointer['sha256']
    plan=json.loads(plan_path.read_text());failed=next(s for s in plan['cases'] if s['id']=='extended-regression-piano-reserve-12-48k')
    assert digest(ROOT/failed['raw'])==failed['raw_sha256'] and digest(ROOT/failed['reference'])==failed['reference_sha256']
    with Store() as store:
        verify_files(store)
        register_case(store,'piano-wrong-row',raw,44100,dict(kind='known development routing miss',anchor=route),reference,ROOT/sample['midi'])
        register_case(store,'piano-pedal-restrike',raw,44100,dict(kind='known development repeated strike while prior MIDI tone sounds',anchor=repeat),reference,ROOT/sample['midi'])
        register_case(store,'rejected-continuity-flash',ROOT/failed['raw'],failed['rate'],
            dict(kind='isolated flash in rejected continuity candidate; preserve ordinary primary behavior',case=failed['id']),ROOT/failed['reference'],ROOT/failed['midi'] if 'midi' in failed else None)
        verify_files(store)
        print('Registered 3 failure anchors using 2 existing audio inputs; no PCM copies',flush=True)


def replay():
    binary,metadata=primary_tool();columns=('end_sample','bass','guitar','keys','voice','other','ambiguous','chord','bpm','confidence','drums')
    results={}
    with Store() as store:
        verify_files(store)
        cases=list(store.connection.execute('select c.id,r.path,r.rate,e.path from regression_cases c join regression_files r on r.id=c.raw_id join regression_files e on e.id=c.reference_id order by c.id'))
        assert len(cases)==3
        with tempfile.TemporaryDirectory(prefix='regression-replay-') as temporary:
            cache={}
            for name,raw,rate,reference in cases:
                if (raw,rate) not in cache:
                    output=Path(temporary)/('replay-'+str(len(cache))+'.tsv')
                    subprocess.run([str(binary),str(ROOT/raw),str(rate),str(output)],check=True,timeout=180)
                    with output.open() as stream: rows=list(csv.DictReader(stream,delimiter='\t'))
                    cache[raw,rate]=(rows,digest(output))
                rows,checksum=cache[raw,rate]
                with (ROOT/reference).open() as stream: expected=list(csv.DictReader(stream,delimiter='\t'))
                assert len(rows)==len(expected) and all(all(r[k]==e[k] for k in columns) for r,e in zip(rows,expected)),name
                results[name]=dict(frames=len(rows),output_sha256=checksum)
        store.evidence('regression-replay','validation',dict(source_tree=metadata['inputs']['source_tree'],cases=results,unique_inputs=len(cache),passed=True,
            inputs={'scripts/regression_recordings.py':digest(Path(__file__))},scope='Ordinary primary output preservation on retained failure inputs; rejected experiments remain off. Shared audio inputs are not independent recordings.'))
    print(json.dumps(results,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('register','replay'));args=parser.parse_args()
    {'register':register,'replay':replay}[args.mode]()


if __name__=='__main__': main()
