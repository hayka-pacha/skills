# Common Pitfalls — What NOT to Do

Twenty mistakes ranked by severity. Scan this when auditing a site — these account for most underperformance.

## 🔴 Critical (Can Tank a Site)

1. **Cloaking** — showing different content to Googlebot vs users. Manual-action territory.
2. **Keyword stuffing** — unnatural density triggers spam filters.
3. **Link schemes** — buying links, excessive exchanges, PBN footprints. Penguin still bites.
4. **Duplicate content across locales** — each locale must have unique or properly translated content; auto-translated copies count as duplicates.
5. **Changing URLs without 301 redirects** — instant loss of all accumulated authority. If you must change URLs, set up redirects *before* the change.
6. **Blocking CSS/JS in robots.txt** — Google can't render the page properly and may downgrade rankings.
7. **Ignoring mobile** — mobile-first indexing means the mobile version is what Google uses. If desktop has content the mobile version hides, that content effectively doesn't exist for Google.

## 🟡 Subtle (Slow Silent Damage)

8. **Over-optimizing anchor text** — exact-match internal anchors everywhere looks manipulative.
9. **Thin content at scale** — template pages with < 200 unique words. March 2024 update specifically targets this.
10. **Orphan pages** — pages not linked from anywhere. Never discovered, never indexed.
11. **Soft 404s** — empty/error pages returning HTTP 200 instead of 404. Wastes crawl budget, confuses Google.
12. **Mixed signals** — noindex page included in sitemap, canonical pointing to a noindexed page, hreflang to a redirected URL. Pick one signal per page and be consistent.
13. **Ignoring search intent** — ranking informational queries with commercial pages (or vice versa). Match SERP intent or get filtered.
14. **No internal linking strategy** — random links instead of intentional topic clusters. Authority doesn't flow where you need it.

## 🟢 Missed Opportunities (Leaving Traffic on the Table)

15. **Not using FAQ schema** — free SERP real estate, eligible for rich snippets.
16. **Generic meta descriptions** — Google ignores yours and generates its own from page content, often worse than what you'd write.
17. **No image optimization** — missing WebP/AVIF, no alt text, no lazy loading, no image sitemap.
18. **Ignoring long-tail** — 70% of searches are 4+ words. Long-tail = lower volume per term but cumulatively massive and easier to rank.
19. **Not mining GSC data** — the free goldmine of what Google already thinks your site is about. Use it.
20. **No IndexNow** — free, instant notification to Bing/Yandex for new content. Tiny effort, real upside.

## Diagnostic shortcut

When auditing a new site, scan these 20 first. They surface ~80% of underperformance issues in 20% of the time of a full audit.
