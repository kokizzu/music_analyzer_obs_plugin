#!/usr/bin/env python3
"""Sweep a conservative offline phase/BTT/Beat-This BPM consensus rule.

The neural tracker remains offline-only.  This audit only establishes whether
all three independently computed values agree on labelled stable sections; it
does not alter the OBS runtime or claim that a non-causal model is live-safe.
"""
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path


BTT_PREFIX = "BTT tempo diag\t"
BEAT_THIS_PREFIX = "Beat This tempo diag\t"


@dataclass(frozen=True)
class Row:
    corpus: str
    ident: int
    expected: float
    phase_raw: float
    phase_confidence: float
    btt_raw: float
    btt_confidence: float
    beat_this_raw: float
    already_displayed: bool


def fields(text: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in text.split("\t") if "=" in item)


def parse_phase(path: Path) -> dict[int, dict[str, str]]:
    parsed: dict[int, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if " tempo diag\t" not in line:
            continue
        row = fields(line.split("\t", 1)[1])
        if {"id", "expected", "phase_raw", "phase_confidence"} <= set(row):
            parsed[int(row["id"])] = row
    if not parsed:
        raise ValueError(f"{path}: no phase diagnostic rows")
    return parsed


def parse_prefixed(path: Path, prefix: str, name: str) -> dict[int, dict[str, str]]:
    parsed: dict[int, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            row = fields(line[len(prefix):])
            parsed[int(row["id"])] = row
    if not parsed:
        raise ValueError(f"{path}: no {name} diagnostic rows")
    return parsed


def load_rows(corpus: str, phase_path: Path, btt_path: Path, beat_this_path: Path) -> list[Row]:
    phase = parse_phase(phase_path)
    btt = parse_prefixed(btt_path, BTT_PREFIX, "BTT")
    beat_this = parse_prefixed(beat_this_path, BEAT_THIS_PREFIX, "Beat This")
    if set(phase) != set(btt) or set(phase) != set(beat_this):
        raise ValueError(f"{corpus}: phase/BTT/Beat This ids differ")
    rows: list[Row] = []
    for ident in sorted(phase):
        phase_row, btt_row, beat_row = phase[ident], btt[ident], beat_this[ident]
        expected = float(phase_row["expected"])
        if any(abs(expected - float(row["expected"])) > 0.01 for row in (btt_row, beat_row)):
            raise ValueError(f"{corpus} id {ident}: expected BPM differs")
        rows.append(
            Row(
                corpus,
                ident,
                expected,
                float(phase_row["phase_raw"]),
                float(phase_row["phase_confidence"]),
                float(btt_row["raw"]),
                float(btt_row["confidence"]),
                float(beat_row["raw"]),
                float(phase_row.get("got", "0")) > 0.0,
            )
        )
    return rows


def shown(row: Row, phase_max: float, btt_gate: float, agreement: float) -> bool:
    return (
        row.phase_confidence < phase_max
        and row.btt_confidence >= btt_gate
        and max(
            abs(row.phase_raw - row.btt_raw),
            abs(row.phase_raw - row.beat_this_raw),
            abs(row.btt_raw - row.beat_this_raw),
        ) <= agreement
    )


def correct(row: Row, tolerance: float) -> bool:
    return abs(row.beat_this_raw - row.expected) <= tolerance


def fraction(numerator: int, denominator: int) -> str:
    percent = 100.0 * numerator / denominator if denominator else 0.0
    return f"{numerator}/{denominator} ({percent:.1f}%)"


def emit(lines: list[str], output: Path | None) -> None:
    """Print an audit, or atomically publish it for the dashboard."""
    rendered = "\n".join(lines) + "\n"
    if output is None:
        print(rendered, end="")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", action="append", nargs=4,
        metavar=("NAME", "PHASE_LOG", "BTT_LOG", "BEAT_THIS_LOG"), required=True,
    )
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--phase-max", type=float, default=0.60)
    parser.add_argument("--min-expected", type=float, default=0.0,
                        help="restrict the audit to annotated BPM values at or above this floor")
    parser.add_argument("--btt-gates", default="0.00,0.15,0.25,0.35,0.45,0.55,0.60,0.70,0.80")
    parser.add_argument("--agreement-gates", default="2,4,8,12")
    parser.add_argument("--output", type=Path, help="write the complete audit atomically to this file")
    args = parser.parse_args()
    if args.tolerance < 0.0 or args.phase_max <= 0.0 or args.min_expected < 0.0:
        parser.error("tolerance/min-expected must be non-negative and phase-max must be positive")
    btt_gates = [float(value) for value in args.btt_gates.split(",")]
    agreement_gates = [float(value) for value in args.agreement_gates.split(",")]
    grouped = {
        name: load_rows(name, Path(phase), Path(btt), Path(beat_this))
        for name, phase, btt, beat_this in args.corpus
    }
    if args.min_expected > 0.0:
        grouped = {
            name: [row for row in corpus_rows if row.expected >= args.min_expected]
            for name, corpus_rows in grouped.items()
        }
    if any(not corpus_rows for corpus_rows in grouped.values()):
        parser.error("at least one corpus has no rows in the requested expected-BPM range")
    rows = [row for corpus_rows in grouped.values() for row in corpus_rows]
    lines = [
        f"three-tracker consensus sweep: corpora={len(grouped)} rows={len(rows)}"
        f" min_expected={args.min_expected:.2f}"
    ]
    viable: list[tuple[int, int, int, float, float, dict[str, tuple[int, int, int]]]] = []
    for btt_gate in btt_gates:
        for agreement in agreement_gates:
            selected = [row for row in rows if shown(row, args.phase_max, btt_gate, agreement)]
            if not selected or not all(correct(row, args.tolerance) for row in selected):
                continue
            by_corpus = {
                name: (
                    sum(correct(row, args.tolerance) for row in corpus_rows if shown(row, args.phase_max, btt_gate, agreement)),
                    sum(shown(row, args.phase_max, btt_gate, agreement) for row in corpus_rows),
                    sum(shown(row, args.phase_max, btt_gate, agreement) and not row.already_displayed for row in corpus_rows),
                )
                for name, corpus_rows in grouped.items()
            }
            if any(displayed == 0 for _correct, displayed, _new in by_corpus.values()):
                continue
            newly_revealed = sum(value[2] for value in by_corpus.values())
            viable.append((newly_revealed, len(selected), btt_gate, agreement, by_corpus))
    viable.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
    if not viable:
        lines.append("three-tracker consensus viable: none")
        emit(lines, args.output)
        return 0
    newly_revealed, displayed, btt_gate, agreement, by_corpus = viable[0]
    lines.append(
        "three-tracker consensus viable:"
        f" correct={fraction(displayed, displayed)} newly_revealed={newly_revealed}"
        f" phase_max={args.phase_max:.2f} btt_gate={btt_gate:.2f} agreement={agreement:.2f}"
    )
    for name, (hits, count, new) in by_corpus.items():
        lines.append(f"three-tracker consensus corpus: name={name} correct={fraction(hits, count)} newly_revealed={new}")
    lines.append(f"three-tracker consensus viable_rules={len(viable)}")
    emit(lines, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
