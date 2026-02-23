# 📡 Instagram AI & DevOps News Automation

Automatically scrape the latest AI and DevOps news from RSS feeds, generate beautiful carousel images, and post them to Instagram — **completely free**.

## ✨ Features

- 🔍 **Multi-source RSS scraping** — Wired AI, TechCrunch, DevOps.com, The New Stack, MIT AI News
- 📊 **Smart trend analysis** — Clusters articles by topic, identifies top trends
- 🎨 **Professional carousel images** — Generated with Python Pillow (no paid API)
- 📱 **Auto Instagram posting** — Via instagrapi (free, open-source)
- ⏰ **Scheduled automation** — GitHub Actions (free) or local cron
- 🏃 **Dry-run mode** — Test without posting

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd instagram-ai-news
pip install -r requirements.txt
```

### 2. Configure Credentials

```bash
cp .env.example .env
# Edit .env with your Instagram username and password
```

### 3. Run (Dry Run First!)

```bash
# Generate images without posting (recommended first!)
python main.py --dry-run --verbose

# Full run — generates AND posts to Instagram
python main.py --verbose
```

### 4. Check Output

Generated carousel images will be in the `output/` folder.

## 📁 Project Structure

```
instagram-ai-news/
├── main.py             # 🎯 Main orchestrator (run this!)
├── config.py           # ⚙️  All settings in one place
├── scraper.py          # 📡 RSS feed scraper
├── content_gen.py      # 📊 Trend analyzer & content generator
├── image_gen.py        # 🎨 Carousel image generator (Pillow)
├── instagram_post.py   # 📱 Instagram poster (instagrapi)
├── requirements.txt    # 📦 Python dependencies
├── .env.example        # 🔑 Credentials template
├── .gitignore          # 🙈 Git ignore rules
├── .github/workflows/
│   └── post.yml        # ⏰ GitHub Actions daily schedule
├── output/             # 📸 Generated images (auto-created)
└── fonts/              # 🔤 Cached Google Fonts (auto-downloaded)
```

## ⚙️ Customization

### Add/Remove RSS Feeds

Edit `config.py` → `RSS_FEEDS` list:

```python
RSS_FEEDS = [
    {"url": "https://your-feed.com/rss", "name": "Your Feed", "category": "AI"},
    # ... add more
]
```

### Change Colors & Branding

Edit `config.py`:
- `COLOR_PALETTES` — Gradient colors for each slide
- `BRAND_NAME` — Your brand name on slides
- `BRAND_HANDLE` — Your Instagram handle
- `BRAND_TAGLINE` — Tagline on cover slide

### Adjust Posting Schedule

Edit `.github/workflows/post.yml`:
```yaml
on:
  schedule:
    - cron: '0 14 * * *'  # 9 AM EST / 2 PM UTC
```

## ☁️ GitHub Actions Setup (Free Automation)

1. Push this repo to GitHub (public repo = free Actions minutes)
2. Go to **Settings → Secrets and variables → Actions**
3. Add secrets:
   - `INSTAGRAM_USERNAME` — Your IG username
   - `INSTAGRAM_PASSWORD` — Your IG password
4. GitHub Actions will automatically run daily!

## 🖥️ Local Cron Setup (Alternative)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM):
0 9 * * * cd /path/to/instagram-ai-news && /usr/bin/python3 main.py --verbose >> /tmp/ig-automation.log 2>&1
```

## 💡 CLI Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Generate images but skip Instagram posting |
| `--verbose` / `-v` | Show detailed progress output |
| `--no-images` | Skip image generation (test scraper only) |
| `--no-clean` | Keep old images in output folder |

## ⚠️ Important Notes

- **Instagram risk**: `instagrapi` uses Instagram's unofficial API. Use responsibly and add delays between runs to avoid restrictions.
- **2FA**: If your account has 2FA, you may need to handle verification challenges the first time.
- **Public repo**: If using GitHub Actions, make sure you use **Secrets** for credentials, never commit `.env`.
- **Rate limits**: Don't run more than once per day to stay safe.

## 💰 Cost Breakdown

| Component | Cost |
|-----------|------|
| RSS scraping (`feedparser`) | Free |
| Image generation (`Pillow`) | Free |
| Instagram posting (`instagrapi`) | Free |
| Automation (GitHub Actions) | Free (public repo) |
| Fonts (Google Fonts) | Free |
| **Total** | **$0/month** |
