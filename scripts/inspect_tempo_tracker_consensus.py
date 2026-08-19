#!/usr/bin/env python3
"""Sweep a conservative phase-tracker/BTT BPM consensus rule offline."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


PHASE_PREFIX = "MAESTRO tempo diag\t"
BTT_PREFIX = "BTT tempo diag\t"


@dataclass(frozen=True)
class Row:
    corpus: str
    ident: int
    expected: float
    phase_raw: float
    phase_confidence: float
    btt_raw: float
    btt_confidence: float
    already_displayed: bool


def fields(text: str) -> dict[str, str]:
    return dict(item.split("=", 1) for item in text.split("\t") if "=" in item)


def parse_phase(path: Path) -> dict[int, dict[str, str]]:
    parsed: dict[int, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(PHASE_PREFIX):
            row = fields(line[len(PHASE_PREFIX) :])
            parsed[int(row["id"])] = row
    if not parsed:
        raise ValueError(f"{path}: no phase diagnostic rows")
    return parsed


def parse_btt(path: Path) -> dict[int, dict[str, str]]:
    parsed: dict[int, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(BTT_PREFIX):
            row = fields(line[len(BTT_PREFIX) :])
            parsed[int(row["id"])] = row
    if not parsed:
        raise ValueError(f"{path}: no BTT diagnostic rows")
    return parsed


def load_rows(corpus: str, phase_path: Path, btt_path: Path) -> list[Row]:
    phase = parse_phase(phase_path)
    btt = parse_btt(btt_path)
    if set(phase) != set(btt):
        raise ValueError(f"{corpus}: phase/BTT ids differ")
    rows: list[Row] = []
    for ident in sorted(phase):
        left, right = phase[ident], btt[ident]
        expected = float(left["expected"])
        if abs(expected - float(right["expected"])) > 0.01:
            raise ValueError(f"{corpus} id {ident}: expected BPM differs")
        rows.append(
            Row(corpus, ident, expected, float(left["phase_raw"]), float(left["phase_confidence"]),
                float(right["raw"]), float(right["confidence"]), float(left.get("got", "0")) > 0.0))
    return rows


def shown(row: Row, phase_gate: float, btt_gate: float, agreement: float) -> bool:
    return (row.phase_confidence >= phase_gate and row.btt_confidence >= btt_gate
            and abs(row.phase_raw - row.btt_raw) <= agreement)


def fraction(correct: int, total: int) -> str:
    percent = 100.0 * correct / total if total else 0.0
    return f"{correct}/{total} ({percent:.1f}%)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", action="append", nargs=3, metavar=("NAME", "PHASE_LOG", "BTT_LOG"), required=True)
    parser.add_argument("--tolerance", type=float, default=8.0)
    parser.add_argument("--phase-gates", default="0.00,0.20,0.30,0.40,0.50,0.60")
    parser.add_argument("--btt-gates", default="0.00,0.15,0.25,0.35,0.45,0.55,0.60,0.70,0.80")
    parser.add_argument("--agreement-gates", default="2,4,8,12")
    args = parser.parse_args()
    phase_gates = [float(value) for value in args.phase_gates.split(",")]
    btt_gates = [float(value) for value in args.btt_gates.split(",")]
    agreement_gates = [float(value) for value in args.agreement_gates.split(",")]
    grouped = {name: load_rows(name, Path(phase), Path(btt)) for name, phase, btt in args.corpus}
    rows = [row for corpus_rows in grouped.values() for row in corpus_rows]
    print(f"tempo consensus sweep: corpora={len(grouped)} rows={len(rows)}")
    viable: list[tuple[int, int, int, float, float, float, dict[str, tuple[int, int, int]]]] = []
    for phase_gate in phase_gates:
        for btt_gate in btt_gates:
            for agreement in agreement_gates:
                displayed = [row for row in rows if shown(row, phase_gate, btt_gate, agreement)]
                correct = sum(abs(row.btt_raw - row.expected) <= args.tolerance for row in displayed)
                if displayed and correct == len(displayed):
                    new = sum(not row.already_displayed for row in displayed)
                    by_corpus = {
                        name: (
                            sum(abs(row.btt_raw - row.expected) <= args.tolerance
                                for row in corpus_rows if shown(row, phase_gate, btt_gate, agreement)),
                            sum(shown(row, phase_gate, btt_gate, agreement) for row in corpus_rows),
                            sum(shown(row, phase_gate, btt_gate, agreement) and not row.already_displayed
                                for row in corpus_rows),
                        )
                        for name, corpus_rows in grouped.items()
                    }
                    viable.append((new, correct, len(displayed), phase_gate, btt_gate, agreement, by_corpus))
    viable.sort(key=lambda item: (-item[0], -item[1], item[3], item[4], item[5]))
    if not viable:
        print("tempo consensus viable: none")
        return 0
    best = viable[0]
    print(
        "tempo consensus viable:"
        f" correct={fraction(best[1], best[2])} newly_revealed={best[0]} phase_gate={best[3]:.2f}"
        f" btt_gate={best[4]:.2f} agreement={best[5]:.2f}"
    )
    for name, (correct, displayed, new) in best[6].items():
        print(f"tempo consensus corpus: name={name} correct={fraction(correct, displayed)} newly_revealed={new}")
    print(f"tempo consensus viable_rules={len(viable)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
