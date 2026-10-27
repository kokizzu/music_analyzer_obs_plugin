#!/usr/bin/env python3
"""Review and publish only the visual-row recipe-contract repair."""
import argparse
import importlib.util
from pathlib import Path
import re
import subprocess
import tempfile

from publish_next_detection import git, identity
from visual_row_contract import assert_visual_row_contract

ROOT = Path(__file__).resolve().parents[1]
PATHS = ['scripts/visual_row_contract.py', 'tests/test_visual_row_contract.py',
         'tests/test_measure_analyzer_patterns_makefile.py',
         'scripts/manage_visual_row_contract.py', 'make/visual_row_contract.mk']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['inspect', 'publish'])
    args = parser.parse_args()
    branch, remote, primary, tip = identity()
    print('Verified primary:', branch, remote, primary)
    print(git('diff', '--', 'tests/test_measure_analyzer_patterns_makefile.py'))
    if args.mode == 'inspect':
        print(git('log', '-3', '--format=%h %s', '--', 'make/sections/rules-02.mk', 'tests/test_measure_analyzer_patterns_makefile.py'))
        return
    assert git('rev-parse', 'HEAD').strip() == tip
    assert not git('diff', '--cached', '--name-only').strip(), 'Preserve existing staged work'
    # The exact original primary source must also pass the new metric-specific
    # assertions; do not publish a test that assumes older local analyzer work.
    loader = git('show', 'HEAD:Makefile')
    sections = re.findall(r'^include (make/sections/[^\s]+)$', loader, re.M)
    primary_source = ''.join(git('show', 'HEAD:' + name) for name in sections)
    match = re.search(r'^test-real-note-samples-full-mix-parallel-unlocked:.*(?:\n\t.*)+', primary_source, re.M)
    assert match
    assert_visual_row_contract(primary_source, match.group())
    with tempfile.TemporaryDirectory(prefix='visual-row-primary-') as folder:
        source = Path(folder) / 'primary.mk'
        source.write_text(primary_source)
        test = ROOT / 'tests/test_measure_analyzer_patterns_makefile.py'
        spec = importlib.util.spec_from_file_location('primary_visual_row_recipe_contract', test)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.MAKEFILE = source
        module.main()
    for target in ['test-visual-row-contract', 'test-measure-analyzer-patterns-target', 'test-makefile-source']:
        subprocess.run(['make', target], cwd=ROOT, check=True)
    include = 'include make/visual_row_contract.mk\n'
    makefile = loader if include in loader else loader + include
    contents = {p: (ROOT / p).read_text() for p in PATHS}
    contents['Makefile'] = makefile
    for path, content in contents.items():
        existing = git('ls-files', '--stage', '--', path).split()
        mode = existing[0] if existing else '100644'
        blob = git('hash-object', '-w', '--stdin', data=content).strip()
        git('update-index', '--add', '--cacheinfo', mode + ',' + blob + ',' + path)
    assert set(git('diff', '--cached', '--name-only').splitlines()) == set(contents)
    git('diff', '--cached', '--check')
    for path, content in contents.items():
        assert git('show', ':' + path) == content
    print(git('diff', '--cached', '--stat'))
    print(git('commit', '-m', 'Fix visual-row recipe assertions for stable metrics and VocalSet preparation'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()
    print('Published', git('rev-parse', '--short', 'HEAD').strip())


if __name__ == '__main__':
    main()
