"""
Configuration for AI/DevOps News Carousel Generator.
All settings are centralized here for easy customization.
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ─── RSS Feed Sources ────────────────────────────────────────────────
RSS_FEEDS = [
    {
        "url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "name": "Wired AI",
        "category": "AI"
    },
    {
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "name": "TechCrunch AI",
        "category": "AI"
    },
    {
        "url": "https://thenewstack.io/blog/feed/",
        "name": "The New Stack",
        "category": "DevOps"
    },
    {
        "url": "https://devops.com/feed/",
        "name": "DevOps.com",
        "category": "DevOps"
    },
    {
        "url": "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml",
        "name": "MIT AI News",
        "category": "AI"
    },
    {
        "url": "https://www.artificialintelligence-news.com/feed/",
        "name": "AI News",
        "category": "AI"
    },
]

# ─── Scraping Settings ───────────────────────────────────────────────
MAX_ARTICLES_PER_FEED = 15
ARTICLE_AGE_HOURS = 72  # Consider articles from last 72 hours

# Keywords that indicate promo/ad articles (skip these)
PROMO_KEYWORDS = [
    "disrupt 2026", "disrupt 2025", "save $", "register now", "subscribe",
    "early bird", "ticket", "pricing", "discount", "coupon", "promo code",
    "webinar", "sign up for", "join us", "sponsored",
]

# Boilerplate patterns to strip from descriptions
BOILERPLATE_PATTERNS = [
    r"The post .+? appeared first on .+?\.",
    r"Continue reading\.{0,3}$",
    r"Read more\.{0,3}$",
    r"\[\.\.\.$",
]

# ─── Gemini AI Settings ─────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"

SUMMARIZE_PROMPT = """You are a tech news analyst for an Instagram carousel about AI and DevOps trends.

Given this article text, generate content for an Instagram carousel slide. Return ONLY valid JSON with these fields:

{{
  "headline": "A compelling, attention-grabbing headline (max 80 chars). Should communicate the key news clearly.",
  "insight": "A 2-3 sentence summary explaining WHY this matters and WHAT the impact is. Should provide real value and context, not just restate the headline. Max 250 chars.",
  "takeaways": [
    "First actionable or interesting takeaway (max 80 chars)",
    "Second takeaway (max 80 chars)",
    "Third takeaway (max 80 chars)"
  ]
}}

Rules:
- headline: Be specific and punchy. Use numbers/stats when available.
- insight: Explain the significance. Why should a tech professional care?
- takeaways: Concrete facts, stats, or implications. Not generic statements.
- Do NOT include any markdown formatting, code blocks, or extra text. Return ONLY the JSON object.

Article title: {title}
Source: {source}
Article text:
{text}
"""

# ─── Image Generation Settings ───────────────────────────────────────
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350
NUM_CAROUSEL_SLIDES = 5  # 1 cover + 4 trend slides
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# ─── Color Palettes (Modern Dark Theme) ──────────────────────────────
# Each slide gets a different gradient palette
COLOR_PALETTES = [
    # Cover slide: Deep purple to dark blue
    {
        "bg_start": (20, 10, 50),
        "bg_end": (10, 25, 80),
        "accent": (138, 96, 255),       # Bright purple
        "text_primary": (255, 255, 255),
        "text_secondary": (180, 180, 210),
        "highlight": (255, 107, 157),    # Pink accent
    },
    # Slide 2: Dark teal
    {
        "bg_start": (8, 20, 35),
        "bg_end": (15, 45, 60),
        "accent": (0, 210, 190),         # Teal
        "text_primary": (255, 255, 255),
        "text_secondary": (170, 210, 210),
        "highlight": (255, 200, 50),     # Gold accent
    },
    # Slide 3: Dark crimson
    {
        "bg_start": (35, 8, 18),
        "bg_end": (60, 15, 35),
        "accent": (255, 75, 110),        # Crimson
        "text_primary": (255, 255, 255),
        "text_secondary": (220, 180, 190),
        "highlight": (255, 180, 80),     # Orange accent
    },
    # Slide 4: Dark emerald
    {
        "bg_start": (8, 30, 20),
        "bg_end": (15, 55, 40),
        "accent": (50, 215, 130),        # Emerald
        "text_primary": (255, 255, 255),
        "text_secondary": (180, 220, 200),
        "highlight": (100, 200, 255),    # Sky blue accent
    },
    # Slide 5: Dark amber/orange
    {
        "bg_start": (35, 20, 8),
        "bg_end": (60, 35, 12),
        "accent": (255, 170, 50),        # Amber
        "text_primary": (255, 255, 255),
        "text_secondary": (220, 200, 170),
        "highlight": (150, 130, 255),    # Lavender accent
    },
]

# ─── Topic Icons (Unicode for visual flair) ──────────────────────────
TOPIC_ICONS = {
    "ai": "🤖",
    "machine learning": "🧠",
    "deep learning": "🧠",
    "llm": "💬",
    "chatbot": "💬",
    "robotics": "🦾",
    "autonomous": "🚗",
    "data": "📊",
    "cloud": "☁️",
    "devops": "⚙️",
    "kubernetes": "🐳",
    "docker": "🐳",
    "security": "🔒",
    "privacy": "🛡️",
    "startup": "🚀",
    "funding": "💰",
    "research": "🔬",
    "chip": "🔲",
    "gpu": "🔲",
    "energy": "⚡",
    "default": "📡",
}

# ─── Branding ─────────────────────────────────────────────────────────
BRAND_NAME = "AI & DevOps Daily"
BRAND_HANDLE = "@your_handle"  # Change to your IG handle
BRAND_TAGLINE = "Your daily dose of tech trends"

# ─── Instagram Caption Template ──────────────────────────────────────
CAPTION_TEMPLATE = """🔥 {title}

{summary}

Swipe ➡️ for today's top AI & DevOps trends!

{hashtags}

📡 Sources: {sources}
🤖 Auto-generated from latest tech news

#AI #DevOps #TechNews #MachineLearning #CloudComputing #DataScience #TechTrends #ArtificialIntelligence #Automation #SoftwareEngineering
"""

# ─── Article Scraping Settings ──────────────────────────────────────────────
MAX_ARTICLE_TEXT_CHARS = 3000  # Max chars to extract from article body
ARTICLE_FETCH_TIMEOUT = 10  # Seconds to wait for article page
