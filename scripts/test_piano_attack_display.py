#!/usr/bin/env python3
"""Fast regression tests against primary interfaces, preserving the dirty analyzer."""
from pathlib import Path
import argparse
import re
import subprocess
from publish_next_detection import git
from routing_duration_baseline import ROOT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--continuity',action='store_true')
    args=parser.parse_args()
    stem='piano_attack_continuity' if args.continuity else 'piano_attack_display'
    directory=ROOT/'build'/(stem+'_test')
    directory.mkdir(parents=True,exist_ok=True)
    pending=['analyzer.hpp','joint_grace_restore.hpp']
    seen=set()
    while pending:
        name=pending.pop()
        if name in seen:
            continue
        seen.add(name)
        assert '..' not in Path(name).parts
        text=git('show','HEAD:src/'+name)
        target=directory/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text)
        pending.extend(re.findall(r'^#include "([^"]+)"',text,re.MULTILINE))
    (directory/(stem+'.hpp')).write_bytes((ROOT/'src'/(stem+'.hpp')).read_bytes())
    binary=directory/'test'
    subprocess.run(['g++','-O2','-std=c++17','-I'+str(directory),str(ROOT/'tests'/(stem+'.cpp')),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
    print('First-hit eligibility, const tracking, missing evidence, duplicate and occupied-row preservation passed',flush=True)


if __name__=='__main__':
    main()
