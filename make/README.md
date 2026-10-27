# Makefile layout

`Makefile` loads `sections/rules-*.mk` in explicit numeric order. Existing
`GNUmakefile`, `windows.mk` and `accuracy_next.mk` retain their entry points.
Use the same `make target` commands from the repository root.

Sections are bounded at complete top-level blocks (roughly 900 lines). Their
order preserves immediate variable expansion, conditional definitions, rule
overrides and the original default goal. Do not alphabetize the include list.
The original file mixes corpus configuration, builds, tests and diagnostics;
this first split deliberately preserves that order instead of moving rules
across assignments. Search within `make/sections/` when maintaining targets.

Source-inspection scripts use `scripts/makefile_source.py` to read the ordered
sections as one source. It does not evaluate Make syntax or expand unrelated
includes. GNU Make remains the authority for execution.

`make verify-makefile-split` checks the local migration checkpoint in
`build/makefile_split/plan.json`: concatenated sections must exactly reproduce
the original source, and GNU Make's rules, recipes and variable values must
match. The checkpoint also keeps every original file for rollback. Avoid
restoring it over subsequent edits; compare each saved file before restoring.

The migration publishes the primary branch's original contents split the same
way. Pre-existing worktree changes remain local in their corresponding sections
and source-inspection scripts.
