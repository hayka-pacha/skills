# Failure catalog

Written for GitHub Actions; GitLab equivalents are noted where they differ. Every row is a
pattern to *confirm in the logs*, not a diagnosis by symptom alone.

## Contents
- Catalog: symptom, cause, permanent fix
- Details worth knowing
- Flaky tests
- Post-incident method
- Not verified

## Catalog

| Category | Log symptom | Permanent fix |
|---|---|---|
| Dependency or tool drift | `npm ci` reports package.json and lockfile out of sync; a previously green build breaks with no code change | Commit the lockfile; install with `npm ci`; pin tool versions via `setup-*` inputs or a version file |
| Runner image change | Failure starts with no repo change; tool versions differ in the "Set up job" log | Pin an OS version (for example `ubuntu-24.04`) instead of `-latest`; read the runner-images release notes before moving |
| Cache | Miss on every run, or a stale restore | Key on `hashFiles('<lockfile>')`; order `restore-keys` most to least specific; a job must still work with no cache |
| Permissions or token | `403`, `Resource not accessible by integration`; OIDC token request fails | Find the one scope the failing call needs and grant only that, on that job (commenting on a PR through the issue-comments endpoint accepts `pull-requests: write` or `issues: write`); `id-token: write` for OIDC; trust policy that matches the token's `sub`. Never `write-all`. First check the repository's default "Workflow permissions" setting and the permissions the run actually received |
| Timeout | Job cancelled at its limit | Find the slow or hung step; set an explicit `timeout-minutes` (default is 360) |
| Concurrency collision | Runs cancelled unexpectedly; two deploys overlap | `concurrency` group with the right `cancel-in-progress`; queue deploys instead of cancelling them |
| Network or registry unreachable | `ETIMEDOUT`, `ECONNRESET`, DNS or TLS errors, registry pull limits, a step that hangs on "connecting" | Bounded retry with backoff on the network call only, a step-level timeout, and a mirror or cache for the registry; confirm an outage or limit on the provider's status page before changing code |
| Rate limit | `403` or `429`; `x-ratelimit-remaining: 0` | Authenticate requests; cache API responses; wait for `x-ratelimit-reset`; honour `retry-after`; capped exponential backoff |
| Fork or Dependabot PR | A secret is empty; token is read-only; a comment or label step gets 403 | These runs get a read-only token and no Actions secrets, and a `permissions:` block cannot grant them write access. Design the workflow to need neither; split privileged work into a `workflow_run` stage (Dependabot-triggered runs read Dependabot secrets, not Actions secrets) |
| Skipped required check | PR stuck on "Waiting for status" | Always run the workflow and skip by job-level `if:`; avoid requiring workflows that can be skipped by path or branch filters |
| Syntax or expression | "Invalid workflow file"; an expression evaluates empty | actionlint in pre-commit and in CI |
| Flaky test | Same commit passes and fails | Track the rate, quarantine with an owner, fix the root cause; retries only as labelled mitigation. To reproduce: loop the single test (`for i in $(seq 200); do <test> || break; done`), then add load or pin it to one CPU to widen a race |

## Details worth knowing

- **Token permissions**: a repository's "Workflow permissions" setting offers a restricted default
  (read access to `contents` and `packages` only); an organisation can set the default, and a more
  restrictive organisation default disables the permissive option; the `permissions:` key in a
  workflow overrides it.
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- **Fork and Dependabot runs**: for pull requests from forks the `permissions:` key "can add and
  remove read permissions" but typically cannot grant write access, with one exception: a
  repository admin can enable "Send write tokens to workflows from pull requests". Without it,
  write permissions are reduced to read-only. `pull_request_target` runs with read/write
  permission, which is why untrusted PR code must never be checked out there. Dependabot pull
  request runs "run as if they are from a forked repository": read-only token, no Actions secrets.
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- **Which scope for a PR comment**: `POST /repos/{owner}/{repo}/issues/{issue_number}/comments`
  accepts either Issues write or Pull requests write.
  https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens
- **See what the run received**: the "Set up job" step of the log lists the `GITHUB_TOKEN`
  permissions. This is observed in logs; the documentation pages read do not state it.

- **Re-runs** keep the same `GITHUB_SHA` and `GITHUB_REF`; allowed for 30 days, at most 50 times.
  https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
- **`gh run rerun --job`** needs the job's `databaseId` from `gh run view --json jobs`, not the number in the browser URL.
  https://cli.github.com/manual/gh_run_rerun
- **`gh run view`**: `--log-failed` shows failed steps only; `-j <jobID>` selects a job; `--exit-status`
  exits non-zero on failure; `--json` fields include `jobs`, `conclusion`, `attempt`, `headSha`,
  `workflowName`, `startedAt`, `updatedAt`. https://cli.github.com/manual/gh_run_view , https://cli.github.com/manual/gh_run_list
- **Job and step timings** via REST: `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`
  (`started_at`, `completed_at`, `conclusion`, `runner_name`, `labels`). Log endpoints return a
  302 whose link expires after 1 minute. https://docs.github.com/en/rest/actions/workflow-jobs
- **Debug logging**: secret or variable `ACTIONS_STEP_DEBUG=true` (step debug) and
  `ACTIONS_RUNNER_DEBUG=true` (runner diagnostics); one debug re-run enables both without changing
  settings. https://docs.github.com/en/actions/how-tos/monitor-workflows/enable-debug-logging
- To debug an `if:` condition, read `JOB/system.txt` in the downloaded log archive for the
  "Expanded" values. Path filters only consider the first 3,000 changed files.
  https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
- **`npm ci`** errors when `package.json` and the lockfile disagree and never writes either file.
  https://docs.npmjs.com/cli/v10/commands/npm-ci . `setup-node` recommends always giving
  `node-version` (or `node-version-file`) instead of using the runner's system Node.
  https://github.com/actions/setup-node
- **`-latest` images** migrate over one to two months; maintainers advise pinning an OS version.
  The "Set up job" log records the exact image. https://github.com/actions/runner-images
- **Cache**: contents are immutable (new content needs a new key); saved only if the job
  succeeds; unused entries evicted after 7 days; default cap 10 GB; `hashFiles` returns an empty
  string when nothing matches, giving a constant key.
  https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching ,
  https://docs.github.com/en/actions/reference/workflows-and-actions/expressions
- **Permissions**: unspecified scopes in a `permissions:` block become `none`; `permissions: {}`
  disables all. Prefer OIDC over stored cloud secrets (short-lived, single-job tokens). Events
  triggered by `GITHUB_TOKEN` generally do not start new workflow runs.
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax ,
  https://docs.github.com/en/actions/concepts/security/openid-connect ,
  https://docs.github.com/en/actions/concepts/security/github_token
- **Fork PRs**: secrets are not passed and `GITHUB_TOKEN` is read-only. Avoid `pull_request_target`
  unless needed and never check out untrusted PR code with it.
  https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows ,
  https://docs.github.com/en/actions/reference/security/secure-use
- **Concurrency**: `group` plus `cancel-in-progress`, with a fallback such as
  `github.head_ref || github.run_id`; for deployments a shared group with `queue: max` queues
  instead of cancelling (confirm that option against the current docs before using it).
  https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- **Rate limits**: `GITHUB_TOKEN` gets 1,000 requests/hour per repository; a limit hit returns 403
  or 429; wait for `x-ratelimit-reset`, honour `retry-after`, back off exponentially with a cap.
  https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- **Skipped required checks**: a workflow skipped by path, branch or commit-message filters leaves
  its check Pending and blocks merge; a job skipped by `if:` reports Success. GitHub's advice:
  "Avoid requiring workflows that can be skipped."
  https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- **Pin actions to a full commit SHA**: "the only way to use an action as an immutable release";
  Dependabot can raise version-update PRs for actions.
  https://docs.github.com/en/actions/reference/security/secure-use ,
  https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot
- **actionlint**: https://github.com/rhysd/actionlint and its usage doc. **act** limits: https://nektosact.com/not_supported.html
- **GitLab**: job logs under CI/CD > Pipelines > job (https://docs.gitlab.com/ci/jobs/job_logs/);
  `CI_DEBUG_TRACE` exposes variables and secrets (https://docs.gitlab.com/ci/variables/variables_troubleshooting/).

## Flaky tests

From Google's testing blog (https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html):
about 1.5% of test runs were flaky and almost 16% of tests had some flakiness; about 84% of
pass-to-fail transitions in post-submit testing involved a flaky test. Their mitigations:
re-run only failing tests, auto re-run, and a "flaky" marker that fails only after three
failures in a row, which the post calls "hardly a perfect solution". Tooling auto-quarantines
very flaky tests, taking them off the critical path and filing a bug, with the warning that this
"could easily mask a real race condition". People learn to ignore alarms that have a history of
false signals. Reading for this skill: track flake rate per test, quarantine with an owner and a
bug, and treat retries as mitigation only.

## Post-incident method

- Blameless: "You can't 'fix' people, but you can fix systems and processes"; action items need
  an owner and a tracking bug; "a postmortem without subsequent action is indistinguishable from
  no postmortem". https://sre.google/sre-book/postmortem-culture/ , https://sre.google/workbook/postmortem-culture/
- Five whys is documented by AWS (back each answer with evidence, branch for multiple causes;
  blame-free): https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_testing_resiliency_rca_resiliency.html ,
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/incident-report-5whys.html .
  Google's SRE chapters leave the root-cause technique to the team.

## Not verified

- That Dependabot rewrites both the SHA and a version comment for SHA-pinned actions (the page
  fetched does not say).
- Whether a GitHub-hosted default `sub` claim format changed recently for new repositories:
  read the current OIDC page before relying on a specific format.
- The `queue: max` concurrency option: appears on the syntax page, not read in its own section.
- That the "Set up job" log lists token permissions: observed behaviour, no documentation page found.
- An official GitLab API page for job traces.
- A flake-rate threshold for quarantine: the source gives none.
