# Waste patterns and the principles behind them

## Contents
- Measuring
- Concurrency sizing
- Retries and server signals
- Time-of-day effects
- Resumability and logs
- Browser automation
- Not verified

## Measuring

- Do not design around the mean: "the 99th percentile of one backend can easily become the median
  response of your frontend." Track the latency of failed requests separately: "a slow error is
  even worse than a fast error." https://sre.google/sre-book/monitoring-distributed-systems/
- Python: `statistics.quantiles(data, n=100, method="inclusive")` returns 99 cut points, so
  `[49]` is p50, `[94]` p95, `[98]` p99. `inclusive` treats the sample min and max as the 0th and
  100th percentile, which suits a description of observed runs; the default `exclusive` assumes
  the population has more extreme values than the sample. More than `n` data points are needed
  for meaningful results. https://docs.python.org/3/library/statistics.html
  A p95 from a few dozen samples is noisy: `analyze_durations.py` marks any percentile built from
  fewer than 20 successful units with `*`, meaning indicative only.

## Concurrency sizing

- Little's Law, L = λW: average items in the system = arrival rate × average time in system.
  For one group: concurrency needed = N × W / budget. It holds exactly over an interval that
  starts and ends empty, whatever the service order. Large queues add overhead and can push W
  up, so extra concurrency can make things slower.
  Little, *Operations Research* 59(3), 2011, DOI 10.1287/opre.1110.0940.
- Throughput = work in process ÷ cycle time (Hopp & Spearman, same relation).
- Adding workers when a job misses its deadline can make it worse (thundering herd); naive
  retries "can compound the problem". https://sre.google/sre-book/data-processing-pipelines/
- Theory of Constraints, five focusing steps: identify the constraint, exploit it, subordinate
  everything else to it, elevate it, repeat. Secondary source only:
  https://www.tocinstitute.org/five-focusing-steps.html

## Retries and server signals

- Capped exponential backoff with jitter; cap retries locally (token bucket); retry at a single
  point in the stack, because independent retries at every layer multiply load (the article
  gives 243x for five layers of three attempts); only retry operations that are idempotent;
  derive timeouts from a downstream latency percentile (for example p99.9).
  https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Jitter variants (Full, Equal, Decorrelated) compared:
  https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- Anti-patterns: retrying every error, including permission or configuration errors that will
  not resolve; no alerting on repeated failures. Cap both retry count and total elapsed time.
  https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_limit_retries.html
- Idempotency: attach a client request id so a retry is recognised as a duplicate.
  https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- HTTP 429 is defined in RFC 6585 and may carry `Retry-After`. Its syntax is
  `HTTP-date / delay-seconds` (RFC 9110 §10.2.3). Honour it: waiting is cheaper than being blocked.
  https://www.rfc-editor.org/rfc/rfc6585.html , https://www.rfc-editor.org/rfc/rfc9110.html ,
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After

## Time-of-day effects

Weakest-evidence area: no primary source says off-peak hours are faster in general, so a "best
window" must come from the user's own data.

- Fixed limit windows exist: for example GitHub's `x-ratelimit-reset` gives the window reset in
  UTC epoch seconds and says not to retry before it.
  https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- The IETF `RateLimit` / `RateLimit-Policy` headers are still an Internet-Draft and only hints.
  https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers
- Daily load cycles are normal (https://sre.google/sre-book/service-best-practices/). Pipelines
  that start together can collide on a shared resource; plot each one's use of it.
- Experiment design: time of day is a nuisance factor; "Block what you can, randomize what you
  cannot." https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm
- Comparing medians across several hours: Kruskal-Wallis, at least 5 samples per group.
  https://www.itl.nist.gov/div898/handbook/prc/section4/prc41.htm ,
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
  (not in the Python standard library).

## Resumability and logs

- Make units idempotent so a restart does not create corrupt or duplicate output; write partial
  progress to persistent storage and resume from it at startup; if that does not fit, split work
  into smaller tasks. https://docs.cloud.google.com/run/docs/jobs-retries
- With idempotent units you do not need exactly-once semantics; checkpoints let a pipeline skip
  expensive work it already did. Put the SLO on the sum of all stages. https://sre.google/workbook/data-processing/
- Logs are time-ordered event streams written unbuffered to stdout. https://12factor.net/logs
- OpenTelemetry log data model (stable): Timestamp, SeverityText, Body, Attributes, and others.
  Unit id, group id, status and duration go in Attributes. https://opentelemetry.io/docs/specs/otel/logs/data-model/

## Browser automation

- Actions auto-wait for visible, stable, receives-events, enabled and editable.
  https://playwright.dev/docs/actionability
- `waitForTimeout`: "Never wait for timeout in production. Tests that wait for time are
  inherently flaky." Wait on a signal (network event, visible selector). https://playwright.dev/docs/api/class-page
- Block requests you do not need with `route.abort()`. Enabling routing disables the HTTP cache,
  and Service Worker requests are not intercepted (use `serviceWorkers: 'block'`).
  https://playwright.dev/docs/network
- Contexts are "fast and cheap to create and are completely isolated": prefer a new context per
  unit over a new browser. https://playwright.dev/docs/browser-contexts
- Playwright Test workers are separate OS processes, each with its own browser.
  https://playwright.dev/docs/test-parallel
- Reuse a saved `storageState` instead of logging in every time; it holds sensitive cookies, so
  never commit it. https://playwright.dev/docs/auth

## Not verified

- General claims about off-peak speed; the claim that service types peak at particular times.
- Exact jitter formulas (images on the source page).
- Theory of Constraints from its original author.
- Official guidance on staggering cron or top-of-the-hour start times.
