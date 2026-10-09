# CI Failure Analysis

Claude Code skill that analyses CI/CD run history and logs, ranks failure classes by wasted minutes, classifies each into a root-cause category (dependency drift, runner image change, cache, permissions, timeout, rate limit, flaky test and more) and recommends permanent fixes, rejecting quick workarounds such as blind re-runs, `continue-on-error` or added sleeps.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/ci-cd/ci-failure-analysis" ~/.claude/skills/ci-failure-analysis
```

## Triggers

Red or flaky pipeline; GitHub Actions or GitLab CI errors; "it passes when I re-run"; deploy failures; how to stop CI errors from recurring.

## Structure

```
ci-failure-analysis/
├── SKILL.md                        # collect, rank, classify, reject quick fixes, root cause, report
├── scripts/summarize_runs.py       # reads `gh run list --json`; failure rate, wasted minutes, flake signals, --selftest
├── references/failure-catalog.md   # symptom -> cause -> permanent fix, gh and API details, sources
└── evals/evals.json                # test prompts and expectations
```

```bash
gh run list --limit 200 --json databaseId,workflowName,conclusion,headSha,headBranch,event,attempt,startedAt,updatedAt \
  | python3 scripts/summarize_runs.py
```
