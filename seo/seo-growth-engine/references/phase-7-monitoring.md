# Phase 7 — Monitoring & Iteration

SEO is not "ship and forget". Tracking what changes — and what Google does in response — is half the game.

## 7.1 GSC Monitoring Cadence

| Check | Frequency | What to watch for |
|-------|-----------|-------------------|
| **Clicks & Impressions** | Daily | Sudden drops (penalty/deindex), spikes (new SERP feature) |
| **CTR by query** | Weekly | High-impression low-CTR opportunities (rewrite title/meta) |
| **Position changes** | Weekly | Pages newly in positions 5-20 with volume = quick wins |
| **Index coverage** | Monthly | Crawl errors, excluded pages, "Discovered – currently not indexed" |
| **Core Web Vitals** | Monthly | Field data regressions (only field data, not lab) |
| **Sitemaps** | Monthly | Error/warning counts, drift from intended URL set |

## 7.2 Quick Win Formula

```
Quick Win Score = Impressions × (1 - CTR) × (1 / Position)
```

High score = lots of impressions, low CTR (so title/meta probably weak), decent position (so realistic to improve). Pages with this profile are where small effort yields biggest gains.

Sort GSC's queries report by this score. Top 20 = your weekly optimization queue.

## 7.3 SEO Testing Discipline

- **Change ONE variable at a time.** Title, meta, schema, internal links — never simultaneously.
- **Wait 2-4 weeks** before evaluating. Google's re-crawl + re-ranking cycle is slow.
- **Compare 30-day windows** before vs after. Account for seasonality and weekday effects.
- **Track at page and query level**, not just site-wide. Site-wide averages hide everything.
- **Document the change** — what, when, why. Future you will not remember.

## 7.4 Diagnosing a Traffic Drop

Methodical order:
1. **GSC manual actions** — check for penalties. Rare but instant fix priority if present.
2. **GSC coverage** — pages dropping out of index?
3. **Algorithm update timing** — match drop date against known Google updates (Search Engine Land, Search Engine Roundtable).
4. **Specific query loss** — which queries dropped? Suggests intent shift or competitor wins.
5. **Specific page loss** — which pages dropped? Look for technical changes (URL change, redirect, deindex tag).
6. **Server logs** — Googlebot crawl frequency change?
7. **Backlink loss** — Ahrefs/Semrush, sudden referring-domain drop?
8. **Seasonal/news** — is the drop industry-wide or just you?

Don't panic-redesign before diagnosing. Most drops have a specific cause.

## 7.5 Tools

- **Google Search Console** — free, primary source of truth for what Google sees
- **Bing Webmaster Tools** — free, often ignored, gives 5-10% more search traffic
- **IndexNow** — push new URLs to Bing/Yandex instantly. Free.
- **Ahrefs / Semrush** — paid, competitive intelligence and backlink data
- **Screaming Frog** — desktop crawler, finds technical issues fast
- **PageSpeed Insights** — combined lab + field CWV data
- **GA4 / Plausible / Fathom** — user-side analytics, complements GSC's search-side view

## Sources

GSC Help, Search Engine Land update timeline, Ahrefs analytics guides. Full list in `sources.md`.
