"""Validate RSS news feeds for Phase 2.

Tests BBC News Middle East and Al Jazeera English RSS feeds and checks
that they return recent articles relevant to the Iran-Israel-US conflict.
Uses only stdlib (no feedparser dependency) to parse RSS 2.0 / Atom XML.

Outputs:
  data/raw/rss_validation_sample.json   – up to 50 articles per feed
  reports/tables/rss_validation_summary.md
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
TABLES_DIR = ROOT / "reports" / "tables"

# ── Feed catalogue ────────────────────────────────────────────────────────────
FEEDS: dict[str, dict] = {
    "bbc_middle_east": {
        "label": "BBC News – Middle East",
        "url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
    },
    "aljazeera_english": {
        "label": "Al Jazeera English – All",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
    },
}

# Conflict keywords for relevance scoring
CONFLICT_KEYWORDS = {
    "iran", "israel", "israel", "hamas", "hezbollah", "gaza", "west bank",
    "idf", "irgc", "netanyahu", "khamenei", "tehran", "tel aviv",
    "missile", "drone", "strike", "ceasefire", "war", "conflict",
    "escalation", "nuclear", "sanction", "strait", "hormuz",
    "beirut", "lebanon", "syria", "iraq", "houthi", "yemen",
    "rafah", "jenin", "ramallah",
}

HEADERS = {
    "User-Agent": "Proyecto-Final-ML1-OSINT/0.1 (educational source validation)"
}

MAX_ARTICLES = 50  # per feed


# ─────────────────────────────────────────────────────────────────────────────
# Fetch
# ─────────────────────────────────────────────────────────────────────────────

def fetch_feed(url: str, timeout: int = 30, retries: int = 3) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                print(f"  [retry {attempt}] {exc}", flush=True)
                time.sleep(5 * attempt)
    assert last_error is not None
    raise last_error


# ─────────────────────────────────────────────────────────────────────────────
# Parsing  – supports RSS 2.0 and basic Atom
# ─────────────────────────────────────────────────────────────────────────────

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return (el.text or "").strip()

def _normalise_date(raw: str) -> str:
    """Try to parse RFC 2822 (RSS) or ISO-8601 (Atom) dates to ISO."""
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).isoformat()
    except Exception:
        pass
    try:
        return datetime.fromisoformat(raw.rstrip("Z")).isoformat()
    except Exception:
        return raw


def parse_rss(xml_bytes: bytes) -> list[dict]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"XML parse error: {exc}") from exc

    articles: list[dict] = []

    # RSS 2.0
    for item in root.findall(".//item")[:MAX_ARTICLES]:
        pub_raw = _text(item.find("pubDate")) or _text(item.find("dc:date", _NS))
        articles.append({
            "title": _text(item.find("title")),
            "link": _text(item.find("link")),
            "description": _text(item.find("description")),
            "published": _normalise_date(pub_raw),
            "source": _text(item.find("source")),
        })

    if articles:
        return articles

    # Atom fallback
    atom_ns = "http://www.w3.org/2005/Atom"
    for entry in root.findall(f"{{{atom_ns}}}entry")[:MAX_ARTICLES]:
        pub_raw = _text(entry.find(f"{{{atom_ns}}}published")) or \
                  _text(entry.find(f"{{{atom_ns}}}updated"))
        link_el = entry.find(f"{{{atom_ns}}}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary_el = entry.find(f"{{{atom_ns}}}summary") or entry.find(f"{{{atom_ns}}}content")
        articles.append({
            "title": _text(entry.find(f"{{{atom_ns}}}title")),
            "link": link,
            "description": _text(summary_el),
            "published": _normalise_date(pub_raw),
            "source": "",
        })

    return articles


# ─────────────────────────────────────────────────────────────────────────────
# Relevance scoring
# ─────────────────────────────────────────────────────────────────────────────

def score_article(art: dict) -> bool:
    """Return True if the article matches at least one conflict keyword."""
    text = " ".join([art.get("title", ""), art.get("description", "")]).lower()
    return any(kw in text for kw in CONFLICT_KEYWORDS)


def analyse_feed(articles: list[dict]) -> dict:
    total = len(articles)
    relevant = [a for a in articles if score_article(a)]

    # Date quality
    with_date = [a for a in articles if a.get("published")]
    dates = sorted(a["published"] for a in with_date)
    min_date = dates[0] if dates else "N/A"
    max_date = dates[-1] if dates else "N/A"

    # Missing fields
    missing_title = sum(1 for a in articles if not a.get("title"))
    missing_link = sum(1 for a in articles if not a.get("link"))
    missing_desc = sum(1 for a in articles if not a.get("description"))

    return {
        "total_articles": total,
        "with_date": len(with_date),
        "date_range": f"{min_date} → {max_date}",
        "conflict_relevant": len(relevant),
        "conflict_relevance_pct": round(100 * len(relevant) / total, 1) if total else 0,
        "missing_title": missing_title,
        "missing_link": missing_link,
        "missing_description": missing_desc,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Per-feed validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_feed(key: str, spec: dict) -> dict:
    label = spec["label"]
    url = spec["url"]
    print(f"\n{'─'*60}", flush=True)
    print(f"  Feed: {label}", flush=True)
    print(f"  URL:  {url}", flush=True)

    result: dict = {
        "label": label,
        "url": url,
        "error": None,
        "articles": [],
        "analytics": {},
    }

    try:
        raw = fetch_feed(url)
        print(f"  Fetched {len(raw):,} bytes", flush=True)
        articles = parse_rss(raw)
        print(f"  Parsed {len(articles)} articles", flush=True)
        result["articles"] = articles
        result["analytics"] = analyse_feed(articles)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        print(f"  ERROR: {result['error']}", flush=True)
    except Exception as exc:
        result["error"] = f"Unexpected: {type(exc).__name__}: {exc}"
        print(f"  ERROR: {result['error']}", flush=True)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Markdown report
# ─────────────────────────────────────────────────────────────────────────────

def write_summary(results: dict[str, dict]) -> Path:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# RSS Feeds Validation Summary",
        "",
        f"Generated at: {now}",
        "",
        f"Conflict keywords used for relevance: {len(CONFLICT_KEYWORDS)}",
        "",
        "---",
        "",
    ]

    for key, res in results.items():
        lines.append(f"## {res['label']}")
        lines.append("")
        lines.append(f"- URL: {res['url']}")
        lines.append(f"- Error: {res['error'] or 'None'}")
        ana = res.get("analytics", {})
        if ana:
            lines.append(f"- Articles retrieved: {ana.get('total_articles', 0)}")
            lines.append(f"- Articles with date: {ana.get('with_date', 0)}")
            lines.append(f"- Date range: {ana.get('date_range', 'N/A')}")
            lines.append(f"- Conflict-relevant articles: {ana.get('conflict_relevant', 0)} "
                         f"({ana.get('conflict_relevance_pct', 0)}%)")
            lines.append(f"- Missing title: {ana.get('missing_title', 0)}")
            lines.append(f"- Missing link: {ana.get('missing_link', 0)}")
            lines.append(f"- Missing description: {ana.get('missing_description', 0)}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines += [
        "## Decision",
        "",
        "RSS feeds provide real-time textual context for the conflict.",
        "They will be used as a complementary noticiero (news) feature layer,",
        "NOT as the primary event-count source.",
        "Ingestion will use scheduled pulls (e.g., every 6 h) with deduplication",
        "by `link` to build a running archive.",
        "",
    ]

    output = TABLES_DIR / "rss_validation_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  RSS Feed Source Validation")
    print(f"  {datetime.now(UTC).isoformat(timespec='seconds')}")
    print("=" * 60)

    results: dict[str, dict] = {}
    all_articles: list[dict] = []

    for key, spec in FEEDS.items():
        res = validate_feed(key, spec)
        results[key] = res
        for art in res["articles"]:
            art["_feed_key"] = key
            art["_feed_label"] = spec["label"]
        all_articles.extend(res["articles"])

    # Save combined sample
    sample_path = RAW_DIR / "rss_validation_sample.json"
    sample_path.write_text(
        json.dumps(all_articles[:150], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n  Sample saved → {sample_path.name}", flush=True)

    summary_path = write_summary(results)
    print(f"  Summary written → {summary_path}", flush=True)

    print(f"\n{'='*60}")
    errors = [k for k, r in results.items() if r.get("error")]
    if errors:
        print(f"  ⚠  Feed failures: {', '.join(errors)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
