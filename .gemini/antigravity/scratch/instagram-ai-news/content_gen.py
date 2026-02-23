"""
Content Generator — Analyzes scraped articles and generates carousel content.
Identifies trending topics, clusters articles, uses Gemini AI to generate
high-quality summaries and takeaways from full article text.
"""

import json
import time
from collections import Counter
from config import (
    NUM_CAROUSEL_SLIDES, TOPIC_ICONS, CAPTION_TEMPLATE,
    GEMINI_API_KEY, GEMINI_MODEL, SUMMARIZE_PROMPT,
)


# ─── Gemini AI Summarization ─────────────────────────────────────────

def summarize_with_gemini(article: dict, verbose: bool = False) -> dict | None:
    """
    Use Gemini to generate a headline, insight, and takeaways from article text.
    Returns dict with 'headline', 'insight', 'takeaways' or None on failure.
    Retries with exponential backoff; falls back to alternate models on quota errors.
    """
    if not GEMINI_API_KEY:
        return None
    
    text = article.get("article_text", "") or article.get("description", "")
    if not text or len(text) < 50:
        return None
    
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = SUMMARIZE_PROMPT.format(
        title=article["title"],
        source=article["source"],
        text=text[:2500],
    )
    
    # Try primary model first, then fallback
    models_to_try = [GEMINI_MODEL, "gemini-2.0-flash-lite"]
    
    for model_name in models_to_try:
        for attempt in range(2):  # 2 attempts per model
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw = response.text.strip()
                
                # Clean up markdown code blocks if present
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
                
                result = json.loads(raw)
                
                if "headline" in result and "insight" in result and "takeaways" in result:
                    if verbose:
                        print(f"      ✨ AI ({model_name}): \"{result['headline'][:50]}...\"")
                    return result
                    
            except json.JSONDecodeError as e:
                if verbose:
                    print(f"      ⚠️  JSON parse error: {e}")
                break  # Don't retry parse errors, try next model
            except Exception as e:
                err_str = str(e)
                if "404" in err_str:
                    if verbose:
                        print(f"      ⚠️  Model {model_name} not available, skipping...")
                    break  # Model doesn't exist, try next
                elif "429" in err_str or "quota" in err_str.lower():
                    if attempt == 0:
                        wait = 3
                        if verbose:
                            print(f"      ⏳ Rate limit on {model_name}, waiting {wait}s...")
                        time.sleep(wait)
                        continue
                    else:
                        if verbose:
                            print(f"      ⚠️  Quota exceeded on {model_name}, trying next model...")
                        break  # Try next model
                else:
                    if verbose:
                        print(f"      ⚠️  Gemini error: {e}")
                    return None  # Non-transient error, stop entirely
    
    return None


def truncate_at_sentence(text: str, max_len: int, min_len: int = 80) -> str:
    """Truncate text at the nearest sentence boundary within max_len."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    for sep in ['. ', '! ', '? ']:
        last_sep = truncated.rfind(sep)
        if last_sep >= min_len:
            return truncated[:last_sep + 1].strip()
    last_space = truncated.rfind(' ')
    if last_space >= min_len:
        return truncated[:last_space].strip() + '...'
    return truncated.strip() + '...'


# ─── Topic Mapping ───────────────────────────────────────────────────

TOPIC_MAP = {
    # AI Topics
    "openai": "AI & LLMs",
    "chatgpt": "AI & LLMs",
    "gpt": "AI & LLMs",
    "llm": "AI & LLMs",
    "llms": "AI & LLMs",
    "claude": "AI & LLMs",
    "anthropic": "AI & LLMs",
    "gemini": "AI & LLMs",
    "copilot": "AI & LLMs",
    "language model": "AI & LLMs",
    "generative": "Generative AI",
    "diffusion": "Generative AI",
    "midjourney": "Generative AI",
    "image generation": "Generative AI",
    "deepfake": "Generative AI",
    "nvidia": "AI Hardware",
    "chip": "AI Hardware",
    "chips": "AI Hardware",
    "gpu": "AI Hardware",
    "tpu": "AI Hardware",
    "semiconductor": "AI Hardware",
    "safety": "AI Safety & Ethics",
    "regulation": "AI Safety & Ethics",
    "bias": "AI Safety & Ethics",
    "ethics": "AI Safety & Ethics",
    "alignment": "AI Safety & Ethics",
    "privacy": "AI Safety & Ethics",
    "autonomous": "Autonomous & Robotics",
    "robot": "Autonomous & Robotics",
    "robotics": "Autonomous & Robotics",
    "self-driving": "Autonomous & Robotics",
    "drone": "Autonomous & Robotics",
    "drones": "Autonomous & Robotics",
    "agents": "AI Agents",
    "agent": "AI Agents",
    "agentic": "AI Agents",
    "startup": "AI Startups & Funding",
    "startups": "AI Startups & Funding",
    "funding": "AI Startups & Funding",
    "venture": "AI Startups & Funding",
    "million": "AI Startups & Funding",
    "billion": "AI Startups & Funding",
    "raises": "AI Startups & Funding",
    "series": "AI Startups & Funding",
    "defense": "AI & Defense",
    "military": "AI & Defense",
    "pentagon": "AI & Defense",
    "weapons": "AI & Defense",
    # DevOps Topics
    "kubernetes": "Cloud & Containers",
    "docker": "Cloud & Containers",
    "container": "Cloud & Containers",
    "containers": "Cloud & Containers",
    "cloud": "Cloud & Containers",
    "aws": "Cloud & Containers",
    "azure": "Cloud & Containers",
    "gcp": "Cloud & Containers",
    "devops": "DevOps & CI/CD",
    "cicd": "DevOps & CI/CD",
    "pipeline": "DevOps & CI/CD",
    "deployment": "DevOps & CI/CD",
    "terraform": "Infrastructure as Code",
    "infrastructure": "Infrastructure as Code",
    "iac": "Infrastructure as Code",
    "ansible": "Infrastructure as Code",
    "security": "Security & Compliance",
    "vulnerability": "Security & Compliance",
    "cybersecurity": "Security & Compliance",
    "breach": "Security & Compliance",
    "observability": "Observability & Monitoring",
    "monitoring": "Observability & Monitoring",
    "logging": "Observability & Monitoring",
    "metrics": "Observability & Monitoring",
    # General Tech
    "data center": "Data Centers & Energy",
    "energy": "Data Centers & Energy",
    "climate": "Data Centers & Energy",
    "environment": "Data Centers & Energy",
    "search": "AI in Search",
    "google": "AI in Search",
    "perplexity": "AI in Search",
    "meta": "Big Tech & AI",
    "apple": "Big Tech & AI",
    "microsoft": "Big Tech & AI",
    "research": "AI Research",
    "paper": "AI Research",
    "breakthrough": "AI Research",
}


def get_topic_for_keyword(keyword: str) -> str | None:
    """Map a keyword to a broader topic."""
    return TOPIC_MAP.get(keyword.lower())


def get_icon_for_topic(topic: str) -> str:
    """Get an emoji icon for a topic."""
    topic_lower = topic.lower()
    for key, icon in TOPIC_ICONS.items():
        if key in topic_lower:
            return icon
    return TOPIC_ICONS["default"]


def _extract_takeaways_from_text(article_text: str, description: str) -> list[str]:
    """
    Extract 2-3 key takeaway sentences from the article's own body text.
    Prioritizes sentences with numbers, stats, or strong claims.
    Skips sentences too similar to the insight/description.
    """
    import re
    from difflib import SequenceMatcher
    
    text = article_text or ""
    if len(text) < 100:
        return []
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Skip first 2 sentences — they usually overlap with the insight/description
    sentences = sentences[2:] if len(sentences) > 4 else sentences[1:]
    
    # Filter out noise
    candidates = []
    seen_starts = set()
    skip_patterns = [
        "cookie", "subscribe", "sign up", "newsletter", "click here",
        "read more", "advertisement", "sponsored", "terms of",
        "privacy policy", "copyright", "follow us", "follow equity",
        "twitter", "threads", "@equitypod", "@techcrunch",
        "comment", "related:", "see also", "table of contents",
        "photo by", "image credit", "getty", "shutterstock",
        "appeared first on", "this article", "we may earn",
        "disclosure", "affiliate", "podcast", "episode",
    ]
    
    desc_lower = (description or "").lower()[:100]
    
    for s in sentences:
        s = s.strip()
        if len(s) < 40 or len(s) > 150:
            continue
        s_lower = s.lower()
        if any(skip in s_lower for skip in skip_patterns):
            continue
        # Avoid duplicate-ish sentences
        start = s_lower[:30]
        if start in seen_starts:
            continue
        seen_starts.add(start)
        # Skip if too similar to the description/insight
        if desc_lower and SequenceMatcher(None, s_lower[:80], desc_lower[:80]).ratio() > 0.5:
            continue
        candidates.append(s)
    
    if not candidates:
        return []
    
    # Score sentences: prefer those with numbers, stats, or strong signal words
    signal_words = [
        "billion", "million", "percent", "%", "$",
        "first", "new", "launch", "announce", "release",
        "increase", "decrease", "grow", "decline",
        "according", "report", "study", "research",
        "key", "major", "significant", "critical",
        "expect", "predict", "plan", "partner",
    ]
    
    scored = []
    for s in candidates:
        score = 0
        s_lower = s.lower()
        for word in signal_words:
            if word in s_lower:
                score += 1
        if re.search(r'\d', s):
            score += 2
        scored.append((score, s))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    takeaways = [truncate_at_sentence(s, 85, min_len=30) for _, s in scored[:3]]
    
    return takeaways


# ─── Trend Analysis ──────────────────────────────────────────────────

def analyze_trends(articles: list[dict], verbose: bool = False) -> list[dict]:
    """
    Analyze articles and identify trending topics.
    For each selected topic, fetches full article text and uses Gemini AI
    to generate high-quality slide content.
    """
    from scraper import fetch_article_texts
    
    # Count topic occurrences across all articles
    topic_articles: dict[str, list[dict]] = {}
    
    for article in articles:
        matched_topics = set()
        
        for kw in article["keywords"]:
            topic = get_topic_for_keyword(kw)
            if topic:
                matched_topics.add(topic)
        
        title_lower = article["title"].lower()
        for key, topic in TOPIC_MAP.items():
            if key in title_lower:
                matched_topics.add(topic)
        
        for topic in matched_topics:
            if topic not in topic_articles:
                topic_articles[topic] = []
            topic_articles[topic].append(article)

    # Rank topics by article count
    ranked_topics = sorted(
        topic_articles.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    if verbose:
        print("\n  📈 Topic rankings:")
        for topic, articles_list in ranked_topics[:10]:
            print(f"    {get_icon_for_topic(topic)} {topic}: {len(articles_list)} articles")

    # Build carousel content for top topics
    num_trends = NUM_CAROUSEL_SLIDES - 1
    trends = []
    used_article_titles = set()
    
    # First pass: select the best article for each topic
    selected_articles = []
    
    for topic, topic_arts in ranked_topics[:num_trends + 3]:
        if len(selected_articles) >= num_trends:
            break
        
        candidates = sorted(
            topic_arts,
            key=lambda a: (len(a["description"]), a["published"]),
            reverse=True
        )
        best = None
        for candidate in candidates:
            if candidate["title"] not in used_article_titles:
                best = candidate
                break
        if best is None:
            continue
        
        used_article_titles.add(best["title"])
        selected_articles.append((topic, topic_arts, best))
    
    # Fetch full article text for selected articles only
    articles_to_fetch = [item[2] for item in selected_articles]
    fetch_article_texts(articles_to_fetch, verbose=verbose)
    
    # Generate AI summaries for each selected article
    use_ai = bool(GEMINI_API_KEY)
    if use_ai and verbose:
        print("\n  🤖 Generating AI summaries with Gemini...")
    
    for topic, topic_arts, best in selected_articles:
        ai_result = None
        if use_ai:
            ai_result = summarize_with_gemini(best, verbose=verbose)
            time.sleep(0.5)  # Rate limiting: stay under 15 RPM
        
        if ai_result:
            headline = ai_result["headline"]
            insight = ai_result["insight"]
            takeaways = ai_result.get("takeaways", [])[:3]
        else:
            # Fallback to RSS-based content
            headline = best["title"]
            insight = truncate_at_sentence(best["description"], 300)
            # Extract takeaways from the article's own body text
            takeaways = _extract_takeaways_from_text(
                best.get("article_text", ""), best.get("description", "")
            )
        
        all_sources = sorted(set(a["source"] for a in topic_arts))
        
        trends.append({
            "topic": topic,
            "icon": get_icon_for_topic(topic),
            "count": len(topic_arts),
            "articles": topic_arts,
            "headline": headline,
            "insight": insight,
            "source": best["source"],
            "source_count": len(all_sources),
            "all_sources": all_sources,
            "takeaways": takeaways,
            "ai_generated": ai_result is not None,
        })

    # Fill with individual articles if needed
    if len(trends) < num_trends:
        for article in articles:
            if len(trends) >= num_trends:
                break
            if article["title"] not in used_article_titles:
                headline = article["title"]
                insight = truncate_at_sentence(article["description"], 300)
                
                used_article_titles.add(article["title"])
                trends.append({
                    "topic": article.get("entry_categories", ["Tech News"])[0]
                             if article.get("entry_categories") else "Tech News",
                    "icon": "📡",
                    "count": 1,
                    "articles": [article],
                    "headline": headline,
                    "insight": insight,
                    "source": article["source"],
                    "source_count": 1,
                    "all_sources": [article["source"]],
                    "takeaways": [],
                    "ai_generated": False,
                })

    return trends


# ─── Caption Generation ──────────────────────────────────────────────

def generate_caption(trends: list[dict]) -> str:
    """Generate an Instagram caption from the trending topics."""
    title = "Today's Top AI & DevOps Trends"
    
    summary_lines = []
    for i, trend in enumerate(trends, 1):
        summary_lines.append(f"{trend['icon']} {trend['topic']}: {trend['headline']}")
    summary = "\n".join(summary_lines)
    
    topic_hashtags = set()
    for trend in trends:
        for word in trend["topic"].split():
            if len(word) > 2:
                topic_hashtags.add(f"#{word}")
    hashtags = " ".join(list(topic_hashtags)[:8])
    
    all_sources = set()
    for trend in trends:
        for article in trend["articles"]:
            all_sources.add(article["source"])
    sources = ", ".join(all_sources)
    
    caption = CAPTION_TEMPLATE.format(
        title=title,
        summary=summary,
        hashtags=hashtags,
        sources=sources,
    )
    
    return caption.strip()


if __name__ == "__main__":
    from scraper import scrape_feeds
    
    print("🔍 Scraping feeds...")
    articles = scrape_feeds(verbose=True)
    
    print("\n📊 Analyzing trends...")
    trends = analyze_trends(articles, verbose=True)
    
    print(f"\n{'='*60}")
    print(f"Top {len(trends)} Trending Topics:\n")
    for i, t in enumerate(trends, 1):
        ai_badge = " 🤖" if t.get("ai_generated") else ""
        print(f"{i}. {t['icon']} {t['topic']} ({t['count']} articles){ai_badge}")
        print(f"   📰 {t['headline']}")
        print(f"   💡 {t['insight'][:120]}...")
        if t.get("takeaways"):
            for ta in t["takeaways"]:
                print(f"   • {ta}")
        print(f"   📡 Source: {t['source']}")
        print()
    
    print(f"{'='*60}")
    print("📝 Generated Caption:\n")
    print(generate_caption(trends))
