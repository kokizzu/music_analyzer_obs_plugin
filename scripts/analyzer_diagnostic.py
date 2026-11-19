#!/usr/bin/env python3
"""Bounded Linux monitor capture and exact-primary replay in one compact store."""
import argparse
import array
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
from detection_validation_store import Store
from publish_next_detection import git,identity
from routing_duration_baseline import ROOT,digest

TOOLS=ROOT/'build/pitch_heldout_tools/06aec4200b7fb541'
MAX_RECORDINGS=20


def save_recording(store,pcm,rate):
    if rate not in (16000,44100,48000) or not pcm or len(pcm)%4 or len(pcm)>rate*4*120:
        raise ValueError('Need finite f32 mono audio, supported rate and at most 120 seconds')
    values=array.array('f');values.frombytes(pcm)
    if sys.byteorder!='little':
        values.byteswap()
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Nonfinite audio')
    key=hashlib.sha256(struct.pack('<I',rate)+pcm).hexdigest()
    with store.connection:
        store.connection.execute('begin immediate')
        existing=store.connection.execute('select 1 from recordings where id=?',(key,)).fetchone()
        if not existing and store.connection.execute('select count(*) from recordings').fetchone()[0]>=MAX_RECORDINGS:
            raise ValueError('Diagnostic store is at its 20-recording limit; review retained recordings before cleanup')
        payload=store.put(pcm)
        store.connection.execute('insert or ignore into recordings values(?,?,?,?)',(key,rate,len(pcm)//4,payload))
    return key


def primary_tool():
    identity();metadata=json.loads((TOOLS/'build.json').read_text())
    assert metadata['inputs']['source_tree']==git('rev-parse','HEAD:src').strip(),'Rebuild and qualify the primary replay for the current source tree'
    assert digest(TOOLS/'primary')==metadata['binaries']['primary']
    return TOOLS/'primary',metadata


def replay(store,key):
    if key=='latest':
        row=store.connection.execute('select id from recordings order by rowid desc limit 1').fetchone()
        if row is None:
            raise ValueError('Capture a diagnostic recording first')
        key=row[0]
    row=store.connection.execute('select rate,samples,audio from recordings where id=?',(key,)).fetchone()
    if row is None:
        raise ValueError('Unknown recording ID')
    rate,samples,audio=row;binary,metadata=primary_tool();checksum=digest(binary)
    with tempfile.TemporaryDirectory(prefix='analyzer-diagnostic-') as temporary:
        raw=Path(temporary)/'audio.f32';output=Path(temporary)/'replay.tsv';raw.write_bytes(store.get(audio))
        started=time.monotonic()
        subprocess.run([str(binary),str(raw),str(rate),str(output)],check=True,timeout=600)
        wall=time.monotonic()-started;payload=output.read_bytes()
    frames=list(csv.DictReader(io.StringIO(payload.decode()),delimiter='\t'))
    hop=int(rate*.05+.5)
    assert len(frames)==samples//hop and all(int(r['end_sample'])==(i+1)*hop for i,r in enumerate(frames))
    previous=store.connection.execute('select output from replays where recording=? and binary=?',(key,checksum)).fetchone()
    if previous:
        assert store.get(previous[0])==payload,'Deterministic primary replay changed'
    with store.connection:
        output_hash=store.put(payload)
        store.connection.execute('insert or ignore into replays values(?,?,?)',(key,checksum,output_hash))
    result=dict(recording=key,rate=rate,frames=len(frames),audio_seconds=samples/rate,
        source_tree=metadata['inputs']['source_tree'],binary=checksum,output=output_hash,
        deterministic_repeat_checked=bool(previous),offline_wall_seconds=wall,
        scope='Exact committed-primary engine replay. Not the dirty workspace standalone build, a live audio callback benchmark or Basic Pitch integration qualification.')
    store.evidence('diagnostic-last-replay','replay',{k:v for k,v in result.items()
        if k not in ('offline_wall_seconds','deterministic_repeat_checked')})
    print(json.dumps(result),flush=True)
    return result


def capture(seconds):
    if not math.isfinite(seconds) or not 1<=seconds<=120:
        raise ValueError('Capture duration must be 1 to 120 seconds')
    sink=subprocess.run(['pactl','get-default-sink'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
    if not sink or '\n' in sink:
        raise ValueError('Cannot resolve the default output monitor')
    with tempfile.TemporaryDirectory(prefix='analyzer-capture-') as temporary:
        target=Path(temporary)/'capture.f32'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-f','pulse','-i',sink+'.monitor','-t',str(seconds),
            '-ac','1','-ar','48000','-f','f32le',str(target)],check=True,timeout=seconds+30)
        pcm=target.read_bytes()
    assert abs(len(pcm)/4/48000-seconds)<.1,'Unexpected capture duration'
    with Store() as store:
        key=save_recording(store,pcm,48000)
        print('Captured diagnostic recording',key,flush=True)
        replay(store,key)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('capture','replay','self-test'))
    parser.add_argument('--seconds',type=float,default=15);parser.add_argument('--recording',default='latest');args=parser.parse_args()
    if args.mode=='capture':
        capture(args.seconds)
    elif args.mode=='replay':
        with Store() as store:
            replay(store,args.recording)
    else:
        # Use a temporary database; test deterministic primary replay twice.
        with tempfile.TemporaryDirectory(prefix='diagnostic-test-') as temporary,Store(Path(temporary)/'state.sqlite3') as store:
            pcm=b''.join(struct.pack('<f',.1*math.sin(2*math.pi*440*i/48000)) for i in range(48000))
            key=save_recording(store,pcm,48000);first=replay(store,key);second=replay(store,key)
            assert first['frames']==20 and second['deterministic_repeat_checked'] and first['output']==second['output']


if __name__=='__main__':
    main()
