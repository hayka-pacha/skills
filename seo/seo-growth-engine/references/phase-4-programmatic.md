# Phase 4 — Programmatic SEO at Scale

## 4.1 Avoiding Thin Content

Google's March 2024 core update introduced explicit "scaled content abuse" policy targeting:
- Mass-generated pages with minimal unique value
- Template pages with only variable swaps (city name, product name, etc.)
- Auto-translated content without editorial review
- AI-generated content with no value-add

**How to stay safe:**

1. **500+ words of unique content per page** as a hard minimum.
2. **Dynamic editorial content** — vary sentence structures, paragraph orders, supporting facts. Not just variable substitution.
3. **Progressive indexation** — launch with your top 10K pages, expand gradually. Don't dump 1M pages on day one; Google's quality filters will trip.
4. **Internal quality signals** — engagement, time on page, return visits, bounce rate. If users hate it, Google notices.
5. **Noindex low-value pages** — stub pages with empty data, near-duplicate listings, expired content. Better to have 50K great pages than 500K mediocre ones.
6. **Add real differentiation per page**: pricing history, availability schedule, comparison vs alternatives, user reviews, regional context. Anything that couldn't be produced by a simple template fill.

**Test of survival**: would a user prefer this page over the merchant's own page or a generic AI answer? If no, deindex.

## 4.2 Crawl Budget Management

For sites with 100K+ pages.

Google's crawl budget = `crawl rate limit × crawl demand`. You influence both:

- **Server speed matters more than page count.** Fast TTFB = more pages crawled per session. ISR + edge caching ≈ 50ms TTFB — massive advantage over slow origin servers.
- **Remove/noindex dead pages** — 404s, empty listings, expired offers eat crawl budget.
- **Clean the sitemap** — only include indexable URLs. Don't list noindexed, redirected, or 404 pages.
- **Monitor in GSC** → Settings → Crawl Stats. Look for response time spikes and crawl-rate drops.
- **Block parameter explosion** in robots.txt or via canonicals (sort, filter, tracking params).
- **Faceted navigation** is a classic crawl-trap — combinatorial URL explosion. Use canonicals to consolidate, or block via robots.txt for non-indexable combinations.

## 4.3 Pagination vs Infinite Scroll

```
✅ Server-rendered paginated URLs (/page/2, /page/3) — fully crawlable
✅ First page server-rendered + "Load More" button for UX — best hybrid
❌ Pure infinite scroll — Googlebot only sees first page
❌ JavaScript-only pagination with no real URLs — invisible to crawlers
```

If you want infinite scroll for UX, give every "page" a real crawlable URL (`?page=2`) and update history state as the user scrolls. Crawlers can hit the URL; users get the smooth experience.

`rel=next`/`rel=prev` is deprecated as a ranking signal but doesn't hurt to include. Real crawlable URLs matter more.

## Sources

Google March 2024 Core Update blog, Google Crawl Budget docs, JavaScript SEO docs. Full list in `sources.md`.
