#!/usr/bin/env python3
"""Mine simple high-precision hi-hat recovery selectors from MDB window logs."""

from __future__ import annotations

from pathlib import Path

from evaluate_egmd_drum_recovery import read_events, trigger_ratio, value


FIELDS = ("seg", "band", "shape", "rms", "low", "mid", "high", "transient", "onset")


def main() -> int:
    events = read_events([Path("build/mdb_drums_windows.log")])
    positives = [event for event in events if "hihat" in event.expected and "hihat" in event.missing]
    protected = [event for event in events if "hihat" not in event.expected]
    candidates: list[tuple[int, int, str]] = []
    for field in FIELDS:
        values = sorted({value(event, "hihat", field) for event in events})
        for threshold in values:
            for operator, matches in (
                (">=", lambda event, threshold=threshold: value(event, "hihat", field) >= threshold),
                ("<=", lambda event, threshold=threshold: value(event, "hihat", field) <= threshold),
            ):
                tp = sum(matches(event) for event in positives)
                fp = sum(matches(event) for event in protected)
                if tp >= 3 and fp <= 1:
                    candidates.append((tp, -fp, f"hihat_{field}{operator}{threshold:.4g}"))
    values = sorted({trigger_ratio(event, "hihat") for event in events})
    for threshold in values:
        for operator, matches in (
            (">=", lambda event, threshold=threshold: trigger_ratio(event, "hihat") >= threshold),
            ("<=", lambda event, threshold=threshold: trigger_ratio(event, "hihat") <= threshold),
        ):
            tp = sum(matches(event) for event in positives)
            fp = sum(matches(event) for event in protected)
            if tp >= 3 and fp <= 1:
                candidates.append((tp, -fp, f"hihat_trigger_ratio{operator}{threshold:.4g}"))
    print(f"mdb_hihat_selector_events={len(events)} positives={len(positives)} protected={len(protected)}")
    for tp, negative_fp, selector in sorted(candidates, reverse=True)[:20]:
        print(f"selector={selector} tp={tp} fp={-negative_fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
