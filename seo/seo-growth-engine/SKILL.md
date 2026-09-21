---
name: seo-growth-engine
description: "SEO methodology for auditing, planning, and fixing organic search performance — backed by 60+ authoritative sources. **Trigger aggressively** on any mention of SEO, organic traffic, search rankings, GSC/Search Console, indexation, sitemaps, robots.txt, hreflang, canonical, schema/structured data, meta tags, title tags, Core Web Vitals (LCP/INP/CLS), E-E-A-T, helpful content, scaled content, March 2024 update, programmatic SEO, affiliate quality, IndexNow, crawl budget, or Google not finding/ranking/indexing/demoting pages. Also trigger on adjacent framings users may not realize are SEO — traffic dropped, competitor outranks us, rich snippets not showing, Google shows wrong language, page rewritten in SERP, site slapped by an update, CMS/URL migration without losing rankings. Do NOT trigger for pure web scraping (use firecrawl), bundle-size/JS perf with no indexation angle (vercel-react-best-practices), browser-tab title bugs, GA4 implementation, or frontend URL-routing UX."
---

# SEO Growth Engine

A complete SEO methodology distilled from 60+ authoritative sources. Use this skill to audit, plan, or improve any website's organic search performance.

## Workflow — pick the right reference, then deliver

Identify the user's job. Read ONLY the matching reference(s) — never read all of them.

| User's situation | Read | Why |
|------------------|------|-----|
| General audit / "look at my site" | `phase-1-technical.md` + `phase-2-content.md` + `pitfalls.md` | Covers ~80% of issues. |
| Speed / CWV problem (LCP/INP/CLS) | `phase-1-technical.md` §1.2 | Optimization patterns. |
| Indexation / crawl / sitemap issues | `phase-1-technical.md` §1.1 + `phase-4-programmatic.md` §4.2 | Crawl budget + canonicals. |
| Multi-language / hreflang | `phase-3-international.md` | Return-link rule (#1 silent killer). |
| Programmatic / templated pages at scale | `phase-4-programmatic.md` + `pitfalls.md` | March 2024 scaled-content. |
| Affiliate / monetization | `phase-5-affiliate.md` | `rel=sponsored`, value-add. |
| CRO / CTAs / mobile-first | `phase-6-conversion.md` | Placement, trust, mobile. |
| GSC analysis / quick wins | `phase-7-monitoring.md` | Quick-win formula. |
| Traffic drop / "we got slapped" | `phase-7-monitoring.md` (§7.4) + `pitfalls.md` | Diagnostic order. |

If unsure which references apply, ask the user one clarifying question — don't fan out and read everything.

## Have a real audit script — use it

Before guessing at someone's setup, run the bundled audit script when a URL is available:

```bash
python3 ~/.claude/skills/seo-growth-engine/scripts/audit.py https://example.com
```

Outputs JSON with HTTP status, robots.txt presence/contents, sitemap reachability, title/meta length, canonical, hreflang cluster, JSON-LD count, h1 count, image-without-alt count. **Run this first whenever the user gives you a URL** — it gives you facts instead of asking them to read their own HTML to you.

It is pure stdlib (no install needed), single-page only, and respectful (one HEAD + one GET). Don't crawl with it.

## Response shape — answer above the fold, depth below

This is the single most important behavior in this skill. SEO replies tend to bloat into 50-item generic checklists. Don't do that.

**Structure every response like this:**

1. **The answer in 2-3 sentences.** Lead with the single most-likely diagnosis or the 1-2 highest-leverage changes. No preamble.
2. **The next concrete action** the user should take today — one command, one GSC report to open, one file to inspect.
3. **(Below)** Diagnostic order or detailed checklist for users who want depth.
4. **(Below)** Tradeoffs, caveats, time-bounds.

If the user asks a short focused question ("is X correct?"), give a short focused answer. Don't dump the workflow. Match length to question.

## Core thresholds — hold these without re-reading

| Metric | Good | Poor | Source |
|--------|------|------|--------|
| LCP | ≤ 2.5s | > 4.0s | web.dev / CrUX field data |
| INP | ≤ 200ms | > 500ms | web.dev (replaced FID Mar 2024) |
| CLS | ≤ 0.1 | > 0.25 | web.dev |
| #1 result avg word count | ~1,447 | — | Backlinko 11.8M study |
| Pages with 0 organic traffic | 96.55% | — | Ahrefs |
| 100ms speed improvement | +8.4% conv | — | Deloitte |
| Top 25% landing pages convert | > 5.31% | avg 4.02% | Unbounce |

## How to deliver SEO advice

These principles override generic-advisor instincts. They exist because most SEO advice fails by being non-specific.

1. **Diagnose before prescribing.** Ask what they're seeing (GSC data, specific URLs, current rankings) before any sweeping recommendation. SEO advice without context is usually wrong for *this* site.
2. **Pick the 2-3 levers that matter for *this* site.** Not 50 micro-optimizations. The long tail of SEO advice is the trap.
3. **Cite the source on non-obvious claims.** "Google's spam policy says..." or "Backlinko's 11.8M-result study found...". Earns trust, lets the user verify.
4. **Surface the tradeoff.** Subdirectories vs ccTLDs, pagination vs load-more, exact-match anchors — name the tradeoff so the user decides, don't decide for them.
5. **Time-bound expectations.** Most changes need 2-4 weeks for Google to re-evaluate. Say so up front — don't let the user expect Monday results.
6. **Push back when the plan is wrong.** "Launch 80K pages at once" deserves pushback, not polite agreement. State the risk, offer the safer alternative.
7. **Honest about uncertainty.** Nobody knows Google's algorithm. Frame as "documented best practice" or "industry consensus", not "this will rank you #1".

## Common pitfalls when applying this skill

- **Don't fan out the references.** A real request needs 1-2 references, not 7.
- **Don't recommend changes without seeing current state.** "Optimize your title tags" is useless without knowing what they are. Ask, or fetch the page.
- **Don't ignore the user's stack.** Next.js, WordPress, plain HTML — implementation differs. Confirm before giving code.
- **Don't bury the lede.** If the answer is "your hreflang is broken because of missing return links", say that in sentence one.
- **Don't dump the 20-item pitfalls list** when a focused diagnosis fits.

## Sources

Full list in `references/sources.md` (60+ entries: Google official, industry research, conversion/ROI, technical deep dives). Cite from this list when making claims.
