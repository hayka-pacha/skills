# Using the audit script

The `scripts/audit.py` script is a deterministic fact-gatherer. It pulls structured data from a single URL so you can reason from facts instead of asking the user to read HTML to you.

## When to use

- The user gave you a URL and wants an SEO opinion → run it first.
- Diagnosing a specific page's ranking/CTR problem → run it.
- Verifying a fix (hreflang, canonical, schema) was deployed correctly → run it before and after.

## When NOT to use

- The user's question is conceptual ("how does hreflang work?") — no URL needed.
- The user asked about *another* site that requires scraping/crawling — use `firecrawl` skill instead.
- The user wants a *multi-page* audit — this is single-page only. For crawls, point them at Screaming Frog.

## How to invoke

```bash
python3 ~/.claude/skills/seo-growth-engine/scripts/audit.py https://example.com/page --pretty
```

No dependencies. Single GET + HEAD. ~1s typical.

## What it returns

A JSON object with three top-level groups:

1. **`robots_txt`** — present, sitemap declarations, whether the audited path is blocked
2. **`sitemaps`** — reachability of each declared sitemap
3. **`page`** — the main payload: title/meta/canonical/hreflang/JSON-LD/headings/images/word-count + response timing
4. **`flags`** — pre-computed diagnostic flags (the "what's wrong" summary)

## How to use the output

Read the `flags` array first — it's the diagnostic summary. Common flags:

| Flag | Means | Likely fix |
|------|-------|-----------|
| `missing-canonical` | No `<link rel=canonical>` | Add self-referencing canonical |
| `missing-title` / `missing-meta-description` | Tag absent | Add it |
| `h1-count=N-should-be-1` | Multiple or zero H1s | Restructure headings |
| `hreflang-missing-self-reference` | Page doesn't list itself in hreflang | See `phase-3-international.md` |
| `hreflang-missing-x-default` | No `x-default` entry | Add one pointing to primary version |
| `thin-content-N-words` | < 300 words in body | See `phase-2-content.md` E-E-A-T |
| `no-json-ld` | No structured data | See `phase-1-technical.md` §1.3 |
| `slow-response-Nms` | TTFB > 1.5s | Cache, CDN, edge — see `phase-1-technical.md` §1.2 |
| `robots-txt-blocks-this-path` | robots.txt disallows this URL | Fix robots.txt or the URL |
| `images-missing-alt=X/Y` | More than 30% of images lack alt | Add alt attributes |
| `sitemap-hreflang-duplicate-code:CODE->N-hrefs` | Same hreflang code declared on multiple URLs in the sitemap — Google silently drops duplicates | Pick one canonical href per hreflang code in the sitemap |
| `sitemap-hreflang-code-mismatch:page=[...]-vs-sitemap=[...]` | Page `<head>` uses one scheme (e.g. `en`/`fr`/`es`) but sitemap uses a different one (e.g. `en-US`/`fr-FR`/`es-ES`) — Google requires consistency | Unify on one scheme. Language-only (`en`/`fr`/`es`) unless you actually target regions |
| `sitemap-hreflang-cluster-mismatch:page-langs=[...]-vs-sitemap-langs=[...]` | Page and sitemap list a different *set* of languages — one is missing entries | Reconcile so both list the same languages |

The script also returns a `sitemap_hreflang` block in the JSON when it finds hreflang declarations for the target URL in the sitemap — useful for showing the user exactly which codes were declared where.

If `flags` is empty, the page passes the lightweight checks — focus diagnosis on field data (CWV via PageSpeed Insights), backlinks, content depth, search-intent match — things the script can't see.

## What the script can't see

- **Field-data CWV** (real-user LCP/INP/CLS) — only PageSpeed Insights / CrUX can.
- **JavaScript-rendered content** — the script gets the initial HTML only. If a Next.js page is client-side rendered, the audit will look thin even if the user sees rich content. Flag this and confirm SSR with the user.
- **Indexation status** — only GSC knows.
- **Backlinks / authority** — Ahrefs/Semrush territory.
- **Internal link graph** — single-page only.
- **Whether competitors are doing better** — manual SERP check.

State these limitations to the user — don't pretend the audit is the whole story.

## Example workflow

1. User says: "my product page at example.com/products/foo isn't ranking, can you take a look?"
2. Run: `python3 ~/.claude/skills/seo-growth-engine/scripts/audit.py https://example.com/products/foo --pretty`
3. Read `flags`. Inspect `title`, `meta_description`, `structured_data.types`, `body_word_count`.
4. Lead the response with the 1-2 issues from `flags` that matter most. Use the references for the *why* and the fix.
5. Note what the audit can't see, ask for GSC data if needed.
