#!/usr/bin/env python3
"""Summarise per-unit durations of a batch pipeline: per-group wall-clock vs budget,
percentiles (successful units only), failures, group overlap, time-of-day comparison.

Input CSV header (extra columns ignored):
    group,unit,start,duration_s,status
  start      ISO 8601, e.g. 2026-03-02T14:05:09+00:00 (naive = treated as UTC)
  status     optional; anything other than ok/success/done/passed counts as a failure

Usage:
    python3 <skill-folder>/scripts/analyze_durations.py runs.csv [--budget-min 20]
        [--min-samples 5] [--tz-offset 0] [--window-h 1] [--top 10]
    python3 <skill-folder>/scripts/analyze_durations.py --selftest

--tz-offset shifts start times (hours) before bucketing, to read hours in the target's local time;
--window-h widens the buckets (3 = 00-02h, 03-05h, ...). Stdlib only.
"""
import argparse
import csv
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

OK_STATUSES = {"", "ok", "success", "done", "passed"}
SMALL_N = 20  # percentiles from fewer samples are marked with * (indicative only)


def parse_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            start = datetime.fromisoformat(r["start"].strip())
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            rows.append({
                "group": r["group"].strip(), "unit": r["unit"].strip(), "start": start,
                "duration_s": float(r["duration_s"]),
                "ok": (r.get("status") or "").strip().lower() in OK_STATUSES,
            })
    return rows


def pct(values, p):
    """p-th percentile (1-99) of observed values; nan if empty."""
    if len(values) < 2:
        return values[0] if values else float("nan")
    return statistics.quantiles(values, n=100, method="inclusive")[p - 1]


def group_report(rows, budget_min, tz_offset=0, window_h=1):
    by_group = defaultdict(list)
    for r in rows:
        by_group[r["group"]].append(r)
    out = []
    for g, rs in by_group.items():
        first = min(r["start"] for r in rs)
        last = max(r["start"] + timedelta(seconds=r["duration_s"]) for r in rs)
        ok = [r["duration_s"] for r in rs if r["ok"]]
        bad = [r["duration_s"] for r in rs if not r["ok"]]
        wall = (last - first).total_seconds() / 60
        out.append({
            "group": g, "units": len(rs), "first": first, "last": last, "wall_min": wall,
            "start_hour": ((first + timedelta(hours=tz_offset)).hour // window_h) * window_h,
            "busy_min": sum(r["duration_s"] for r in rs) / 60,  # > wall_min means units overlap
            "n_ok": len(ok), "p50": pct(ok, 50), "p95": pct(ok, 95),  # successful units only
            "fail_pct": 100 * len(bad) / len(rs), "fail_med": statistics.median(bad) if bad else float("nan"),
            "over_budget": budget_min is not None and wall > budget_min,
        })
    for g in out:  # groups whose time span overlaps this one (shared-resource / concurrency evidence)
        g["overlap"] = sum(1 for h in out if h is not g and h["first"] < g["last"] and g["first"] < h["last"])
    return sorted(out, key=lambda x: -x["wall_min"])


def hour_report(groups, min_samples):
    """Median group wall-clock by start bucket. Buckets below min_samples are flagged, not trusted."""
    buckets = defaultdict(list)
    for g in groups:
        buckets[g["start_hour"]].append(g["wall_min"])
    return [(h, len(v), statistics.median(v), len(v) >= min_samples) for h, v in sorted(buckets.items())]


def rank_test(buckets, rounds=5000):
    """Kruskal-Wallis H over {label: [values]} with a permutation p-value (seeded, stdlib only).
    Answers 'do these buckets differ at all?'; it does not control for group size or day."""
    data = [(v, k) for k, vs in buckets.items() for v in vs]
    n = len(data)
    order = sorted(range(n), key=lambda i: data[i][0])
    ranks, i = [0.0] * n, 0
    while i < n:  # average ranks for ties
        j = i
        while j + 1 < n and data[order[j + 1]][0] == data[order[i]][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    labels = [k for _, k in data]
    sizes = Counter(labels)

    def stat(lbls):
        sums = defaultdict(float)
        for r, lab in zip(ranks, lbls):
            sums[lab] += r
        return 12 / (n * (n + 1)) * sum(s * s / sizes[lab] for lab, s in sums.items()) - 3 * (n + 1)

    observed, hits, rng = stat(labels), 0, random.Random(0)
    for _ in range(rounds):
        rng.shuffle(labels)
        hits += stat(labels) >= observed - 1e-9
    return observed, (hits + 1) / (rounds + 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--budget-min", type=float, help="target wall-clock minutes per group")
    ap.add_argument("--min-samples", type=int, default=5, help="min groups per hour bucket to trust it")
    ap.add_argument("--tz-offset", type=float, default=0, help="hours added to UTC before bucketing")
    ap.add_argument("--window-h", type=int, default=1, help="bucket width in hours")
    ap.add_argument("--top", type=int, default=10, help="slowest units to list")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.csv:
        ap.error("csv path required (or --selftest)")

    rows = parse_rows(args.csv)
    if not rows:
        sys.exit("no rows")
    groups = group_report(rows, args.budget_min, args.tz_offset, args.window_h)
    ok_all = [r["duration_s"] for r in rows if r["ok"]]
    bad_all = [r["duration_s"] for r in rows if not r["ok"]]

    print(f"{len(rows)} units in {len(groups)} groups; successful units: median {pct(ok_all, 50):.1f}s, "
          f"p95 {pct(ok_all, 95):.1f}s; failed units: {len(bad_all)}"
          + (f", median {statistics.median(bad_all):.1f}s" if bad_all else ""))
    print("\n== Groups, slowest first (wall = first start to last end; busy = sum of unit time) ==")
    print(f"{'group':<22}{'units':>6}{'wall_min':>9}{'busy_min':>9}{'ok_p50_s':>9}{'ok_p95_s':>10}{'fail%':>7}{'fail_med_s':>11}{'overlap':>8}  budget")
    for g in groups:
        star = "*" if g["n_ok"] < SMALL_N else " "
        print(f"{g['group'][:21]:<22}{g['units']:>6}{g['wall_min']:>9.1f}{g['busy_min']:>9.1f}{g['p50']:>9.1f}"
              f"{g['p95']:>9.1f}{star}{g['fail_pct']:>7.1f}{g['fail_med']:>11.1f}{g['overlap']:>8}  {'OVER' if g['over_budget'] else ''}")
    print(f"* fewer than {SMALL_N} successful units: percentiles are indicative only")

    label = "local" if args.tz_offset else "UTC"
    print(f"\n== Median group wall-clock by start hour ({label}, {args.window_h}h buckets); '?' = fewer than {args.min_samples} groups ==")
    buckets = defaultdict(list)
    for g in groups:
        buckets[g["start_hour"]].append(g["wall_min"])
    for h, n, med, trusted in hour_report(groups, args.min_samples):
        print(f"{h:02d}h  n={n:<4} median={med:6.1f} min {'' if trusted else '?'}")
    trusted = {h: v for h, v in buckets.items() if len(v) >= args.min_samples}
    if len(trusted) >= 2:
        h_stat, p = rank_test(trusted)
        print(f"Kruskal-Wallis across trusted buckets: H={h_stat:.2f}, permutation p={p:.4f} "
              "(do the hours differ at all? does not control for group size or day)")
    else:
        print("Not enough trusted buckets for a significance test.")

    print(f"\n== {args.top} slowest units ==")
    for r in sorted(rows, key=lambda r: -r["duration_s"])[: args.top]:
        print(f"{r['duration_s']:8.1f}s  {r['group']} / {r['unit']}{'' if r['ok'] else '  (failed)'}")


def selftest():
    import os
    import tempfile
    lines = ["group,unit,start,duration_s,status"]
    for g in range(8):  # four groups at 09h (fast), four at 15h (slow, first unit fails)
        hour, dur = (9, 30) if g < 4 else (15, 120)
        base = datetime(2026, 3, 2 + g, hour, 0, tzinfo=timezone.utc)
        for u in range(10):
            ts = base + timedelta(seconds=u * dur)
            lines.append(f"g{g},u{u},{ts.isoformat()},{dur},{'ok' if (hour == 9 or u) else 'error'}")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write("\n".join(lines))
    try:
        rows = parse_rows(f.name)
    finally:
        os.unlink(f.name)
    groups = group_report(rows, budget_min=10)
    assert len(groups) == 8
    assert [g["group"] for g in groups[:4]] == ["g4", "g5", "g6", "g7"], "slow 15h groups must rank first"
    assert all(g["over_budget"] for g in groups[:4]) and not any(g["over_budget"] for g in groups[4:])
    assert groups[0]["fail_pct"] == 10.0 and groups[0]["fail_med"] == 120 and groups[0]["n_ok"] == 9
    assert all(g["overlap"] == 0 for g in groups), "groups run on different days"
    hours = {h: med for h, _, med, _ in hour_report(groups, min_samples=4)}
    assert hours[15] > 3 * hours[9]
    buckets = defaultdict(list)
    for g in groups:
        buckets[g["start_hour"]].append(g["wall_min"])
    h_stat, p = rank_test(buckets)
    assert p < 0.05, (h_stat, p)
    shifted = group_report(rows, None, tz_offset=3, window_h=3)  # 09h->12h->bucket 12; 15h->18h->bucket 18
    assert {g["start_hour"] for g in shifted} == {12, 18}
    print("selftest ok")


if __name__ == "__main__":
    main()
