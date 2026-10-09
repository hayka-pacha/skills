# Pipeline Throughput Analysis

Claude Code skill that mines the logs of a batch job, bot, crawler or ETL pipeline to find where time goes and how to meet a time budget per group of work. Computes per-group wall-clock time and percentiles, compares time-of-day windows with sample-size caveats, finds retries, fixed sleeps, serial work and slow outliers, and ranks the changes by minutes saved.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/performance/pipeline-throughput-analysis" ~/.claude/skills/pipeline-throughput-analysis
```

## Triggers

Make a pipeline or bot faster; "what is slowing this down"; hit a target duration per batch, region or customer; "am I running at the best time of day"; analyse run logs.

## Structure

```
pipeline-throughput-analysis/
├── SKILL.md                       # terms and budget, extract CSV, analyse, windows, waste, report, verify
├── scripts/analyze_durations.py   # stdlib only; group wall-clock, percentiles, by-hour medians, --selftest
├── references/waste-patterns.md   # percentiles, Little's Law, retries, time windows, resumability, sources
└── evals/evals.json               # test prompts and expectations
```

The script reads a CSV with the header `group,unit,start,duration_s,status`:

```bash
python3 scripts/analyze_durations.py runs.csv --budget-min 20
```
