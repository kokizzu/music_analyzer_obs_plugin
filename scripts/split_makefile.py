#!/usr/bin/env python3
"""Plan, apply, verify and publish an order-preserving Makefile split."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'build/makefile_split/plan.json'
MAINTENANCE = '''\n.PHONY: plan-makefile-split apply-makefile-split verify-makefile-split publish-makefile-split test-makefile-source
plan-makefile-split: scripts/split_makefile.py
\t$(PYTHON) scripts/split_makefile.py plan
apply-makefile-split: scripts/split_makefile.py
\t$(PYTHON) scripts/split_makefile.py apply
verify-makefile-split: scripts/split_makefile.py
\t$(PYTHON) scripts/split_makefile.py verify
publish-makefile-split: scripts/split_makefile.py
\t$(PYTHON) scripts/split_makefile.py publish
test-makefile-source: tests/test_makefile_source.py scripts/makefile_source.py
\t$(PYTHON) tests/test_makefile_source.py
'''


def git(*args, data=None):
    result = subprocess.run(['git', *args], cwd=ROOT, input=data, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def shebang_first(text):
    lines = text.splitlines(True)
    for i, line in enumerate(lines):
        if line.startswith('#!'):
            return line + ''.join(lines[:i] + lines[i + 1:])
    return text


def clean_adapter_whitespace(text):
    return ''.join(line.rstrip(' \t\n') + ('\n' if line.endswith('\n') else '') if 'read_makefile(' in line else line for line in text.splitlines(True))


def split(text):
    lines = text.splitlines(True)
    chunks, start, depth = [], 0, 0
    continuation = False
    for i, line in enumerate(lines):
        word = line.strip().split(' ', 1)[0]
        if not line.startswith('\t') and not continuation:
            if word in ('define', 'ifdef', 'ifndef', 'ifeq', 'ifneq'):
                depth += 1
            elif word in ('endef', 'endif'):
                depth -= 1
        if not depth and not continuation and not line.strip() and i - start >= 900:
            # A blank inside a recipe does not terminate its rule.
            following = next((x for x in lines[i + 1:] if x.strip()), '')
            if not following.startswith('\t'):
                chunks.append(''.join(lines[start:i + 1]))
                start = i + 1
        continuation = line.rstrip('\n').endswith('\\')
    assert depth == 0 and not continuation
    chunks.append(''.join(lines[start:]))
    assert ''.join(chunks) == text
    sections = {f'make/sections/rules-{i:02}.mk': chunk for i, chunk in enumerate(chunks, 1)}
    loader = '# Ordered Makefile sections; definition order is significant.\n# See make/README.md. Use scripts/makefile_source.py for source inspection.\n'
    loader += ''.join('include ' + name + '\n' for name in sections)
    return {'Makefile': loader, **sections}


def adapt(text, test=False):
    """Adapt only statically identified Makefile reads, leaving other I/O alone."""
    if 'Makefile' not in text:
        return text
    tree = ast.parse(text)
    aliases = set()
    def is_make(node):
        return any(isinstance(n, ast.Constant) and n.value == 'Makefile' for n in ast.walk(node)) or isinstance(node, ast.Name) and node.id in aliases
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and is_make(node.value):
            aliases.update(target.id for target in node.targets if isinstance(target, ast.Name))
    lines = text.splitlines(True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode()))
    raw = text.encode()
    edits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'read_text':
            value = ast.get_source_segment(text, node.func.value)
            original = ast.get_source_segment(text, node)
            arguments = original[original.index('.read_text(') + len('.read_text('):-1]
            replacement = 'read_makefile(' + value + (', ' + arguments if arguments else '') + ')'
            edits.append((offsets[node.lineno - 1] + node.col_offset, offsets[node.end_lineno - 1] + node.end_col_offset, replacement.encode()))
    if not edits:
        return text
    for begin, end, replacement in sorted(edits, reverse=True):
        raw = raw[:begin] + replacement + raw[end:]
    result = raw.decode()
    tree = ast.parse(result)
    position = 0
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) or isinstance(node, ast.ImportFrom) and node.module == '__future__':
            position = node.end_lineno
        else:
            break
    lines = result.splitlines(True)
    bootstrap = ''
    if test:
        bootstrap = "import sys as _makefile_sys\nfrom pathlib import Path as _MakefilePath\n_makefile_sys.path.insert(0, str(_MakefilePath(__file__).resolve().parents[1] / 'scripts'))\n"
    lines.insert(position, bootstrap + 'from makefile_source import read_makefile\n')
    result = ''.join(lines)
    ast.parse(result)
    return clean_adapter_whitespace(shebang_first(result))


def database(makefile, wrapper):
    wrapper.write_text('include ' + str(makefile) + '\n.PHONY: __verify_ordered_makefile_split\n__verify_ordered_makefile_split:\n')
    result = subprocess.run(['make', '--no-print-directory', '-p', '-f', str(wrapper), '__verify_ordered_makefile_split'], cwd=ROOT, capture_output=True, text=True, check=True)
    # Source locations and MAKEFILE_LIST necessarily change; rule and variable
    # values, including the default goal and recipes, must remain identical.
    included = re.search(r'^MAKEFILE_LIST := (.*)$', result.stdout, re.M).group(1).split()
    text = '\n'.join(line for line in result.stdout.splitlines() if not line.startswith('#') and not line.startswith('MAKEFILE_LIST :='))
    # GNU Make's hash table enumerates targets in a different order when the
    # new include-file entries are inserted. Compare complete rule/variable
    # blocks, preserving prerequisite and recipe order within each block.
    blocks = [block.strip('\n') for block in text.split('\n\n') if block.strip()]
    blocks = [block for block in blocks if block not in {name + ':' for name in [*included, 'Makefile', 'GNUmakefile']}]
    return '\n\n'.join(sorted(blocks))


def verify(state):
    for p, text in state['working'].items():
        if p.startswith('scripts/stage_'):
            assert (ROOT / p).read_text() == state['before'][p]
            continue
        text = clean_adapter_whitespace(shebang_first(text)) if p.endswith('.py') else text
        if p == 'scripts/list_make_targets.py':
            text = text.replace('    parser.add_argument("--pattern", default=".")\n', '    parser.add_argument("--pattern", default=".")\n    parser.add_argument("legacy_file", nargs="?")\n    parser.add_argument("legacy_pattern", nargs="?")\n')
            text = text.replace('re.compile(args.pattern, re.IGNORECASE)', 're.compile(args.legacy_pattern if args.legacy_pattern is not None else args.pattern, re.IGNORECASE)')
            text = text.replace('Path(args.file)', 'Path(args.legacy_file or args.file)')
        assert (ROOT / p).read_text() == text, p
    joined = ''.join((ROOT / p).read_text() for p in state['working'] if p.startswith('make/sections/'))
    assert joined == state['original'], 'Section content/order changed'
    with tempfile.TemporaryDirectory(prefix='makefile-verify-') as temporary:
        folder = Path(temporary)
        original = folder / 'original.mk'
        original.write_text(state['original'])
        before = database(original, folder / 'before.mk')
        after = database(ROOT / 'Makefile', folder / 'after.mk')
        # Wall-clock/database statistics are printed as comments and excluded.
        if before != after:
            (STATE.parent / 'database.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True))))
            raise RuntimeError('Make database differs: build/makefile_split/database.diff')
        gnu = folder / 'original-gnu.mk'
        gnu.write_text((ROOT / 'GNUmakefile').read_text().replace('include Makefile', 'include ' + str(original), 1))
        gnu_before, gnu_after = database(gnu, folder / 'gnu-before.mk'), database(ROOT / 'GNUmakefile', folder / 'gnu-after.mk')
        if gnu_before != gnu_after:
            (STATE.parent / 'gnu-database.diff').write_text(''.join(difflib.unified_diff(gnu_before.splitlines(True), gnu_after.splitlines(True))))
            raise RuntimeError('GNUmakefile database differs: build/makefile_split/gnu-database.diff')
        primary_before = folder / 'primary-before.mk'
        primary_text = git('show', state['head'] + ':Makefile') + MAINTENANCE
        primary_before.write_text(primary_text)
        primary_sections = {p: text for p, text in state['primary'].items() if p.startswith('make/sections/')}
        assert ''.join(primary_sections.values()) == primary_text
        for p, text in primary_sections.items():
            destination = folder / p
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text)
        primary_after = folder / 'primary-after.mk'
        primary_after.write_text(state['primary']['Makefile'].replace('include make/sections/', 'include ' + str(folder / 'make/sections') + '/'))
        assert database(primary_before, folder / 'primary-wrapper-before.mk') == database(primary_after, folder / 'primary-wrapper-after.mk'), 'Primary Makefile database differs'
        test = ROOT / 'tests/test_measure_analyzer_patterns_makefile.py'
        if test.exists():
            spec = importlib.util.spec_from_file_location('split_existing_contract', test)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            outcomes = []
            for source in (original, ROOT / 'Makefile'):
                module.MAKEFILE = source
                try:
                    module.main()
                    outcomes.append('passed')
                except AssertionError as error:
                    outcomes.append(str(error))
            assert outcomes[0] == outcomes[1], 'Existing recipe contract changed'
            print('Existing recipe contract (before/after):', outcomes[0])
    for path in state['working']:
        if path.endswith('.py'):
            ast.parse((ROOT / path).read_text())
    print('Verified byte-identical ordered content and identical GNU Make rule/variable database')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['plan', 'apply', 'verify', 'publish'])
    args = parser.parse_args()
    if args.mode == 'plan':
        assert not git('diff', '--cached', '--name-only').strip(), 'Preserve staged work'
        original = (ROOT / 'Makefile').read_text()
        assert '# Ordered Makefile sections' not in original
        working = split(original)
        primary = split(git('show', 'HEAD:Makefile') + MAINTENANCE)
        for path in [*(ROOT / 'scripts').glob('*.py'), *(ROOT / 'tests').glob('*.py')]:
            if path.name in ('split_makefile.py', 'makefile_source.py', 'deduplicate_make_targets.py') or path.name.startswith(('manage_', 'publish_', 'stage_')):
                continue
            text = path.read_text()
            try:
                updated = adapt(text, path.parent.name == 'tests')
            except (SyntaxError, UnicodeError):
                continue
            if updated != text:
                working[str(path.relative_to(ROOT))] = updated
                name = str(path.relative_to(ROOT))
                if git('ls-files', '--', name).strip():
                    baseline = git('show', 'HEAD:' + name)
                    converted = adapt(baseline, path.parent.name == 'tests')
                    if converted != baseline:
                        primary[name] = converted
        for name in ('scripts/split_makefile.py', 'scripts/makefile_source.py', 'make/README.md', 'tests/test_makefile_source.py'):
            primary[name] = (ROOT / name).read_text()
        state = dict(head=git('rev-parse', 'HEAD').strip(), original=original, working=working, primary=primary,
                     before={p: (ROOT / p).read_text() if (ROOT / p).exists() else None for p in working})
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state, indent=2) + '\n')
        print(json.dumps(dict(sections=len([p for p in working if p.endswith('.mk')]), consumers=len(working)-len(split(original)),
                             files=list(working), backup=str(STATE.relative_to(ROOT))), indent=2))
        return
    state = json.loads(STATE.read_text())
    if args.mode == 'apply':
        assert all(((ROOT / p).read_text() if (ROOT / p).exists() else None) == before for p, before in state['before'].items())
        for p, text in state['working'].items():
            destination = ROOT / p
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + '.split-tmp')
            temporary.write_text(text)
            temporary.replace(destination)
        verify(state)
        return
    verify(state)
    if args.mode == 'verify':
        return
    state['primary']['scripts/split_makefile.py'] = Path(__file__).read_text()
    state['primary']['scripts/list_make_targets.py'] = (ROOT / 'scripts/list_make_targets.py').read_text()
    state['primary'] = {p: text for p, text in state['primary'].items() if not p.startswith('scripts/stage_')}
    state['primary'] = {p: clean_adapter_whitespace(shebang_first(text)) if p.endswith('.py') else text for p, text in state['primary'].items()}
    from publish_next_detection import identity
    branch, remote, primary, tip = identity()
    assert git('rev-parse', 'HEAD').strip() == state['head'] == tip
    staged = set(git('diff', '--cached', '--name-only').splitlines())
    if staged:
        assert staged == set(state['primary']), 'Preserve unrelated staged work'
        for p, text in state['primary'].items():
            if p != 'scripts/split_makefile.py':
                staged_text = git('show', ':' + p)
                assert (clean_adapter_whitespace(staged_text) if p.endswith('.py') else staged_text) == text, 'Unexpected staged content: ' + p
    for p, text in state['primary'].items():
        blob = git('hash-object', '-w', '--stdin', data=text).strip()
        existing = git('ls-files', '--stage', '--', p).split()
        mode = existing[0] if existing else '100644'
        if existing and p in state['working']:
            (ROOT / p).chmod(0o755 if mode == '100755' else 0o644)
        git('update-index', '--add', '--cacheinfo', mode + ',' + blob + ',' + p)
    # Moved sections deliberately retain the original whitespace byte for byte;
    # check newly authored/edited paths without reformatting relocated recipes.
    git('diff', '--cached', '--check', '--', '.', ':!make/sections/*')
    print(git('diff', '--cached', '--stat'))
    for p, text in state['primary'].items():
        assert git('show', ':' + p) == text
    print(git('commit', '-m', 'Split Makefile into ordered include sections and preserve source inspection'))
    print(git('push', remote, 'HEAD:' + primary))
    assert identity()[3] == git('rev-parse', 'HEAD').strip()


if __name__ == '__main__':
    main()
