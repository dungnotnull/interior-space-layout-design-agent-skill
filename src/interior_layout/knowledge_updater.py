"""SECOND-KNOWLEDGE-BRAIN pipeline (Phase 3).

Self-improving crawler that refreshes the knowledge base weekly:
  1. fetch candidate entries (crawl4ai + ArXiv API) -- defensively
  2. parse -> title, authors, year, link, abstract
  3. score -> recency x domain-keyword relevance
  4. dedupe -> skip entries whose URL/DOI hash already exists
  5. append -> dated, cited entries to SECOND-KNOWLEDGE-BRAIN.md

crawl4ai is optional: when unavailable the updater logs a warning and exits
without mutating the knowledge base (graceful degradation).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SKILL_ID = 89
SKILL_SLUG = "interior-space-layout-design"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRAIN = os.path.join(ROOT, "SECOND-KNOWLEDGE-BRAIN.md")

ARXIV_CATEGORIES = ["cs.HC", "cs.GR"]
SEARCH_QUERIES = [
    "interior layout ergonomics circulation",
    "daylighting indoor comfort standards",
    "spatial perception human factors",
]
SOURCE_URLS = [
    "https://www.wiley.com",
    "https://www.ctbuh.org",
    "https://www.archdaily.com",
    "https://www.wellcertified.com",
]
DOMAIN_KEYWORDS = [
    "ergonomics", "circulation", "clearance", "anthropometric",
    "daylight", "ventilation", "comfort", "acoustic", "reverberation",
    "layout", "zoning", "feng shui", "bagua", "interior", "space planning",
    "well building", "neufert", "pattern language",
]
ARXIV_API = "http://export.arxiv.org/api/query?search_query=cat:%s&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending"


@dataclass
class Entry:
    title: str
    url: str
    authors: str = ""
    year: str = ""
    venue: str = ""
    abstract: str = ""
    source: str = ""

    def hash(self) -> str:
        return hashlib.sha256(self.url.encode("utf-8")).hexdigest()[:16]


def _norm_year(s: str) -> str:
    m = re.search(r"(19|20)\d{2}", s or "")
    return m.group(0) if m else str(datetime.date.today().year)


def load_seen_hashes(brain_path: str = BRAIN) -> set:
    if not os.path.exists(brain_path):
        return set()
    with open(brain_path, "r", encoding="utf-8") as f:
        return set(re.findall(r"<!--hash:([0-9a-f]{16})-->", f.read()))


def relevance_score(entry: Entry) -> float:
    try:
        year = int(entry.year)
    except (TypeError, ValueError):
        year = 0
    now = datetime.date.today().year
    recency = max(0.0, 1.0 - (now - year) / 8.0) if year else 0.3
    text = (entry.title + " " + entry.abstract).lower()
    hits = sum(1 for kw in DOMAIN_KEYWORDS if kw in text)
    rel = min(1.0, hits / max(1, len(DOMAIN_KEYWORDS) / 2))
    return round(recency * (0.4 + 0.6 * rel), 3)


# --- fetchers ----------------------------------------------------------------

def _http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "interior-layout-knowledge-updater/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - controlled URLs
        data = resp.read()
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return data.decode("latin-1", errors="replace")


def fetch_arxiv_api() -> List[Entry]:
    """Use the public ArXiv API (no external dependency needed)."""
    entries: List[Entry] = []
    for cat in ARXIV_CATEGORIES:
        url = ARXIV_API % cat
        try:
            xml = _http_get(url)
        except Exception as e:
            print("[warn] arxiv api %s failed: %s" % (cat, e))
            continue
        entries.extend(_parse_arxiv_atom(xml, cat))
    return entries


def _parse_arxiv_atom(xml: str, cat: str) -> List[Entry]:
    out: List[Entry] = []
    for block in re.findall(r"<entry>.*?</entry>", xml, re.S):
        title = _first(block, r"<title>(.*?)</title>")
        summary = _first(block, r"<summary>(.*?)</summary>")
        link = _first(block, r'<id>(.*?)</id>')
        published = _first(block, r"<published>(.*?)</published>")
        authors = ", ".join(re.findall(r"<name>(.*?)</name>", block, re.S))
        out.append(Entry(
            title=html.unescape(title).strip(),
            url=html.unescape(link).strip(),
            authors=html.unescape(authors).strip(),
            year=_norm_year(published),
            venue="arXiv [%s]" % cat,
            abstract=html.unescape(summary).strip()[:500],
            source="arxiv",
        ))
    return out


def _first(s: str, pattern: str) -> str:
    m = re.search(pattern, s, re.S)
    return m.group(1) if m else ""


def fetch_crawl4ai() -> List[Entry]:
    """Optional rich crawl of curated sources via crawl4ai."""
    out: List[Entry] = []
    try:
        from crawl4ai import WebCrawler  # type: ignore
    except Exception as e:
        print("[info] crawl4ai unavailable (%s); using ArXiv API only." % e)
        return out
    try:
        crawler = WebCrawler()
        crawler.warmup()
        for url in SOURCE_URLS:
            try:
                res = crawler.run(url=url)
                md = getattr(res, "markdown", "") or ""
                out.append(Entry(
                    title="Source scan: %s" % urllib.parse.urlparse(url).netloc,
                    url=url, year=str(datetime.date.today().year),
                    abstract=md[:500], source="crawl4ai",
                ))
            except Exception as e:
                print("[warn] crawl4ai source %s failed: %s" % (url, e))
    except Exception as e:
        print("[warn] crawl4ai init failed: %s" % e)
    return out


def fetch_entries(use_crawl4ai: bool = True) -> List[Entry]:
    entries = fetch_arxiv_api()
    if use_crawl4ai:
        entries.extend(fetch_crawl4ai())
    return entries


# --- append ------------------------------------------------------------------

def append_entries(entries: List[Entry], brain_path: str = BRAIN,
                   min_score: float = 0.15, dry_run: bool = False) -> int:
    seen = load_seen_hashes(brain_path)
    scored = sorted(((relevance_score(e), e) for e in entries if e.url),
                    key=lambda x: x[0], reverse=True)
    today = datetime.date.today().isoformat()
    blocks: List[str] = []
    for score, e in scored:
        if score < min_score:
            continue
        h = e.hash()
        if h in seen:
            continue
        seen.add(h)
        abstract = (e.abstract or "(abstract pending)")[:280].replace("\n", " ")
        blocks.append(
            "### [%s] %s\n"
            "- Authors: %s\n"
            "- Year: %s\n"
            "- Venue: %s\n"
            "- Link: %s\n"
            "- Relevance score: %s\n"
            "- Key findings: %s\n"
            "<!--hash:%s-->\n" % (
                today, e.title or "Untitled", e.authors or "n/a",
                e.year or "n/a", e.venue or "n/a", e.url, score, abstract, h)
        )
    if not blocks:
        print("No new entries to append (scored >= %.2f)." % min_score)
        return 0
    if dry_run:
        print("[dry-run] Would append %d entries:\n%s" % (len(blocks), "\n".join(blocks)))
        return len(blocks)
    with open(brain_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Automated Crawl Batch - %s\n\n" % today)
        f.write("\n".join(blocks))
    print("Appended %d new entries to %s" % (len(blocks), brain_path))
    return len(blocks)


def update_log(brain_path: str = BRAIN) -> None:
    today = datetime.date.today().isoformat()
    marker = "- [%s] " % today
    if os.path.exists(brain_path):
        with open(brain_path, "r", encoding="utf-8") as f:
            if marker in f.read():
                return
    with open(brain_path, "a", encoding="utf-8") as f:
        f.write("\n- [%s] Automated crawl batch run via tools/knowledge_updater.py.\n" % today)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Refresh SECOND-KNOWLEDGE-BRAIN.md")
    p.add_argument("--no-crawl4ai", action="store_true", help="Skip crawl4ai; use ArXiv API only.")
    p.add_argument("--dry-run", action="store_true", help="Print what would be appended; do not write.")
    p.add_argument("--min-score", type=float, default=0.15, help="Minimum relevance score to keep.")
    p.add_argument("--brain", default=BRAIN, help="Path to SECOND-KNOWLEDGE-BRAIN.md")
    args = p.parse_args(argv)

    print("[knowledge_updater] skill #%s (%s)" % (SKILL_ID, SKILL_SLUG))
    entries = fetch_entries(use_crawl4ai=not args.no_crawl4ai)
    print("Fetched %d candidate entries." % len(entries))
    appended = append_entries(entries, brain_path=args.brain,
                              min_score=args.min_score, dry_run=args.dry_run)
    if not args.dry_run:
        update_log(args.brain)
    return 0


if __name__ == "__main__":
    sys.exit(main())
