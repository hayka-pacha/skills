---
name: pipeline-throughput-analysis
description: >-
  Mine the logs of a batch job, bot, crawler, scraper, ETL or any pipeline that works through many
  units of work grouped into batches, to find where time goes and how to meet a time budget per
  group. Computes per-group wall-clock time and percentiles, compares time-of-day windows, spots
  retries, fixed sleeps, serial work and slow outliers, and proposes ranked changes with expected
  gains. Use this skill whenever the user wants a pipeline or bot to finish faster, asks "what is
  slowing this down", wants to hit a target duration per batch, region, tenant or customer, asks
  whether they are running at the best time of day, or hands over run logs to analyse, even if
  they never say "throughput" or "bottleneck".
metadata:
  version: 1.0.0
---

# Pipeline Throughput Analysis

A pipeline processes **units** (the smallest piece of work) in **groups** (a batch, region,
tenant, customer, file) and the owner wants each group done within a **budget**. The job is to
turn logs into numbers, numbers into a bottleneck, and the bottleneck into a change whose effect
can be re-measured. Opinions about speed are cheap; the same CSV analysed before and after is not.

Analysis is read-only. Recommend changes; apply them only when asked. Speed-ups must respect the
other side's limits: never recommend evading rate limits, bans or bot protection. Slow down or
spread out instead.

## Workflow

### 1. Pin down the terms
Ask for anything not stated, in one message. If nobody can answer right now, state your
assumptions up front, carry on, and put the open questions at the end of the report.
- What is a **unit**, what is a **group**, and the **budget** per group (for example 20 minutes).
- Where the logs are, and what period they cover.
- Whether units inside a group run one after another or concurrently.

Compute what the budget implies. With N units per group and mean unit time W (waiting included),
the average number of units that must be in flight is **L = N × W / budget** (Little's Law). If
L is 4 and the pipeline runs 1 at a time, concurrency is the lever; if L is below 1, the pipeline
is already fast enough on average and the problem is outliers or waste. Beware: past a point,
more concurrency queues work and raises W instead of lowering it.

### 2. Extract timings into one table
Produce a CSV with a header `group,unit,start,duration_s,status`: `start` as ISO 8601,
`status` as `ok` or anything else for a failure. Write a throwaway extraction script for the
log format at hand (grep start and end lines, pair them by unit id, subtract timestamps).

If the logs have no unit id, no timestamps, or no end marker, say so first: **not being able to
measure is the first finding.** Recommend one structured log line per unit (JSON, one object per
line, written to stdout) with timestamp, group id, unit id, status and duration, and fall back to
differences between consecutive timestamps in the meantime, flagged as approximate.

### 3. Run the analysis
```
python3 <this-skill-folder>/scripts/analyze_durations.py runs.csv --budget-min 20
```
It prints groups ranked by wall-clock time (flagging those over budget), p50 and p95 of the
*successful* units, failure rate and the median time of failed units, how many other groups ran
at the same time, the median group duration by start hour with a significance test, and the
slowest units. Add `--tz-offset H` to read hours in the target's local time and `--window-h N`
for wider buckets. Read it this way:
- **Percentiles, not means.** A mean hides the slow tail that blows the budget. Failed units
  are reported apart from successful ones: a slow failure costs more than a fast one, and mixing
  them blurs both. A `*` means fewer than 20 successful units, so treat that percentile as indicative.
- **busy vs wall.** If busy time is much larger than wall time, units already overlap; if they
  are equal, everything is serial.
- **overlap.** Groups running at the same time are evidence about concurrency and shared
  limits: if slow groups do not overlap with others, contention is not the explanation.
- **Over-budget groups**: what do they share (size, region, hour, a specific slow unit)?

### 4. Time windows: be sceptical
"Is this the best time to run?" has no general answer; the data decides. Off-peak is not
automatically faster, and a target's limits may reset on a fixed window. Before trusting an hour:
- Require at least 5 groups per bucket (the script marks smaller ones with `?`).
- Control confounders. If the big groups always run in the afternoon, hour and size are tangled.
  Compare like with like (similar unit counts), or run an experiment: the same group at two
  different hours, order randomised.
- The script runs a Kruskal-Wallis test with a permutation p-value over the trusted buckets. It
  answers "do the hours differ at all?" and nothing more: it does not control for group size or
  day. Back it with a same-day comparison (groups from one day at different hours) read off the
  group table.

### 5. Hunt waste in the code and config
First confirm the code you are reading is the code that produced the logs: do the log lines,
statuses and timings match what it writes and how long its sleeps and retries would take? If
not (a different version, a wrapper, another service), say so and ask for the right one; waste
found in the wrong code is fiction. Then read it against `references/waste-patterns.md`. The
usual suspects, in order of
how often they dominate:
1. **Fixed sleeps and timeouts** where a condition exists to wait on.
2. **Retries**: on every error, no cap, no jitter, or at several layers at once.
3. **Serial work** that could overlap, up to the concurrency L from step 1 and the target's limits.
4. **Repeated setup** per unit: logging in, launching, or loading the same thing again.
5. **Unneeded work**: resources fetched and never used; units re-done that were already done.
6. **No resume**: a failure restarts the whole group instead of the failed unit.
7. **Slow outliers** holding up the group because the timeout is far above the p99.

Quantify each from the CSV (for example "units retried account for 23% of busy time") instead
of asserting it.

### 6. Report
1. **Where the time goes**: a table of the biggest consumers, from data.
2. **Verdict on timing windows**: supported, not supported, or not enough data (and what data would settle it).
3. **Ranked changes**: each with expected minutes saved per group, effort, risk, and which numbers
   you will check afterwards. Rank by saved time ÷ effort.
4. **Gap to budget**: even if everything lands, is the budget met? With k units in flight,
   wall ≈ busy ÷ k; the k needed is busy ÷ budget; the group size that fits is about
   budget ÷ mean unit time. If the budget cannot be met, say what has to give (scope, concurrency
   ceiling, group size, the budget itself).
5. **Measurement gaps**: what to log so the next analysis is better.

### 7. Verify after changes
Re-extract to the same CSV format and rerun. Success means p95 group wall-clock under budget
across enough groups, not one good run. Report before and after side by side.

## Principles

- Measure first; every claim points at a number.
- The bottleneck is wherever the time is. Speeding up anything else changes nothing.
- A faster pipeline that gets blocked is slower. Respect the other side's signals.
