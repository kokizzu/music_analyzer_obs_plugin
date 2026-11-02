#!/usr/bin/env python3
"""Plan/apply invalidation of replay entries whose saved TSV hash changed."""
import argparse
import json
import subprocess

from checkpoint_routing_extensions import REPORTS
from routing_duration_baseline import ROOT, atomic_json, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    plan_path = ROOT / 'build/routing_replay_repair_plan.json'
    if not args.apply:
        items = []
        for key in REPORTS:
            directory = ROOT / 'build/piano_guitar_extensions' / key
            checkpoint = directory / 'report.json'
            report = json.loads(checkpoint.read_text())
            for name, entry in report['recordings'].items():
                path = directory / (name + '.tsv')
                if digest(path) != entry['sha256']:
                    items.append(dict(key=key, id=name, checkpoint_sha256=digest(checkpoint),
                                      observed_sha256=digest(path), recorded_sha256=entry['sha256']))
        atomic_json(plan_path, dict(items=items))
        print(json.dumps(items, indent=2))
        return
    processes = subprocess.run(['ps', '-eo', 'args'], text=True, capture_output=True, check=True).stdout
    assert not any('validate_piano_guitar_extensions.py' in line or '5423eaeda3f96b38/pair ' in line for line in processes.splitlines())
    plan = json.loads(plan_path.read_text())
    for key in sorted({item['key'] for item in plan['items']}):
        directory = ROOT / 'build/piano_guitar_extensions' / key
        checkpoint = directory / 'report.json'
        selected = [item for item in plan['items'] if item['key'] == key]
        assert all(digest(checkpoint) == item['checkpoint_sha256'] for item in selected)
        report = json.loads(checkpoint.read_text())
        # Backup supplies a direct rollback path; TSVs are never deleted.
        backup = directory / ('report.pre-repair-' + digest(checkpoint)[:16] + '.json')
        if not backup.exists():
            backup.write_bytes(checkpoint.read_bytes())
        for item in selected:
            assert digest(directory / (item['id'] + '.tsv')) == item['observed_sha256']
            assert report['recordings'][item['id']]['sha256'] == item['recorded_sha256']
            del report['recordings'][item['id']]
        report.update(complete=False, passed=False)
        atomic_json(checkpoint, report)
        print('Invalidated', key, [item['id'] for item in selected])


if __name__ == '__main__':
    main()
