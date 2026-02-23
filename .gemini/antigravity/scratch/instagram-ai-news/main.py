#!/usr/bin/env python3
"""
Instagram AI/DevOps News Automation — Main Orchestrator

Scrapes AI/DevOps RSS feeds, analyzes trends, and generates carousel images.
Images are saved to the output/ folder for you to post manually.

Usage:
    python3 main.py                  # Generate carousel images
    python3 main.py --verbose        # Show detailed progress
    python3 main.py --no-images      # Test scraper only (skip image gen)
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime

from scraper import scrape_feeds
from content_gen import analyze_trends, generate_caption
from image_gen import generate_carousel
from config import OUTPUT_DIR


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def clean_output_dir():
    """Remove old image files from output directory."""
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith((".jpg", ".jpeg", ".png")):
                os.remove(os.path.join(OUTPUT_DIR, f))


def main():
    parser = argparse.ArgumentParser(
        description="Instagram AI/DevOps News Carousel Generator"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed progress output"
    )
    parser.add_argument(
        "--no-images", action="store_true",
        help="Skip image generation (useful for testing scraper only)"
    )
    parser.add_argument(
        "--no-clean", action="store_true",
        help="Don't clean output directory before generating"
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    start_time = time.time()
    print("\n" + "=" * 60)
    print("🚀 Instagram AI/DevOps News Carousel Generator")
    print(f"📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 60)
    
    # ─── Step 1: Scrape RSS Feeds ─────────────────────────────────
    print("\n📡 Step 1/3: Scraping RSS feeds...")
    try:
        articles = scrape_feeds(verbose=args.verbose)
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        print(f"\n❌ Scraping failed: {e}")
        sys.exit(1)
    
    if not articles:
        print("\n⚠️  No articles found! Check your internet connection or RSS feeds.")
        sys.exit(1)
    
    print(f"\n  ✅ Found {len(articles)} articles")
    
    # ─── Step 2: Analyze Trends ───────────────────────────────────
    print("\n📊 Step 2/3: Analyzing trends...")
    try:
        trends = analyze_trends(articles, verbose=args.verbose)
    except Exception as e:
        logging.error(f"Trend analysis failed: {e}")
        print(f"\n❌ Trend analysis failed: {e}")
        sys.exit(1)
    
    if not trends:
        print("\n⚠️  No trends identified! Not enough data to generate carousel.")
        sys.exit(1)
    
    print(f"\n  ✅ Identified {len(trends)} trending topics:")
    for i, t in enumerate(trends, 1):
        print(f"    {i}. {t['icon']} {t['topic']} — {t['headline'][:50]}...")
    
    # Generate caption
    caption = generate_caption(trends)
    
    # Save caption to file
    caption_path = os.path.join(OUTPUT_DIR, "caption.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(caption_path, "w") as f:
        f.write(caption)
    print(f"\n  📝 Caption saved to: {caption_path}")
    
    # ─── Step 3: Generate Carousel Images ─────────────────────────
    if args.no_images:
        print("\n🖼️  Step 3/3: Skipped (--no-images)")
        image_paths = []
    else:
        print("\n🎨 Step 3/3: Generating carousel images...")
        
        if not args.no_clean:
            clean_output_dir()
        
        try:
            image_paths = generate_carousel(trends, verbose=args.verbose)
        except Exception as e:
            logging.error(f"Image generation failed: {e}")
            print(f"\n❌ Image generation failed: {e}")
            sys.exit(1)
        
        print(f"\n  ✅ Generated {len(image_paths)} carousel images")
        for path in image_paths:
            print(f"    📸 {os.path.basename(path)}")
    
    # ─── Done ─────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"✅ Done in {elapsed:.1f}s")
    if image_paths:
        print(f"📁 Images saved to: {OUTPUT_DIR}")
        print(f"📝 Caption saved to: {caption_path}")
    print(f"\n💡 Post the images from output/ to Instagram manually!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
