# Review checklist

Every item is something to *check in the project*, not a rule to recite. Sources are official
documentation; open them when the owner asks why.

## Contents
- Pillars
- Failure modes
- Operability
- CI/CD hygiene (GitHub Actions, with GitLab equivalents)
- Delivery metrics
- Recording decisions

## Pillars

Combined from the AWS, Google Cloud and Azure well-architected frameworks. Azure publishes a
tradeoffs page per pillar; state the tradeoff behind each recommendation the same way.

| Pillar | Ask |
|---|---|
| Reliability | Does it recover from failure on its own? Are recovery procedures ever tested? Do components share a common point of failure? Is capacity assumed or measured? Is change automated? |
| Security | Least privilege everywhere? Secrets outside the repo and rotated? Untrusted input kept out of shell and queries? |
| Operational excellence | Can an operator tell what happened from logs and signals alone? Is a deploy or rollback one command? |
| Performance | Is the slowest step known, or assumed? Is work serialised that could run concurrently? |
| Cost | Is anything paid for and unused (runners, services, retained artifacts)? |
| Sustainability | Redundant runs, over-wide triggers, always-on resources for occasional work. |

- AWS: https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html
- Google Cloud: https://docs.cloud.google.com/architecture/framework
- Azure: https://learn.microsoft.com/en-us/azure/well-architected/pillars
- AWS reliability design principles: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/design-principles.html

## Failure modes

Source: https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis

- List the critical flows, then map each internal and external dependency to find single points of failure.
- Classify each dependency as strong (flow dies without it) or weak (flow degrades). Check read and write failures separately.
- Rank by severity × likelihood and keep the result as a table.
- Timeouts and retries (https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter):
  every remote call has a timeout; retries use capped exponential backoff with jitter; retry
  at one layer only, because independent retries at each layer multiply load.
- Idempotency (https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/):
  an operation with side effects is only safe to retry if it is idempotent. If a run is
  interrupted and re-run, does work get done twice?

## Operability

- Four golden signals, from https://sre.google/sre-book/monitoring-distributed-systems/:
  latency (successes and failures separately), traffic, errors, saturation. Alert on symptoms
  users feel, not on causes.
- Twelve-factor, https://12factor.net/: config in the environment (not in code), logs as event
  streams, dev/prod parity, disposable processes (fast start, graceful stop), stateless
  processes, build/release/run kept separate.
- Structured logs (JSON with level, timestamp, unit id) are queryable; free text is not.
  https://docs.cloud.google.com/logging/docs/structured-logging
- HTTP clients: in Python's `requests`, "if no timeout is specified explicitly, requests do not
  time out", and the docs say nearly all production code should set one.
  https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts
- Batch and scheduled jobs have no port to probe, so the signal that matters is "did not run" or
  "ran and did nothing": look for a heartbeat or a run-count alert, and for output that is kept
  somewhere besides the job log.
- Health checks: a shallow liveness check without dependency calls plus a deeper readiness
  check that fails when a required dependency fails. Put a timeout on each dependency inside the
  probe, or a flaky dependency can take the probe down with it.
  https://learn.microsoft.com/en-us/azure/architecture/patterns/health-endpoint-monitoring

## CI/CD hygiene

Beyond the table below, check by reading:
- **Schedules**: a `schedule` trigger "can be delayed during periods of high loads", and high load
  includes the start of every hour, so avoid `:00`; in a public repository scheduled workflows are
  automatically disabled after 60 days without repository activity; they run only on the default
  branch; the shortest interval is 5 minutes.
  https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- **Double runs**: a workflow triggered by both `push` and `pull_request` runs twice for the same
  commit on a PR branch.
- **Deploy jobs**: branch filter, `needs` on the test job, an `environment` for approvals and
  secrets scoping, and a `concurrency` group that queues rather than cancels.
- **Shell scripts**: executable bit set in git (`git ls-files -s` shows mode 100755), and
  `set -e` so a failed step stops the script.
- **Silent success**: a job that "passes" while doing nothing (zero tests collected, a loop that
  swallows every error). Check exit codes on the paths that matter.

GitHub Actions. Sources: workflow syntax (https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions),
security hardening (https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).

| Check | Why |
|---|---|
| `permissions:` set to read-only by default, raised per job | Once any permission is set, unspecified ones become `none`; unset means the repo default, often broader than needed |
| Third-party actions pinned to a full commit SHA | The only immutable reference; tags can be moved. Confirm the SHA belongs to the action's own repo, not a fork |
| Untrusted values (`github.event.*`, branch names, PR titles) passed through an env var, never inlined as `${{ }}` in `run:` | Script injection |
| `timeout-minutes` on every job | Default is 360; a hung job burns six hours |
| `concurrency` group per workflow and ref, `cancel-in-progress` for CI but not for deploys | Stops stacked runs; cancelling a half-finished deploy is dangerous |
| `paths` / `paths-ignore` filters | Skip work that cannot be affected. They do not apply to tag pushes. Careful with required checks that never report on skipped runs |
| Cache key built from a lockfile hash | A static key never refreshes. Caches are immutable; a job must work when the cache is missing |
| Artifacts for job outputs, cache for dependencies | They are not interchangeable |
| Repeated workflow blocks turned into reusable workflows (`on: workflow_call`) | One place to edit; up to 10 nesting levels |
| `needs:` only where an ordering truly exists | Jobs without `needs` run in parallel |
| `strategy.fail-fast` and `max-parallel` chosen on purpose | Defaults are `true` and "as many as runners allow" |

GitLab equivalents (https://docs.gitlab.com/ci/yaml/): `rules` (conditional jobs), `needs`
(DAG ordering), `cache`, `interruptible` (cancel when superseded), `timeout`, `artifacts`.

## Delivery metrics

https://dora.dev/guides/dora-metrics-four-keys/ lists five metrics. Use them to judge pipeline health.

- Throughput: change lead time (commit to production), deployment frequency, failed deployment recovery time.
- Instability: change fail rate, deployment rework rate.

When the repo cannot answer these, "no way to measure lead time" is itself a finding.

## Recording decisions

Architecture Decision Records (https://adr.github.io/) capture one decision and its rationale.
Microsoft's guidance (https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record):
append-only log; never edit an accepted record, write a new one that supersedes it; include
context, options considered, decision with tradeoffs, and status. For an existing system,
writing past decisions retroactively is fine.
