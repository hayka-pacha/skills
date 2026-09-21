#!/usr/bin/env python3
"""Single-page SEO audit using only the Python stdlib.

Usage:
    python3 audit.py https://example.com [--user-agent UA]

Outputs JSON with technical SEO facts:
- HTTP status, redirect chain, final URL
- robots.txt: present, allows path, sitemap declarations
- sitemap.xml reachability
- Title: text + length
- Meta description: text + length
- Canonical URL
- Hreflang cluster (self-ref check, sibling count)
- JSON-LD blocks (count + @type per block)
- Headings: H1 count and text, H2/H3 counts
- Images: total, missing-alt count
- Word count (rough, body text only)
- Page weight: HTML byte size, transferred-encoding
- TTFB hint: total request duration in ms (single request, not field data)

This is a fact-gathering tool, not a recommender. Run it, then interpret with
the seo-growth-engine skill loaded.
"""

import argparse
import gzip
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


DEFAULT_UA = "Mozilla/5.0 (compatible; seo-growth-engine-audit/1.0; +https://example.com/bot)"
TIMEOUT_S = 15
MAX_BYTES = 5 * 1024 * 1024  # 5 MB cap


def fetch(url: str, ua: str, method: str = "GET") -> dict:
    """Fetch a URL, return dict with status, headers, body (decoded), redirects, duration_ms."""
    req = urllib.request.Request(url, method=method, headers={"User-Agent": ua, "Accept-Encoding": "gzip, identity"})
    start = time.monotonic()
    redirects: list[str] = []
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            duration_ms = int((time.monotonic() - start) * 1000)
            raw = resp.read(MAX_BYTES)
            if resp.headers.get("Content-Encoding") == "gzip":
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
            # urllib follows redirects by default; get final URL
            final_url = resp.geturl()
            if final_url != url:
                redirects.append(final_url)
            charset = resp.headers.get_content_charset() or "utf-8"
            try:
                body = raw.decode(charset, errors="replace")
            except LookupError:
                body = raw.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "status": resp.status,
                "final_url": final_url,
                "redirects": redirects,
                "headers": dict(resp.headers.items()),
                "body": body,
                "byte_size": len(raw),
                "duration_ms": duration_ms,
            }
    except urllib.error.HTTPError as e:
        return {
            "ok": False,
            "status": e.code,
            "error": f"HTTPError {e.code}: {e.reason}",
            "duration_ms": int((time.monotonic() - start) * 1000),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {
            "ok": False,
            "status": None,
            "error": f"{type(e).__name__}: {e}",
            "duration_ms": int((time.monotonic() - start) * 1000),
        }


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts: list[str] = []
        self._in_title = False
        self._title_captured = False  # only capture the first <title> (avoid SVG <title> noise)
        self.meta_description: str | None = None
        self.meta_robots: str | None = None
        self.canonical: str | None = None
        self.hreflang: list[dict] = []  # [{hreflang, href}]
        self.json_ld_blocks: list[str] = []
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []
        self.h1: list[str] = []
        self.h2_count = 0
        self.h3_count = 0
        self._in_heading: str | None = None
        self._heading_buf: list[str] = []
        self.img_total = 0
        self.img_missing_alt = 0
        self._in_body = False
        self._body_text: list[str] = []
        self._skip_text = False  # for script/style/noscript

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and not self._title_captured:
            self._in_title = True
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            if name == "description":
                self.meta_description = a.get("content")
            elif name == "robots":
                self.meta_robots = a.get("content")
        elif tag == "link":
            rel = (a.get("rel") or "").lower()
            if rel == "canonical":
                self.canonical = a.get("href")
            elif rel == "alternate" and a.get("hreflang"):
                self.hreflang.append({"hreflang": a["hreflang"], "href": a.get("href")})
        elif tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buf = []
            else:
                self._skip_text = True
        elif tag in ("style", "noscript"):
            self._skip_text = True
        elif tag in ("h1", "h2", "h3"):
            self._in_heading = tag
            self._heading_buf = []
        elif tag == "img":
            self.img_total += 1
            alt = a.get("alt")
            if alt is None or alt.strip() == "":
                self.img_missing_alt += 1
        elif tag == "body":
            self._in_body = True

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self._title_captured = True
        elif tag == "script":
            if self._in_jsonld:
                self.json_ld_blocks.append("".join(self._jsonld_buf))
                self._in_jsonld = False
            self._skip_text = False
        elif tag in ("style", "noscript"):
            self._skip_text = False
        elif tag in ("h1", "h2", "h3"):
            text = "".join(self._heading_buf).strip()
            if tag == "h1":
                self.h1.append(text)
            elif tag == "h2":
                self.h2_count += 1
            else:
                self.h3_count += 1
            self._in_heading = None
            self._heading_buf = []
        elif tag == "body":
            self._in_body = False

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._in_heading:
            self._heading_buf.append(data)
        if self._in_body and not self._skip_text:
            self._body_text.append(data)


def parse_robots(body: str, path: str = "/") -> dict:
    """Lightweight robots.txt parse for User-agent: * — disallow rules and sitemap declarations."""
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith("#")]
    sitemaps: list[str] = []
    star_block = False
    disallowed: list[str] = []
    allowed: list[str] = []
    for line in lines:
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "sitemap":
            sitemaps.append(val)
            continue
        if key == "user-agent":
            star_block = (val == "*")
            continue
        if star_block:
            if key == "disallow" and val:
                disallowed.append(val)
            elif key == "allow" and val:
                allowed.append(val)
    # rough: does any disallow match the given path?
    path_blocked = any(path.startswith(d) for d in disallowed if d != "/")
    if "/" in disallowed and not any(path.startswith(a) for a in allowed):
        path_blocked = True
    return {
        "disallow_count": len(disallowed),
        "allow_count": len(allowed),
        "sitemaps": sitemaps,
        "path_blocked": path_blocked,
        "disallow_sample": disallowed[:5],
    }


def extract_json_ld_types(blocks: list[str]) -> list[str]:
    types: list[str] = []
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError:
            types.append("(invalid-json)")
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            t = item.get("@type") if isinstance(item, dict) else None
            if isinstance(t, list):
                types.extend(str(x) for x in t)
            elif t:
                types.append(str(t))
    return types


def estimate_word_count(parser: SEOParser) -> int:
    text = " ".join(parser._body_text)
    text = re.sub(r"\s+", " ", text)
    return len(text.split())


SM_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}


def parse_sitemap_hreflang(sitemap_body: str, target_url: str) -> dict | None:
    """Parse a sitemap XML body, return the hreflang cluster declared for target_url.

    Returns None if the target URL isn't found in the sitemap, or if the sitemap is a sitemap
    index (no <url> entries). Returns dict with:
      - entries: [{hreflang, href}]
      - duplicates: list of (hreflang, [hrefs]) where a code maps to multiple hrefs
    """
    try:
        root = ET.fromstring(sitemap_body)
    except ET.ParseError:
        return None
    # Look for <url> entries (urlset). Sitemap indexes have <sitemap> entries — skip those.
    url_elems = root.findall("sm:url", SM_NS)
    if not url_elems:
        return None
    target_norm = target_url.rstrip("/")
    for u in url_elems:
        loc = u.find("sm:loc", SM_NS)
        if loc is None or loc.text is None:
            continue
        # match either the canonical loc or any of its xhtml:link alternates
        loc_norm = loc.text.strip().rstrip("/")
        alternates = u.findall("xhtml:link", SM_NS)
        alt_hrefs = [a.get("href", "").rstrip("/") for a in alternates]
        if loc_norm == target_norm or target_norm in alt_hrefs:
            entries = [
                {"hreflang": a.get("hreflang"), "href": a.get("href")}
                for a in alternates
                if a.get("rel") == "alternate"
            ]
            # find duplicate hreflang codes mapping to different hrefs
            by_code: dict[str, list[str]] = {}
            for e in entries:
                by_code.setdefault(e["hreflang"] or "", []).append(e["href"] or "")
            duplicates = [
                {"hreflang": code, "hrefs": hrefs}
                for code, hrefs in by_code.items()
                if len(set(hrefs)) > 1
            ]
            return {"entries": entries, "duplicates": duplicates, "matched_loc": loc.text.strip()}
    return None


def expand_sitemap_index(index_body: str) -> list[str]:
    """If body is a sitemap index, return child sitemap URLs. Empty list if not an index."""
    try:
        root = ET.fromstring(index_body)
    except ET.ParseError:
        return []
    children = root.findall("sm:sitemap/sm:loc", SM_NS)
    return [c.text.strip() for c in children if c is not None and c.text]


def compare_hreflang(page_hreflang: list[dict], sitemap_hreflang: dict | None) -> list[str]:
    """Compare page <head> hreflang against sitemap declarations. Return list of mismatch flags."""
    flags: list[str] = []
    if sitemap_hreflang is None:
        return flags
    if sitemap_hreflang.get("duplicates"):
        for dup in sitemap_hreflang["duplicates"]:
            flags.append(f"sitemap-hreflang-duplicate-code:{dup['hreflang']}->{len(dup['hrefs'])}-hrefs")
    # exclude x-default — it's a special value, not a language code, and shouldn't compare against region scheme
    page_codes = {h.get("hreflang") for h in page_hreflang if h.get("hreflang") and h.get("hreflang") != "x-default"}
    sitemap_codes = {e.get("hreflang") for e in sitemap_hreflang["entries"] if e.get("hreflang") and e.get("hreflang") != "x-default"}
    if page_codes and sitemap_codes and page_codes != sitemap_codes:
        # is it just a scheme difference (e.g. 'en' vs 'en-US') or a missing-language difference?
        page_langs = {c.split("-")[0] for c in page_codes}
        sitemap_langs = {c.split("-")[0] for c in sitemap_codes}
        if page_langs == sitemap_langs:
            flags.append(f"sitemap-hreflang-code-mismatch:page={sorted(page_codes)}-vs-sitemap={sorted(sitemap_codes)}")
        else:
            flags.append(f"sitemap-hreflang-cluster-mismatch:page-langs={sorted(page_langs)}-vs-sitemap-langs={sorted(sitemap_langs)}")
    return flags


def audit(url: str, ua: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"
    report: dict = {"url": url, "origin": origin, "path": path, "user_agent": ua}

    # 1. Robots
    robots_res = fetch(f"{origin}/robots.txt", ua)
    if robots_res["ok"] and robots_res["status"] == 200:
        report["robots_txt"] = {"present": True, **parse_robots(robots_res["body"], path)}
    else:
        report["robots_txt"] = {"present": False, "error": robots_res.get("error"), "status": robots_res.get("status")}

    # 2. Sitemap — fetch (not HEAD) so we can parse hreflang for the target URL
    sitemap_urls = report.get("robots_txt", {}).get("sitemaps", []) or [f"{origin}/sitemap.xml"]
    report["sitemaps"] = []
    sitemap_hreflang: dict | None = None
    sitemaps_to_try: list[str] = list(sitemap_urls[:3])
    seen: set[str] = set()
    for sm in sitemaps_to_try:
        if sm in seen or len(report["sitemaps"]) >= 5:
            break
        seen.add(sm)
        sm_res = fetch(sm, ua, method="GET")
        ok = sm_res["ok"] and sm_res.get("status") == 200
        report["sitemaps"].append({
            "url": sm,
            "reachable": ok,
            "status": sm_res.get("status"),
        })
        if not ok:
            continue
        # If this is a sitemap index, queue children
        children = expand_sitemap_index(sm_res["body"])
        if children:
            sitemaps_to_try.extend(children[:5])
            continue
        # Otherwise try to find hreflang for the target URL
        if sitemap_hreflang is None:
            sitemap_hreflang = parse_sitemap_hreflang(sm_res["body"], url)
    if sitemap_hreflang is not None:
        report["sitemap_hreflang"] = sitemap_hreflang

    # 3. Page itself
    page = fetch(url, ua)
    if not page["ok"]:
        report["page"] = {"ok": False, "error": page.get("error"), "status": page.get("status")}
        return report

    parser = SEOParser()
    parser.feed(page["body"])

    title = "".join(parser.title_parts).strip()
    json_ld_types = extract_json_ld_types(parser.json_ld_blocks)
    word_count = estimate_word_count(parser)

    # Hreflang analysis
    hreflang = parser.hreflang
    self_ref = any((h.get("href") or "").rstrip("/") == page["final_url"].rstrip("/") for h in hreflang)
    has_x_default = any(h.get("hreflang") == "x-default" for h in hreflang)

    report["page"] = {
        "ok": True,
        "status": page["status"],
        "final_url": page["final_url"],
        "redirects": page["redirects"],
        "duration_ms": page["duration_ms"],
        "byte_size": page["byte_size"],
        "content_encoding": page["headers"].get("Content-Encoding"),
        "content_type": page["headers"].get("Content-Type"),
        "cache_control": page["headers"].get("Cache-Control"),
        "title": {"text": title, "length": len(title), "in_sweet_spot_50_60": 50 <= len(title) <= 60},
        "meta_description": {
            "text": parser.meta_description,
            "length": len(parser.meta_description) if parser.meta_description else 0,
            "in_sweet_spot_150_160": parser.meta_description is not None and 150 <= len(parser.meta_description) <= 160,
            "present": parser.meta_description is not None,
        },
        "meta_robots": parser.meta_robots,
        "canonical": parser.canonical,
        "canonical_self_ref": parser.canonical and parser.canonical.rstrip("/") == page["final_url"].rstrip("/"),
        "hreflang": {
            "count": len(hreflang),
            "self_referenced": self_ref,
            "has_x_default": has_x_default,
            "entries": hreflang[:20],
        },
        "structured_data": {
            "json_ld_block_count": len(parser.json_ld_blocks),
            "types": json_ld_types,
        },
        "headings": {
            "h1_count": len(parser.h1),
            "h1_text": parser.h1,
            "h2_count": parser.h2_count,
            "h3_count": parser.h3_count,
        },
        "images": {
            "total": parser.img_total,
            "missing_alt": parser.img_missing_alt,
        },
        "body_word_count": word_count,
    }

    # 4. Lightweight diagnostic flags
    flags: list[str] = []
    if not parser.canonical:
        flags.append("missing-canonical")
    if not report["page"]["title"]["text"]:
        flags.append("missing-title")
    if not parser.meta_description:
        flags.append("missing-meta-description")
    if len(parser.h1) != 1:
        flags.append(f"h1-count={len(parser.h1)}-should-be-1")
    if parser.img_total and parser.img_missing_alt / parser.img_total > 0.3:
        flags.append(f"images-missing-alt={parser.img_missing_alt}/{parser.img_total}")
    if hreflang and not self_ref:
        flags.append("hreflang-missing-self-reference")
    if hreflang and not has_x_default:
        flags.append("hreflang-missing-x-default")
    if word_count < 300:
        flags.append(f"thin-content-{word_count}-words")
    if not parser.json_ld_blocks:
        flags.append("no-json-ld")
    if page["duration_ms"] > 1500:
        flags.append(f"slow-response-{page['duration_ms']}ms")
    if report["robots_txt"].get("path_blocked"):
        flags.append("robots-txt-blocks-this-path")
    flags.extend(compare_hreflang(hreflang, sitemap_hreflang))
    report["flags"] = flags

    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Single-page SEO audit (stdlib only)")
    p.add_argument("url", help="URL to audit (include scheme)")
    p.add_argument("--user-agent", default=DEFAULT_UA, help="User-Agent string")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = p.parse_args()

    if not args.url.startswith(("http://", "https://")):
        print(f"error: URL must start with http:// or https:// (got: {args.url})", file=sys.stderr)
        return 2

    result = audit(args.url, args.user_agent)
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
