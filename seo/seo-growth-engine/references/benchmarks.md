# SEO Benchmarks & Thresholds

## Core Web Vitals (Google)

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## Content Benchmarks (Backlinko — 11.8M results study)

| Metric | Benchmark |
|--------|-----------|
| Average #1 result word count | ~1,447 words |
| Title tag CTR sweet spot | 15-40 characters |
| Pages with 0 organic traffic | **96.55%** (Ahrefs) |
| Speed: 100ms improvement | **+8.4% conversion** (Deloitte) |

## Conversion Benchmarks

| Metric | Benchmark |
|--------|-----------|
| Landing page avg conversion | 4.02% (Unbounce) |
| Top 25% pages | >5.31% |
| Cart abandonment rate | 70.19% (Baymard) |
| Mobile CWV pass rate | Only 39% of sites (Web Almanac 2024) |

## Structured Data by Page Type

| Page Type | Required Schema | Bonus Schema |
|-----------|----------------|--------------|
| Homepage | WebSite, Organization, SearchAction | SiteNavigationElement |
| Article/Blog | Article, BreadcrumbList | FAQPage, HowTo |
| Product | Product, Offer, AggregateRating | Review |
| Profile | ProfilePage, Person | BreadcrumbList |
| Category | CollectionPage, ItemList | BreadcrumbList |
| FAQ | FAQPage | BreadcrumbList |

## Schema Rules

- In Next.js App Router: use a native `<script type="application/ld+json">` in layout/page — NOT `next/script` (that's for executable JS, not JSON-LD). See `nextjs.org/docs/app/guides/json-ld`.
- Escape `<` in JSON to prevent XSS: `JSON.stringify(jsonLd).replace(/</g, '<')`
- For TypeScript: use `schema-dts` package for typed JSON-LD (`import type { Product, WithContext } from 'schema-dts'`)
- Validate with Google Rich Results Test
- Don't mark up content not visible to users (spam policy)
- BreadcrumbList on every inner page

## Locale Strategy

| Approach | Pros | Cons |
|----------|------|------|
| **Subdirectories** `/fr/` | Consolidates domain authority | Shared IP signals |
| Subdomains `fr.example.com` | Separate crawl budgets | Splits authority |
| ccTLDs `.fr` | Strongest geo signal | Most expensive, splits authority |

**Recommendation**: Subdirectories for most sites (Google, Ahrefs, Moz).
