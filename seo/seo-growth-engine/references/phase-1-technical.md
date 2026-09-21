# Phase 1 — Technical SEO

## 1.1 Crawlability & Indexation

Checklist:
- robots.txt allows critical paths, blocks `/api/`, `/admin/`, etc.
- XML sitemaps: index → sub-sitemaps, < 50K URLs each, < 50MB
- Sitemaps include `lastmod` (and `changefreq`/`priority` when meaningful)
- Sitemaps submitted to Google Search Console
- No orphan pages — every important page reachable via internal links
- Crawl budget visible in GSC → Settings → Crawl Stats
- No soft 404s (200 response with error/empty content)
- Canonical tags on every page (self-referencing by default)
- No duplicate content from URL parameters
- Pagination uses crawlable URLs (`/page/2`), not pure JS infinite scroll

**Why it matters**: If Google can't reach or correctly classify a page, nothing else matters. Source: Google Search Central — Crawling & Indexing docs.

## 1.2 Core Web Vitals

Test field data (real users via CrUX) — not just lab data (Lighthouse). Field data is what Google ranks on.

**LCP — Largest Contentful Paint** (target ≤ 2.5s)

Order of impact:
1. TTFB under 600ms — edge cache, CDN, ISR
2. Preload LCP image: `<link rel="preload" as="image" href="...">`
3. `fetchPriority="high"` on hero/LCP image
4. Serve WebP/AVIF (30-50% smaller than JPEG) via `<picture>` or `next/image`
5. Eliminate render-blocking CSS/JS
6. Limit "priority" images to 4-6 — more dilutes the priority signal

**CLS — Cumulative Layout Shift** (target ≤ 0.1)

1. Explicit `width`/`height` or `aspect-ratio` on every image/video
2. Reserve space for dynamic content with skeleton loaders
3. Never inject content above existing content (banners, cookie notices appearing late)
4. Fonts: `font-display: swap` + preload critical fonts
5. Ads/embeds: reserve fixed dimensions

**INP — Interaction to Next Paint** (target ≤ 200ms)

INP replaced FID in March 2024 — it's stricter.

1. Break long tasks (> 50ms) into chunks; `scheduler.yield()` or `setTimeout(0)`
2. `useTransition()` in React for non-urgent state updates
3. DOM under 1,500 elements (heavier DOM = slower style/layout)
4. Debounce scroll/input handlers (16ms for scroll, 100-300ms for typed input)
5. Defer non-critical third-party scripts

Case study: QuintoAndar reduced INP 80% → +36% conversion. Speed compounds with conversion.

## 1.3 Structured Data

Pick the schema matching the page type. Validate with Google Rich Results Test.

| Page type | Required | Bonus |
|-----------|----------|-------|
| Homepage | WebSite, Organization, SearchAction | SiteNavigationElement |
| Article/Blog | Article, BreadcrumbList | FAQPage, HowTo |
| Product | Product, Offer, AggregateRating | Review |
| Profile | ProfilePage, Person | BreadcrumbList |
| Category | CollectionPage, ItemList | BreadcrumbList |
| FAQ | FAQPage | BreadcrumbList |

Rules:
- In Next.js, use `strategy="beforeInteractive"` so the JSON-LD is in initial HTML
- Don't mark up content not visible to users — Google's spam policy treats this as deceptive
- BreadcrumbList on every inner page; it surfaces in SERPs
- For affiliate sites: never put the affiliate URL in `Product.url` — use the canonical merchant page

## 1.4 Meta Tags

**Title tag** (Source: Backlinko, Moz):
- 50-60 characters (Google truncates around 580px)
- Primary keyword near the front
- Include brand name — builds recognition and direct-search CTR
- Unique per page (never duplicate)
- Use numbers, year, "Best/Free/Guide" for CTR uplift

Google rewrites ~61% of titles it considers low quality — write yours well or Google picks for you.

**Meta description** (Source: Moz):
- 150-160 characters
- Include primary keyword (Google bolds matches)
- Clear value prop + soft CTA
- Unique per page
- If omitted, Google auto-generates from page content — often worse than what you'd write

**Avoid**: keyword stuffing, generic descriptions, marketing-team brand fluff with no keywords.

## 1.5 URL Structure

```
✅ /blog/best-running-shoes-2025      short, descriptive, hyphenated
✅ /products/wool-trail-jacket         slug matches search query
❌ /page?id=12345                     no meaning, no keywords
❌ /category/sub-cat/sub-sub/page     too deep, dilutes authority
```

Rules (Source: Google SEO Starter Guide):
- Hyphens, not underscores
- Lowercase only
- Max 3 directory levels
- Keyword in URL when natural
- **Never change URLs post-indexation without 301 redirects** — instant authority loss

## Sources for this phase

Google Search Central, web.dev Vitals guide, Backlinko ranking study, Chrome DevTools docs, schema.org. Full list in `sources.md`.
