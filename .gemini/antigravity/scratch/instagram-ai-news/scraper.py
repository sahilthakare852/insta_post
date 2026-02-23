"""
RSS Feed Scraper — Fetches latest AI/DevOps articles from multiple RSS feeds.
Also extracts full article body text for AI summarization.
"""

import feedparser
import requests
import re
import html
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from config import (
    RSS_FEEDS, MAX_ARTICLES_PER_FEED, ARTICLE_AGE_HOURS,
    PROMO_KEYWORDS, BOILERPLATE_PATTERNS,
    MAX_ARTICLE_TEXT_CHARS, ARTICLE_FETCH_TIMEOUT,
)

# Browser-like headers to avoid being blocked by RSS servers
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def clean_html(raw_html: str) -> str:
    """Strip HTML tags and decode entities."""
    clean = re.sub(r"<[^>]+>", "", raw_html)
    return html.unescape(clean).strip()


def strip_boilerplate(text: str) -> str:
    """Remove known boilerplate patterns from RSS descriptions."""
    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, "", text).strip()
    return text


def is_promo_article(title: str, description: str) -> bool:
    """Check if an article is a promo/ad based on keywords."""
    combined = f"{title} {description}".lower()
    return any(kw in combined for kw in PROMO_KEYWORDS)


def fetch_article_text(url: str, verbose: bool = False) -> str:
    """Fetch the full article page and extract main body text."""
    if not url:
        return ""
    try:
        resp = requests.get(
            url, headers=HTTP_HEADERS, timeout=ARTICLE_FETCH_TIMEOUT,
            allow_redirects=True
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Remove noise elements
        for tag in soup.find_all(["script", "style", "nav", "footer",
                                   "header", "aside", "form", "iframe"]):
            tag.decompose()
        
        # Strategy: find main content container
        content = None
        
        # 1. Try <article> tag
        article_tag = soup.find("article")
        if article_tag:
            content = article_tag
        
        # 2. Try common content class names
        if not content:
            for selector in [
                "div.article-content", "div.post-content", "div.entry-content",
                "div.article-body", "div.story-body", "main",
                "div[itemprop='articleBody']",
            ]:
                found = soup.select_one(selector)
                if found:
                    content = found
                    break
        
        # 3. Fallback: body
        if not content:
            content = soup.find("body") or soup
        
        # Extract text from <p> tags for cleaner output
        paragraphs = content.find_all("p")
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            text = content.get_text(separator=" ", strip=True)
        
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        return text[:MAX_ARTICLE_TEXT_CHARS]
        
    except Exception as e:
        if verbose:
            print(f"      ⚠️  Could not fetch article text: {e}")
        return ""


def parse_date(entry) -> datetime | None:
    """Parse publish date from RSS entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    return None


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "can", "shall", "it", "its",
        "this", "that", "these", "those", "i", "you", "he", "she", "we",
        "they", "my", "your", "his", "her", "our", "their", "what", "which",
        "who", "whom", "how", "when", "where", "why", "not", "no", "nor",
        "so", "if", "then", "than", "too", "very", "just", "about", "up",
        "out", "off", "over", "under", "again", "further", "once", "here",
        "there", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "only", "own", "same", "as", "into",
        "through", "during", "before", "after", "above", "below", "between",
        "new", "says", "said", "also", "like", "get", "got", "make",
        "made", "us", "use", "used", "one", "two", "first",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in stop_words]


def is_similar(title1: str, title2: str, threshold: float = 0.6) -> bool:
    """Check if two titles are similar enough to be duplicates."""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() > threshold


def scrape_feeds(verbose: bool = False) -> list[dict]:
    """
    Scrape all configured RSS feeds and return a list of article dicts.
    
    Each article has:
        - title: str
        - description: str
        - link: str
        - source: str
        - category: str
        - published: datetime
        - keywords: list[str]
        - article_text: str (populated later for selected articles)
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=ARTICLE_AGE_HOURS)
    all_articles = []

    for feed_config in RSS_FEEDS:
        url = feed_config["url"]
        source_name = feed_config["name"]
        source_category = feed_config["category"]

        if verbose:
            print(f"  📡 Fetching: {source_name} ({url})")

        try:
            resp = requests.get(url, headers=HTTP_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        except Exception as e:
            if verbose:
                print(f"    ⚠️  Failed to fetch {source_name}: {e}")
            continue

        if not feed.entries:
            if verbose:
                print(f"    ⚠️  No entries found in {source_name}")
            continue

        count = 0
        skipped = 0
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title = clean_html(getattr(entry, "title", ""))
            if not title:
                continue

            description = clean_html(
                getattr(entry, "description", "") or
                getattr(entry, "summary", "")
            )
            
            # Strip boilerplate from description
            description = strip_boilerplate(description)

            pub_date = parse_date(entry)
            
            if pub_date and pub_date < cutoff:
                continue
            
            # Skip promo/ad articles
            if is_promo_article(title, description):
                skipped += 1
                continue

            entry_categories = []
            if hasattr(entry, "tags"):
                entry_categories = [t.term for t in entry.tags if hasattr(t, "term")]

            text = f"{title} {description} {' '.join(entry_categories)}"
            keywords = extract_keywords(text)

            # Truncate description at sentence boundary (up to 500 chars)
            truncated_desc = description[:500]
            if len(description) > 500:
                for sep in ['. ', '! ', '? ']:
                    last_sep = truncated_desc.rfind(sep)
                    if last_sep > 200:
                        truncated_desc = truncated_desc[:last_sep + 1]
                        break

            article = {
                "title": title,
                "description": truncated_desc,
                "link": getattr(entry, "link", ""),
                "source": source_name,
                "category": source_category,
                "published": pub_date or datetime.now(timezone.utc),
                "keywords": keywords,
                "entry_categories": entry_categories,
                "article_text": "",  # Populated later for selected articles
            }
            all_articles.append(article)
            count += 1

        if verbose:
            msg = f"    ✅ Found {count} articles from {source_name}"
            if skipped:
                msg += f" (skipped {skipped} promos)"
            print(msg)

    unique_articles = deduplicate(all_articles)
    unique_articles.sort(key=lambda a: a["published"], reverse=True)

    if verbose:
        print(f"\n  📊 Total: {len(all_articles)} articles → {len(unique_articles)} unique")

    return unique_articles


def fetch_article_texts(articles: list[dict], verbose: bool = False) -> None:
    """Fetch full article body text for the given articles (in-place)."""
    if verbose:
        print(f"\n  📄 Fetching full article text for {len(articles)} articles...")
    
    for i, article in enumerate(articles):
        if article.get("article_text"):
            continue
        article["article_text"] = fetch_article_text(
            article["link"], verbose=verbose
        )
        if verbose:
            text_len = len(article["article_text"])
            status = f"{text_len} chars" if text_len > 0 else "failed"
            print(f"    {i+1}. [{status}] {article['title'][:60]}")


def deduplicate(articles: list[dict]) -> list[dict]:
    """Remove duplicate articles based on title similarity."""
    unique = []
    for article in articles:
        is_dup = False
        for existing in unique:
            if is_similar(article["title"], existing["title"]):
                is_dup = True
                break
        if not is_dup:
            unique.append(article)
    return unique


if __name__ == "__main__":
    print("🔍 Scraping RSS feeds...\n")
    articles = scrape_feeds(verbose=True)
    print(f"\n{'='*60}")
    for i, a in enumerate(articles[:10], 1):
        print(f"\n{i}. [{a['source']}] {a['title']}")
        print(f"   {a['description'][:100]}...")
        print(f"   Keywords: {', '.join(a['keywords'][:5])}")
