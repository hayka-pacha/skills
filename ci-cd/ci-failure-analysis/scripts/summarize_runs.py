#!/usr/bin/env python3
"""Summarise GitHub Actions runs to show where CI time and failures concentrate.

Input: JSON from `gh run list --json ... --limit N` (file path or stdin). Needed fields:
  workflowName, conclusion, headSha, event, attempt, startedAt, updatedAt
Optional: databaseId, headBranch, url (shown for the costliest failures).

    gh run list --limit 200 --json databaseId,workflowName,conclusion,headSha,headBranch,event,attempt,startedAt,updatedAt,url \\
      | python3 <skill-folder>/scripts/summarize_runs.py
    python3 <skill-folder>/scripts/summarize_runs.py --selftest

Per workflow: runs, failure rate, median duration, minutes burned by failed runs, runs that
passed only on a later attempt, share of commits that hit a failure or a re-run, and cancelled
runs (a hang someone cancels by hand shows up here, not as a failure).

Limits: `gh run list` returns only the LATEST attempt of each run, so the failed first attempts of
runs that later went green are not in wasted_min; retry_ok counts them. Durations are wall-clock
(queueing included) and so are upper bounds.
"""
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime

FAIL = {"failure", "timed_out", "startup_failure"}
DONE = FAIL | {"success"}


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def minutes(run):
    return (ts(run["updatedAt"]) - ts(run["startedAt"])).total_seconds() / 60


def usable(r):
    return r.get("startedAt") and r.get("updatedAt")


def summarize(runs):
    by_wf = defaultdict(list)
    for r in runs:
        if usable(r) and (r.get("conclusion") in DONE or r.get("conclusion") == "cancelled"):
            by_wf[r["workflowName"]].append(r)
    rows = []
    for wf, all_rs in by_wf.items():
        cancelled = [r for r in all_rs if r["conclusion"] == "cancelled"]
        rs = [r for r in all_rs if r["conclusion"] in DONE]
        if not rs:
            continue
        failed = [r for r in rs if r["conclusion"] in FAIL]
        bad_commits, commits = set(), set()
        for r in rs:
            commits.add(r["headSha"])
            if r["conclusion"] in FAIL or (r.get("attempt") or 1) > 1:
                bad_commits.add(r["headSha"])
        rows.append({
            "workflow": wf, "runs": len(rs), "failed": len(failed),
            "fail_pct": 100 * len(failed) / len(rs),
            "median_min": statistics.median(minutes(r) for r in rs),
            "wasted_min": sum(minutes(r) for r in failed),
            "retry_passes": sum(1 for r in rs if r["conclusion"] == "success" and (r.get("attempt") or 1) > 1),
            "bad_commit_pct": 100 * len(bad_commits) / len(commits),
            "cancelled": len(cancelled), "cancelled_min": sum(minutes(r) for r in cancelled),
            "worst": sorted(failed, key=minutes, reverse=True)[:3],
        })
    return sorted(rows, key=lambda x: -(x["wasted_min"] + x["cancelled_min"]))


def main():
    if "--selftest" in sys.argv:
        return selftest()
    src = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
    rows = summarize(json.load(src))
    if not rows:
        sys.exit("no completed runs in input")
    print(f"{'workflow':<28}{'runs':>5}{'fail%':>7}{'med_min':>9}{'wasted_min':>11}{'retry_ok':>9}{'bad_commit%':>12}{'cancel':>7}{'cancel_min':>11}")
    for r in rows:
        print(f"{r['workflow'][:27]:<28}{r['runs']:>5}{r['fail_pct']:>7.0f}{r['median_min']:>9.1f}"
              f"{r['wasted_min']:>11.1f}{r['retry_passes']:>9}{r['bad_commit_pct']:>12.0f}{r['cancelled']:>7}{r['cancelled_min']:>11.1f}")
    print("\nwasted_min   = minutes spent in failed runs (latest attempt only; earlier failed attempts are not visible)")
    print("retry_ok     = runs that passed only on a later attempt (transient or flaky)")
    print("bad_commit%  = commits where a run failed or needed a re-run (what 'it fails one time in three' feels like)")
    print("cancel_min   = minutes in cancelled runs: manual cancels of hangs, or concurrency cancelling superseded runs")
    for r in rows[:3]:
        for w in r["worst"]:
            print(f"costliest failure: {r['workflow']} run {w.get('databaseId', '?')} ({minutes(w):.0f} min) "
                  f"branch={w.get('headBranch', '?')} event={w['event']} {w.get('url', '')}"
                  f"\n  -> gh run view {w.get('databaseId', '<id>')} --log-failed")


def selftest():
    def run(wf, concl, sha, start, end, attempt=1):
        return {"workflowName": wf, "conclusion": concl, "headSha": sha, "event": "push", "attempt": attempt,
                "startedAt": f"2026-03-02T{start}:00Z", "updatedAt": f"2026-03-02T{end}:00Z"}
    runs = [
        run("build", "success", "a", "10:00", "10:05"),
        run("build", "failure", "b", "10:10", "10:40"),
        run("build", "failure", "b2", "10:41", "10:46"),
        run("build", "success", "c", "11:00", "11:05", attempt=2),  # passed on retry
        run("deploy", "success", "a", "10:06", "10:08"),
        run("deploy", "cancelled", "z", "10:06", "10:56"),  # a hang cancelled by hand
        run("lint", "cancelled", "z", "10:06", "10:07"),    # only cancelled runs: no row
    ]
    rows = {r["workflow"]: r for r in summarize(runs)}
    b = rows["build"]
    assert b["runs"] == 4 and b["failed"] == 2 and b["wasted_min"] == 35 and b["retry_passes"] == 1
    assert b["bad_commit_pct"] == 75, b["bad_commit_pct"]  # b, b2 failed; c needed a retry; a clean
    assert [w["headSha"] for w in b["worst"]] == ["b", "b2"], "costliest failure first"
    assert rows["deploy"]["fail_pct"] == 0 and rows["deploy"]["cancelled"] == 1 and rows["deploy"]["cancelled_min"] == 50
    assert "lint" not in rows
    assert summarize(runs)[0]["workflow"] == "deploy", "ranked by wasted + cancelled minutes (50 > 35)"
    print("selftest ok")


if __name__ == "__main__":
    main()
