---
name: seo-growth-engine
description: >
  Complete SEO audit and optimization methodology backed by 60+ authoritative sources.
  Use this skill whenever the user mentions SEO, search engine optimization, website audit,
  traffic drop diagnosis, Core Web Vitals, page speed, Google ranking, indexation issues,
  sitemaps, structured data, hreflang, international SEO, affiliate SEO, programmatic SEO,
  content strategy, E-E-A-T, conversion optimization, internal linking, or wants to
  improve organic search performance. Triggers on questions like "audit my site",
  "why is my traffic down", "optimize for Google", "improve page speed", "SEO checklist",
  "does this page rank", even if the user doesn't explicitly say "SEO audit."
---

# SEO Growth Engine

Run a structured SEO audit in phases. Every phase produces findings — collect them
as you go. At the end, assemble everything into the Audit Report template.

**Before starting phase 1**, ask the user for:
- The site URL (or codebase path if analyzing source)
- What they care about most: technical health, content, conversions, or programmatic scale
- Whether they have GSC access (if yes, ask for key metrics: clicks, impressions, avg position, crawl stats)

Then run through the phases below. Skip phases the user said they don't care about.

### Multi-site audits: sequential only

When the user asks you to audit multiple sites, run them **one at a time, sequentially**. Never audit sites in parallel — Playwright shares a single browser context, and cookies, localStorage, or service worker state from one site can contaminate navigation to another site, producing false redirects and phantom cross-site behavior.

**Before each new site:**
1. Call `browser_close` to kill the current browser context
2. Wait 2 seconds for state to flush
3. Then start the next site fresh with `browser_navigate`

This ensures each audit is fully isolated and no cross-contamination occurs.

---

## Audit Report Template

Produce the final report in this structure:

```
# SEO Audit: [site]

## Executive Summary
2-3 paragraphs: overall health, top 3 issues, top 3 quick wins.

## Critical Issues (must fix now)
Each: severity (🔴), what's broken, how to fix, expected impact.

## Warnings (degrading performance)
Each: severity (🟡), what's happening, how to fix.

## Opportunities (untapped potential)
Each: severity (🟢), what's missing, expected gain if implemented.

## Phase-by-Phase Findings
Organize all findings under their phase headings.

## Priority Action Plan
Top 10 actions ranked by (impact × ease), with effort estimate (S/M/L).
```

---

## Phase 1: Technical Health

### 1.1 Crawlability & Indexation

Check these items. For each, log a finding with severity if it fails:

```
□ robots.txt — fetch and verify: allows critical paths, blocks /api/, /admin/, staging
□ XML sitemaps — locate and check: index→sub-sitemaps, <50K URLs, <50MB, includes lastmod
□ Sitemaps submitted to GSC (ask user, or check GSC if access)
□ Orphan pages — crawl the site (or ask for Screaming Frog export) and flag pages with no internal links
□ Crawl budget — if GSC access, check Settings→Crawl Stats; flag if host status shows overload
□ Soft 404s — pages returning 200 with thin/error content
□ Canonical tags — every page has self-referencing canonical, no conflicts
□ Duplicate content — check parameterized URLs, www vs non-www, trailing slash variants
□ Pagination — rel=next/prev or server-rendered first page with load-more
```

**How to check:** Use Playwright to fetch pages, inspect `<link rel="canonical">`, `<meta robots>`,
response headers. Use browser_network_requests to spot redirect chains. If the user has a local
codebase, use Serena search_for_pattern to find sitemap/robots files.

Source: Google Search Central — Crawling & Indexing docs. Full list in `references/sources.md`.

### 1.2 Page Speed & Core Web Vitals

Field data (real users) matters more than lab data. If the site is live, run PageSpeed Insights
and check CrUX data. If analyzing source code:

**LCP — target ≤ 2.5s:**
- Check if hero image uses `fetchPriority="high"` or `<link rel="preload">`
- Check image format: WebP/AVIF via `<picture>` or next/image?
- Check for render-blocking CSS/JS in `<head>`
- TTFB target: <600ms (edge caching, CDN, ISR)

**CLS — target ≤ 0.1:**
- All `<img>` / `<video>` have explicit width/height or `aspect-ratio`?
- Dynamic content (ads, embeds) use reserved dimensions?
- Font loading uses `font-display: swap`?

**INP — target ≤ 200ms:**
- Long tasks (>50ms) on main thread?
- Debounced scroll/input handlers?
- DOM size under 1,500 elements?
- React: `useTransition()` for non-urgent updates?

Reference thresholds: `references/benchmarks.md`.

Source: web.dev, Chrome DevTools.

### 1.3 Structured Data

For each page type on the site, verify the right schemas are present.
Map page types to required schemas (see `references/benchmarks.md` — Structured Data table).

Check with Playwright: `document.querySelectorAll('script[type="application/ld+json"]')`.
Validate snippets with Google Rich Results Test URL.

### 1.4 Meta Tags

For each key page type, audit:
- **Title tags**: 50-60 chars, primary keyword near front, unique per page, brand included
- **Meta description**: 150-160 chars, includes keyword, has CTA, unique per page
- Flag duplicates, truncation risks, missing tags

Google rewrites ~61% of poor title tags — the more generic, the more likely it gets rewritten.

### 1.5 URL Structure

```
✅ /blog/best-running-shoes-2025  (short, descriptive, hyphens)
✅ /products/wool-trail-jacket    (slug matches query)
❌ /page?id=12345                 (no meaning)
❌ /category/sub-cat/sub-sub/page (too deep)
```

Rules: hyphens not underscores, lowercase, max 3 levels, keyword in URL, never change without 301.

---

## Phase 2: Content & On-Page

### 2.1 E-E-A-T Assessment

For each page, evaluate against Google's E-E-A-T:
- **Experience**: First-hand experience visible? Author bylines? Real photos?
- **Expertise**: Depth of knowledge demonstrated? Sources cited?
- **Authoritativeness**: Backlinks, mentions, reviews in the space?
- **Trustworthiness**: HTTPS, affiliate disclosure, privacy policy, contact page?

**Affiliate-specific** (Google Affiliate Guidelines):
- Original value beyond merchant descriptions? Proprietary data, comparisons, user ratings?
- Genuine editorial opinion?
- Clear affiliate disclosure on every page with affiliate links?
- At least 500+ words of unique content per programmatic page?

### 2.2 Heading Hierarchy

Crawl key pages and verify:
- Single `<h1>` per page, contains primary keyword
- `<h2>` for sections (secondary keywords), `<h3>` for subsections
- No skipped levels (h1→h3 without h2)

### 2.3 Internal Linking

The #1 most underrated SEO lever. Audit:
- Every page has 3-10 internal links to related pages
- Descriptive anchor text (not "click here", "read more")
- Topic clusters exist: pillar page ↔ supporting pages
- Crawlable `<a href>` links (not JS-only navigation)

**Link patterns to verify:**
- Product/listings: → Related items, same brand, same category, blog posts
- Blog: → Related posts, relevant product/listing pages, category pages
- Footer: Top categories, top blog posts, brand/merchant guides

### 2.4 Image SEO

```
□ Descriptive alt text on every image
□ Descriptive filenames (trail-jacket-navy.webp, not IMG_1234.jpg)
□ WebP/AVIF format (30-50% smaller than JPEG)
□ Responsive: srcset/sizes or next/image
□ Lazy load below-fold images
□ fetchPriority="high" on LCP image only (max 1-2 images)
□ Images in sitemap for Google Images traffic
```

---

## Phase 3: International SEO

Only run this phase if the site serves multiple locales/languages.

### 3.1 Hreflang

For every page in a multi-locale cluster, verify:

```html
<link rel="alternate" hreflang="en" href="https://example.com/page" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

Critical rules:
1. **Return links are MANDATORY** — if EN→FR, FR must also→EN. Missing return links = Google ignores the hreflang. This is the #1 error.
2. x-default = fallback for unmatched locales
3. Self-referencing hreflang required (EN page lists itself)
4. Canonical + hreflang must NOT conflict (e.g., canonical pointing to /en/ but hreflang on /fr/)

For >100 pages, use XML sitemap method, not inline tags.

### 3.2 Localization vs Translation

Translation is NOT localization. Check:
- Examples, currency, cultural references adapted per locale
- Keywords researched per locale (direct translation ≠ what locals search)
- Localized structured data (prices in local currency, availability)
- Internal linking adapted per locale

Good localization delivers 30-50% more organic traffic vs translation alone (SEMrush).

---

## Phase 4: Programmatic SEO at Scale

Only run if the site generates pages at scale (templates, listings, directories).

### 4.1 Thin Content Risk

Google's March 2024 "scaled content abuse" policy targets:
- Mass-generated pages with minimal unique value
- Template pages with only variable swaps (name, city)
- Auto-translated content without editorial review

**Safety checklist:**
```
□ 500+ words unique content per page
□ Dynamic editorial content — varied sentence structures, not just variables
□ Progressive indexation — start with top 10K pages, expand gradually
□ Noindex low-value pages — empty listings, stub detail pages
```

### 4.2 Crawl Budget

For 100K+ pages:
- Crawl budget = crawl rate limit × crawl demand (Google)
- Server speed matters MORE than page count — fast TTFB = more crawled pages
- Remove/noindex dead pages
- Clean sitemap: only indexable pages
- ISR + edge caching → ~50ms TTFB
- Monitor: GSC → Settings → Crawl Stats

### 4.3 Pagination

```
✅ Server-rendered paginated URLs (/page/2, /page/3) — crawlable
✅ First page SSR + "Load More" button — best UX+crawl hybrid
❌ Pure infinite scroll — Googlebot only sees first page
❌ JS-only pagination — invisible to crawlers
```

---

## Phase 5: Affiliate & Monetization

### 5.1 Affiliate Links

Verify every affiliate/paid link:
```html
<!-- Correct -->
<a href="/go/merchant-deal" rel="sponsored nofollow" target="_blank">View offer →</a>

<!-- /go/ paths: 302 redirect, blocked in robots.txt -->
```

Rules (Google Link Spam policy):
- `rel="sponsored"` on ALL paid/affiliate links
- `rel="nofollow"` as belt-and-suspenders
- Never put affiliate URLs in schema markup (Product/Offer.url = canonical merchant page)
- Affiliate disclosure page linked from footer

### 5.2 Value-Add Assessment

Google explicitly penalizes thin affiliate pages. The site must add:
1. Proprietary data: pricing history, availability, specs from multiple sources
2. Comparisons: side-by-side product/service tables
3. Editorial content: genuine reviews, pros/cons
4. User-generated signals: ratings, favorites
5. Unique features: search, filtering not on the merchant site

### 5.3 SafeSearch & Restricted Content

If the site mixes general-audience pages with restricted-audience sections:
- Use only Google-documented markup for restricted content (see Google SafeSearch docs)
- Keep broad-reach editorial pages consistent with normal discovery
- Split intent clearly: restricted catalog vs informational content

---

## Phase 6: Conversion Optimization

### 6.1 CTA Audit

For each key page, check there are 3 CTA positions:
1. Above the fold (hero section)
2. Mid-content (after key info)
3. Bottom (final push after reading)

**CTA copy quality:**
- Action verb + benefit: "Start free trial", "See plans"
- Urgency when real: limited-time phrasing, low-stock signals
- Avoid generic: "Submit", "Click here"

### 6.2 Mobile-First Check

70%+ of traffic is mobile. Verify:
```
□ Touch targets ≥ 48×48px
□ Font size ≥ 16px (prevents iOS zoom on input)
□ No horizontal scroll at 375px width
□ Above-fold content loads fast
□ Thumb-friendly CTA placement (bottom center)
□ No intrusive interstitials (Google penalizes)
```

Use Playwright with `--viewport 375x812` to audit mobile rendering.

### 6.3 Trust Signals

```
□ HTTPS everywhere (ranking factor since 2014)
□ Affiliate disclosure clearly visible
□ Privacy policy + Terms of Service linked from footer
□ Real editorial content (not just API data dumps)
□ Professional design (no broken layouts, readable fonts)
```

---

## Phase 7: Quick Wins & Monitoring

### 7.1 GSC Quick Win Formula

If GSC data is available, calculate for top queries:

```
Quick Win Score = Impressions × (1 - CTR) × (1 / Position)
```

High score = high impressions, low CTR, decent position = most room for improvement.
Flag the top 10 queries by this score — these are the fastest wins.

### 7.2 Monitoring Cadence

Tell the user what to track post-audit:

| Check | Frequency | What to watch |
|-------|-----------|---------------|
| Clicks & Impressions | Daily | Sudden drops (penalty/deindex) |
| CTR by query | Weekly | High-impression low-CTR → improve titles |
| Position changes | Weekly | Quick wins: pos 5-20 with volume |
| Index coverage | Monthly | Crawl errors, excluded pages |
| Core Web Vitals | Monthly | Field data regressions |
| Sitemaps | Monthly | Error/warning counts |

### 7.3 Testing Methodology

Remind the user:
- Change ONE variable at a time
- Wait 2-4 weeks for Google to re-evaluate
- Compare 30-day periods (before vs after)
- Track at page and query level, not just site-wide

---

## Pitfalls Reference

When you spot these, flag them with the right severity:

### 🔴 Critical (can tank the site)
1. Cloaking: different content for Googlebot vs users
2. Keyword stuffing: unnatural density
3. Link schemes: paid links, PBNs, excessive exchanges
4. Duplicate content across locales without translation
5. URL changes without 301 redirects
6. Blocking CSS/JS in robots.txt (Google can't render)
7. Ignoring mobile (mobile-first indexing is live)

### 🟡 Subtle (slow silent damage)
8. Over-optimized anchor text (exact-match everywhere)
9. Thin content at scale (<200 words unique per page)
10. Orphan pages (no internal links)
11. Soft 404s (200 OK on empty pages)
12. Mixed signals: noindex + in sitemap, canonical→noindex
13. Wrong search intent: commercial page for informational query
14. No internal linking strategy

### 🟢 Missed Opportunities
15. No FAQ schema (free SERP real estate)
16. Generic meta descriptions (Google rewrites them)
17. No image optimization (WebP, alt text, lazy loading)
18. Ignoring long-tail (70% of searches are 4+ words)
19. Not using GSC data (free goldmine)
20. No IndexNow (free instant notification to Bing/Yandex)

---

## References

- `references/benchmarks.md` — CWV thresholds, content/conversion benchmarks, schema tables, locale strategy
- `references/sources.md` — Full 64-source bibliography (Google official, industry research, conversion studies, technical deep dives)
