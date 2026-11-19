"""One transactional, content-addressed store for new detection diagnostics."""
import hashlib
import json
from pathlib import Path
import sqlite3
import zlib

DEFAULT=Path(__file__).resolve().parents[1]/'build/detection_validation.sqlite3'


class Store:
    def __init__(self,path=DEFAULT,max_bytes=128*1024*1024,max_payloads=4096):
        path.parent.mkdir(parents=True,exist_ok=True)
        self.max_bytes=max_bytes;self.max_payloads=max_payloads
        self.connection=sqlite3.connect(path,timeout=30)
        self.connection.execute('pragma foreign_keys=on')
        self.connection.executescript('''
            create table if not exists payloads (
                hash text primary key, raw_size integer not null, data blob not null);
            create table if not exists evidence (
                id text primary key, kind text not null, payload text not null references payloads(hash));
            create table if not exists recordings (
                id text primary key, rate integer not null, samples integer not null,
                audio text not null references payloads(hash));
            create table if not exists replays (
                recording text not null references recordings(id), binary text not null,
                output text not null references payloads(hash),
                primary key(recording,binary));
        ''')

    def put(self,data):
        checksum=hashlib.sha256(data).hexdigest()
        if not self.connection.in_transaction:
            self.connection.execute('begin immediate')
        if self.connection.execute('select 1 from payloads where hash=?',(checksum,)).fetchone():
            return checksum
        compressed=zlib.compress(data,6)
        count,size=self.connection.execute('select count(*),coalesce(sum(length(data)),0) from payloads').fetchone()
        if count>=self.max_payloads or size+len(compressed)>self.max_bytes:
            raise ValueError('Diagnostic payload budget reached; review retained evidence before cleanup')
        self.connection.execute('insert or ignore into payloads values(?,?,?)',
            (checksum,len(data),compressed))
        return checksum

    def get(self,checksum):
        row=self.connection.execute('select raw_size,data from payloads where hash=?',(checksum,)).fetchone()
        if row is None:
            raise KeyError(checksum)
        data=zlib.decompress(row[1])
        if len(data)!=row[0] or hashlib.sha256(data).hexdigest()!=checksum:
            raise ValueError('Corrupt diagnostic payload')
        return data

    def evidence(self,name,kind,value):
        with self.connection:
            payload=self.put(json.dumps(value,sort_keys=True,allow_nan=False).encode())
            self.connection.execute('insert into evidence values(?,?,?) on conflict(id) do update set kind=excluded.kind,payload=excluded.payload',
                (name,kind,payload))

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.connection.close()
