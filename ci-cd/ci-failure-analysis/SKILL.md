---
name: ci-failure-analysis
description: >-
  Analyse CI/CD run logs and failed pipelines, group the errors into root-cause categories, and
  recommend permanent fixes instead of quick-and-dirty workarounds like blind re-runs, ignoring
  failures, adding sleeps or raising timeouts. Pulls run history and failing logs with the GitHub
  CLI, ranks failure classes by wasted time, tells flaky tests from environment drift, permission
  errors, cache problems and rate limits, and says how to prevent each from coming back. Use this
  skill whenever the user pastes or mentions CI errors, a red pipeline, flaky builds, "the
  workflow keeps failing", GitHub Actions or GitLab CI logs, deploy failures, or asks how to stop
  CI errors from recurring, even if they only say "my builds are annoying".
metadata:
  version: 1.0.0
---

# CI Failure Analysis

A re-run that goes green fixed nothing; it hid the cause until next time. This skill finds the
cause and the *permanent* fix, and states the cost of each failure class so the user can see
which ones are worth fixing first.

Read-only by default. Recommend changes to workflow files; apply them only when asked.

## Workflow

### 1. Collect evidence
Use the data, not a guess from one log. With the GitHub CLI (`gh`):

```bash
# Recent history, then summarise where failures and minutes concentrate
gh run list --limit 200 --json databaseId,workflowName,conclusion,headSha,headBranch,event,attempt,startedAt,updatedAt,url \
  | python3 <this-skill-folder>/scripts/summarize_runs.py

gh run view <run-id> --log-failed          # only the failed steps' logs
gh run view <run-id> --json jobs           # job and step timings and conclusions
gh run rerun <run-id> --failed --debug     # one re-run with debug logging, when the log is too thin
```

Check that the logs you were given belong to the runs in the history (run id, workflow, commit)
before drawing conclusions from both; say so when they do not.

If the user pasted only an error and there is no repo or history, do not run the full report.
Ask for the four things that decide the answer (the event that triggered the run, whether the PR
comes from a fork, the workflow's `permissions:` block, and the failing step's log), give the
most likely class as a hypothesis, and state what would confirm it. Use the short form: cause,
permanent fix, prevention. Per-step
timings are also available from the REST API (`gh api repos/{owner}/{repo}/actions/runs/<id>/jobs`).
Debug logging comes from the `ACTIONS_STEP_DEBUG` and `ACTIONS_RUNNER_DEBUG` secrets or
variables, or a single debug re-run. For GitLab, job traces are under the pipeline's job page;
`CI_DEBUG_TRACE: "true"` is verbose and exposes variables and secrets in the log, so use it
sparingly and clean up.

### 2. Rank before diving
The summary script ranks workflows by minutes burned by failed and cancelled runs, and shows
two views of flakiness: runs that passed only on a later attempt, and the share of *commits*
that hit a failure or a re-run. The per-commit share is usually closer to how the failure rate
feels than the per-run one. `gh run list` shows only the latest attempt, so the failed first
attempts of retried runs are not in the wasted minutes: say that the cost is understated. Start
with the biggest cost, not the loudest error.

Before trusting a green history, read the workflow files for `continue-on-error`, `|| true` or
steps that swallow exit codes. Those make failures invisible, so the real failure rate is
higher than the one measured and the swallowed step is itself a finding.

### 3. Classify each failure
Use the catalog in `references/failure-catalog.md` (log symptom → cause → permanent fix). Open
the first error in the log, not the last: later errors are usually fallout. Check whether it
started at a specific commit, date or runner image change; a failure with no related repo change
points at the environment.

Separate the three questions people mix up:
- *Did my change break it?* (fails on the branch, passes on the base)
- *Did the world change?* (fails with no repo change: image, dependency, API, quota)
- *Is it intermittent?* (same commit passes and fails)

### 4. Reject the quick fixes
These make the symptom disappear and leave the cause. Do not propose them as the fix:

| Quick fix | What it actually does |
|---|---|
| Re-run until green | Hides flakiness; the failure rate stays |
| `continue-on-error`, `\|\| true`, deleting the check | Turns a signal into silence |
| `permissions: write-all` to clear a 403 | Grants every scope to every step; the failing step needs one scope |
| Adding `sleep` | Guesses at a race instead of waiting on a condition |
| Raising the timeout | Pays more for the same hang; default is 6 hours |
| Skipping or deleting the flaky test | Loses coverage; quarantine with an owner instead |

A mitigation is acceptable only if labelled as one, with an owner and an end date, next to the
real fix.

### 5. Root cause, with evidence
For each class, ask "why" until the answer is something that can be changed in the repo, the
config or the process, and back each answer with a log line or run link. Branch if there are
several causes. Stay blameless: fix systems and processes, not people. Five whys is one method
AWS documents; Google's SRE material leaves the technique to the team, so do not present it as
mandatory.

### 6. Report
For each failure class, ranked by cost:
1. **What happens** and how often (runs, minutes wasted, since when), with run links.
2. **Root cause** and the evidence for it.
3. **Permanent fix**, as a concrete change (file, key, value). Say what it costs.
4. **Prevention**: the check that would have caught it earlier (workflow linting, pinned versions,
   required check, scheduled run).
5. **Owner and effort**; and any mitigation in the meantime, marked temporary.

End with the two or three fixes that remove the most waste. Offer to prepare the workflow edits.

## Prevention that applies broadly

- Lint workflows before they run: **actionlint** checks syntax, `${{ }}` expressions, action
  inputs, `needs`, runner labels, cron and script injection. `act` runs workflows locally but
  ignores `concurrency`, `permissions`, `timeout-minutes`, `continue-on-error` and OIDC, so it
  cannot validate those.
- Pin what moves: runner image version, tool versions, lockfile-driven installs, third-party
  actions to a full commit SHA; let Dependabot propose the bumps as reviewable PRs.
- Give every job a `timeout-minutes`, and every workflow a `concurrency` policy suited to it.
- Track flake rate per test and quarantine with an owner; retries are mitigation, not a cure.
