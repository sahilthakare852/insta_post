"""
Image Generator — Creates professional carousel images for Instagram using Pillow.
Generates 5 slides (1080×1350): 1 cover + 4 trend cards with gradient backgrounds,
modern typography, and visual hierarchy.
"""

import os
import math
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
from config import (
    IMAGE_WIDTH, IMAGE_HEIGHT, OUTPUT_DIR, FONTS_DIR,
    COLOR_PALETTES, BRAND_NAME, BRAND_HANDLE, BRAND_TAGLINE,
)


# ─── Font Management ─────────────────────────────────────────────────

# Direct download URLs for Inter font static TTFs
FONT_URLS = {
    "bold": "https://github.com/rsms/inter/raw/v4.0/docs/font-files/Inter-Bold.woff2",
    "semibold": "https://github.com/rsms/inter/raw/v4.0/docs/font-files/Inter-SemiBold.woff2",
    "regular": "https://github.com/rsms/inter/raw/v4.0/docs/font-files/Inter-Regular.woff2",
    "medium": "https://github.com/rsms/inter/raw/v4.0/docs/font-files/Inter-Medium.woff2",
}
FONT_FILENAMES = {
    "bold": "Inter-Bold.woff2",
    "semibold": "Inter-SemiBold.woff2",
    "regular": "Inter-Regular.woff2",
    "medium": "Inter-Medium.woff2",
}


def download_fonts():
    """Download fonts if not already cached. Uses system fonts as primary fallback."""
    os.makedirs(FONTS_DIR, exist_ok=True)
    
    # On macOS, prefer system fonts for best quality and emoji support
    # Only download if system fonts are unavailable (e.g., Linux CI)
    system_font_available = any(
        os.path.exists(p) for p in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSText.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    )
    if system_font_available:
        return  # System fonts are fine, no need to download


def get_font(style: str = "regular", size: int = 32) -> ImageFont.FreeTypeFont:
    """Get a font by style and size. Uses system fonts with weight matching."""
    # Map styles to macOS system fonts with weight indices
    macos_fonts = {
        "bold": ("/System/Library/Fonts/Helvetica.ttc", 1),    # Bold weight
        "semibold": ("/System/Library/Fonts/Helvetica.ttc", 0), # Regular (closest)
        "medium": ("/System/Library/Fonts/Helvetica.ttc", 0),
        "regular": ("/System/Library/Fonts/Helvetica.ttc", 0),
    }
    
    # Try macOS system font
    if style in macos_fonts:
        path, index = macos_fonts[style]
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except Exception:
                pass
    
    # Fallback: try other system fonts
    fallbacks = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if style == "bold" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fb in fallbacks:
        if os.path.exists(fb):
            try:
                return ImageFont.truetype(fb, size)
            except Exception:
                continue
    
    # Check if we downloaded any fonts
    if style in FONT_FILENAMES:
        filepath = os.path.join(FONTS_DIR, FONT_FILENAMES[style])
        if os.path.exists(filepath):
            return ImageFont.truetype(filepath, size)
    
    return ImageFont.load_default()


# ─── Drawing Helpers ──────────────────────────────────────────────────

def draw_gradient(draw: ImageDraw.Draw, width: int, height: int,
                  color_start: tuple, color_end: tuple, direction: str = "diagonal"):
    """Draw a smooth gradient background."""
    for y in range(height):
        for x in range(width):
            if direction == "diagonal":
                t = (x / width * 0.5 + y / height * 0.5)
            elif direction == "vertical":
                t = y / height
            else:
                t = x / width
            
            r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
            draw.point((x, y), fill=(r, g, b))


def create_gradient_image(width: int, height: int,
                          color_start: tuple, color_end: tuple) -> Image.Image:
    """Create a gradient background image (optimized with numpy-like approach)."""
    img = Image.new("RGB", (width, height))
    
    # Create gradient line by line for better performance
    for y in range(height):
        t = y / height
        r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
        
        for x in range(width):
            # Add slight horizontal variation for diagonal feel
            tx = x / width * 0.3
            rx = int(min(255, max(0, r + (color_end[0] - color_start[0]) * tx * 0.3)))
            gx = int(min(255, max(0, g + (color_end[1] - color_start[1]) * tx * 0.3)))
            bx = int(min(255, max(0, b + (color_end[2] - color_start[2]) * tx * 0.3)))
            img.putpixel((x, y), (rx, gx, bx))
    
    return img


def draw_rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int,
                      fill: tuple = None, outline: tuple = None, width: int = 1):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_decorative_elements(draw: ImageDraw.Draw, width: int, height: int,
                             accent_color: tuple, opacity: int = 30):
    """Add subtle decorative geometric elements to the background."""
    # Top-right circle cluster
    for i in range(3):
        cx = width - 100 + i * 40
        cy = 100 - i * 30
        r = 60 + i * 20
        circle_color = (*accent_color, opacity)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=None,
            outline=(*accent_color[:3], opacity + 20),
            width=2
        )
    
    # Bottom-left geometric lines
    for i in range(5):
        y_pos = height - 200 + i * 25
        x_end = 150 - i * 20
        draw.line(
            [(0, y_pos), (x_end, y_pos)],
            fill=(*accent_color[:3], opacity),
            width=1
        )


def draw_text_wrapped(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                      max_width: int, x: int, y: int, fill: tuple,
                      line_spacing: int = 8) -> int:
    """Draw text with word wrapping. Returns the total height used."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    total_height = 0
    for line in lines:
        draw.text((x, y + total_height), line, font=font, fill=fill)
        bbox = font.getbbox(line)
        line_height = bbox[3] - bbox[1]
        total_height += line_height + line_spacing
    
    return total_height


def add_noise_overlay(img: Image.Image, opacity: int = 8) -> Image.Image:
    """Add subtle noise texture for a premium feel."""
    import random
    noise = Image.new("RGB", img.size)
    pixels = noise.load()
    for y in range(img.height):
        for x in range(img.width):
            v = random.randint(-opacity, opacity)
            pixels[x, y] = (128 + v, 128 + v, 128 + v)
    
    # Blend noise with original
    from PIL import ImageChops
    result = Image.blend(img, noise, 0.05)
    return result


# ─── Slide Generators ────────────────────────────────────────────────

def generate_cover_slide(trends: list[dict], date_str: str) -> Image.Image:
    """Generate the cover slide (Slide 1)."""
    palette = COLOR_PALETTES[0]
    img = create_gradient_image(IMAGE_WIDTH, IMAGE_HEIGHT, palette["bg_start"], palette["bg_end"])
    draw = ImageDraw.Draw(img)
    
    # Decorative elements
    # Draw accent circles
    for i in range(4):
        cx = IMAGE_WIDTH - 180 + i * 50
        cy = 180 - i * 40
        r = 80 + i * 25
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(*palette["accent"], 40),
            width=2
        )
    
    # Draw decorative dots grid
    for row in range(8):
        for col in range(12):
            dx = 60 + col * 90
            dy = IMAGE_HEIGHT - 350 + row * 40
            if dx < IMAGE_WIDTH and dy < IMAGE_HEIGHT:
                dot_alpha = max(10, 40 - row * 5)
                draw.ellipse(
                    [dx - 2, dy - 2, dx + 2, dy + 2],
                    fill=(*palette["accent"][:3], dot_alpha)
                )
    
    # Top bar / badge
    badge_y = 180
    badge_text = ">> DAILY TECH DIGEST <<"
    badge_font = get_font("semibold", 24)
    bbox = badge_font.getbbox(badge_text)
    badge_w = bbox[2] - bbox[0] + 40
    badge_h = bbox[3] - bbox[1] + 24
    badge_x = (IMAGE_WIDTH - badge_w) // 2
    
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=25,
        fill=(*palette["accent"], 60),
        outline=palette["accent"],
        width=2,
    )
    draw.text(
        (badge_x + 20, badge_y + 8),
        badge_text,
        font=badge_font,
        fill=palette["text_primary"],
    )
    
    # Main title
    title_font = get_font("bold", 72)
    title_y = 320
    title = "AI & DevOps"
    draw_text_wrapped(draw, title, title_font, IMAGE_WIDTH - 120, 60, title_y, palette["text_primary"])
    
    title2_font = get_font("bold", 72)
    draw.text((60, title_y + 85), "Trends", font=title2_font, fill=palette["accent"])
    
    # Date
    date_font = get_font("medium", 32)
    draw.text((60, title_y + 190), date_str, font=date_font, fill=palette["text_secondary"])
    
    # Divider line
    div_y = title_y + 260
    draw.line([(60, div_y), (IMAGE_WIDTH - 60, div_y)], fill=(*palette["accent"], 100), width=2)
    
    # Topic previews
    preview_y = div_y + 40
    preview_font = get_font("medium", 28)
    
    for i, trend in enumerate(trends[:4]):
        icon = trend["icon"]
        topic = trend["topic"]
        count = trend["count"]
        
        # Use text marker instead of emoji for icon rendering
        marker = ">>" 
        text = f"{marker}  {topic}"
        count_text = f"{count} articles"
        
        draw.text((80, preview_y), text, font=preview_font, fill=palette["text_primary"])
        
        count_font = get_font("regular", 22)
        count_bbox = count_font.getbbox(count_text)
        count_w = count_bbox[2] - count_bbox[0]
        draw.text(
            (IMAGE_WIDTH - 80 - count_w, preview_y + 4),
            count_text,
            font=count_font,
            fill=palette["text_secondary"]
        )
        
        preview_y += 55
    
    # Bottom branding
    brand_y = IMAGE_HEIGHT - 180
    draw.line([(60, brand_y), (IMAGE_WIDTH - 60, brand_y)], fill=(*palette["accent"], 60), width=1)
    
    brand_font = get_font("bold", 30)
    draw.text((60, brand_y + 25), BRAND_NAME, font=brand_font, fill=palette["accent"])
    
    handle_font = get_font("regular", 24)
    draw.text((60, brand_y + 65), BRAND_HANDLE, font=handle_font, fill=palette["text_secondary"])
    
    tagline_font = get_font("regular", 22)
    draw.text((60, brand_y + 100), BRAND_TAGLINE, font=tagline_font, fill=palette["text_secondary"])
    
    # Swipe indicator
    swipe_font = get_font("semibold", 26)
    swipe_text = "SWIPE >>"
    swipe_bbox = swipe_font.getbbox(swipe_text)
    swipe_w = swipe_bbox[2] - swipe_bbox[0]
    draw.text(
        (IMAGE_WIDTH - 80 - swipe_w, brand_y + 30),
        swipe_text,
        font=swipe_font,
        fill=palette["highlight"]
    )
    
    return img


def generate_trend_slide(trend: dict, slide_index: int, total_slides: int) -> Image.Image:
    """Generate a trend card slide (Slides 2-5) with dynamic content sizing."""
    palette = COLOR_PALETTES[slide_index % len(COLOR_PALETTES)]
    img = create_gradient_image(IMAGE_WIDTH, IMAGE_HEIGHT, palette["bg_start"], palette["bg_end"])
    draw = ImageDraw.Draw(img)
    
    # Decorative elements — large accent circle in background
    circle_r = 300
    draw.ellipse(
        [IMAGE_WIDTH - circle_r - 50, -circle_r + 100,
         IMAGE_WIDTH + circle_r - 50, circle_r + 100],
        outline=(*palette["accent"], 25),
        width=3
    )
    draw.ellipse(
        [-circle_r + 50, IMAGE_HEIGHT - circle_r - 100,
         circle_r + 50, IMAGE_HEIGHT + circle_r - 100],
        outline=(*palette["accent"], 15),
        width=2
    )
    
    # Top section: Progress indicator
    top_y = 60
    progress_font = get_font("medium", 22)
    progress_text = f"TREND {slide_index} OF {total_slides - 1}"
    draw.text((60, top_y), progress_text, font=progress_font, fill=palette["text_secondary"])
    
    # Progress dots
    dots_x = IMAGE_WIDTH - 120
    for i in range(total_slides - 1):
        dot_x = dots_x + i * 22
        dot_color = palette["accent"] if i == slide_index - 1 else (*palette["text_secondary"][:3], 80)
        draw.ellipse([dot_x, top_y + 5, dot_x + 10, top_y + 15], fill=dot_color)
    
    # Topic badge with icon
    badge_y = 130
    icon = trend["icon"]
    topic = trend["topic"]
    badge_font = get_font("semibold", 28)
    badge_text = f">>  {topic.upper()}"
    bbox = badge_font.getbbox(badge_text)
    badge_w = bbox[2] - bbox[0] + 50
    badge_h = bbox[3] - bbox[1] + 28
    
    draw.rounded_rectangle(
        [60, badge_y, 60 + badge_w, badge_y + badge_h],
        radius=badge_h // 2,
        fill=(*palette["accent"], 50),
        outline=palette["accent"],
        width=2,
    )
    draw.text(
        (85, badge_y + 10),
        badge_text,
        font=badge_font,
        fill=palette["text_primary"],
    )
    
    # Large decorative bracket instead of emoji
    icon_font = get_font("bold", 100)
    draw.text(
        (IMAGE_WIDTH - 180, badge_y - 10),
        "{ }", font=icon_font, fill=(*palette["accent"], 80)
    )
    
    # === Dynamic card: measure content first, then size the card ===
    card_x = 40
    card_w = IMAGE_WIDTH - 80
    content_x = card_x + 40
    content_w = card_w - 80
    card_top_y = badge_y + badge_h + 40
    
    # Pre-measure all content heights
    headline_font = get_font("bold", 40)
    insight_font = get_font("regular", 28)
    takeaway_label_font = get_font("semibold", 22)
    takeaway_font = get_font("regular", 24)
    source_font = get_font("medium", 22)
    
    # Measure headline height
    headline_height = _measure_wrapped_height(
        draw, trend["headline"], headline_font, content_w, line_spacing=10
    )
    
    # Measure insight height
    insight_height = _measure_wrapped_height(
        draw, trend["insight"], insight_font, content_w, line_spacing=8
    )
    
    # Measure takeaways height
    takeaways = trend.get("takeaways", [])
    takeaways_total_height = 0
    if takeaways:
        takeaways_total_height += 40  # label + gap
        for t in takeaways:
            th = _measure_wrapped_height(draw, f"• {t}", takeaway_font, content_w - 20, line_spacing=6)
            takeaways_total_height += th + 6  # gap between takeaways
    
    # Measure source line height
    source_height = 30
    
    # Calculate total content height with padding
    content_padding_top = 35
    gap_after_headline = 25  # includes divider
    gap_after_insight = 20
    gap_before_source = 20
    content_padding_bottom = 25
    
    total_content = (
        content_padding_top
        + headline_height
        + gap_after_headline
        + insight_height
        + gap_after_insight
        + takeaways_total_height
        + gap_before_source
        + source_height
        + content_padding_bottom
    )
    
    # Card height: at least 400px, at most fits before branding area
    max_card_h = IMAGE_HEIGHT - card_top_y - 180  # leave room for branding
    card_h = max(400, min(int(total_content), max_card_h))
    
    # Card background
    card_bg = (*palette["bg_end"], 180)
    draw.rounded_rectangle(
        [card_x, card_top_y, card_x + card_w, card_top_y + card_h],
        radius=24,
        fill=card_bg,
        outline=(*palette["accent"], 60),
        width=2,
    )
    
    # === Render content inside card ===
    cursor_y = card_top_y + content_padding_top
    
    # Headline
    headline_h = draw_text_wrapped(
        draw, trend["headline"], headline_font,
        content_w, content_x, cursor_y,
        palette["text_primary"], line_spacing=10
    )
    cursor_y += headline_h + 15
    
    # Accent divider
    draw.line(
        [(content_x, cursor_y), (content_x + 160, cursor_y)],
        fill=palette["accent"],
        width=3
    )
    cursor_y += 15
    
    # Insight text
    insight_h = draw_text_wrapped(
        draw, trend["insight"], insight_font,
        content_w, content_x, cursor_y,
        palette["text_secondary"], line_spacing=8
    )
    cursor_y += insight_h + 15
    
    # Key Takeaways section
    if takeaways:
        # Takeaway label
        draw.text(
            (content_x, cursor_y),
            "KEY TAKEAWAYS",
            font=takeaway_label_font,
            fill=palette["accent"]
        )
        cursor_y += 32
        
        # Render each takeaway bullet
        for takeaway_text in takeaways:
            bullet_text = f"•  {takeaway_text}"
            th = draw_text_wrapped(
                draw, bullet_text, takeaway_font,
                content_w - 20, content_x + 10, cursor_y,
                palette["text_primary"], line_spacing=6
            )
            cursor_y += th + 6
    
    # Source attribution at bottom of card
    source_y = card_top_y + card_h - 55
    source_text = f"Source: {trend['source']}"
    # If multiple sources, show them
    all_sources = trend.get("all_sources", [])
    if len(all_sources) > 1:
        source_text = f"Sources: {', '.join(all_sources[:3])}"
    draw.text(
        (content_x, source_y),
        source_text,
        font=source_font,
        fill=palette["text_secondary"]
    )
    
    # Article count badge
    if trend["count"] > 1:
        count_text = f"{trend['count']} articles"
        count_bbox = source_font.getbbox(count_text)
        count_w = count_bbox[2] - count_bbox[0] + 30
        count_x = card_x + card_w - count_w - 20
        draw.rounded_rectangle(
            [count_x, source_y - 5, count_x + count_w, source_y + 30],
            radius=15,
            fill=(*palette["accent"], 40),
        )
        draw.text(
            (count_x + 15, source_y),
            count_text,
            font=source_font,
            fill=palette["accent"]
        )
    
    # Bottom section: Branding
    brand_y = IMAGE_HEIGHT - 130
    draw.line(
        [(60, brand_y), (IMAGE_WIDTH - 60, brand_y)],
        fill=(*palette["accent"], 40),
        width=1
    )
    
    brand_font = get_font("semibold", 24)
    draw.text((60, brand_y + 20), BRAND_NAME, font=brand_font, fill=palette["accent"])
    
    handle_font = get_font("regular", 20)
    draw.text((60, brand_y + 55), BRAND_HANDLE, font=handle_font, fill=palette["text_secondary"])
    
    # Next slide indicator (except on last slide)
    if slide_index < total_slides - 1:
        next_font = get_font("semibold", 22)
        next_text = "NEXT >>"
        next_bbox = next_font.getbbox(next_text)
        next_w = next_bbox[2] - next_bbox[0]
        draw.text(
            (IMAGE_WIDTH - 80 - next_w, brand_y + 30),
            next_text,
            font=next_font,
            fill=palette["highlight"]
        )
    else:
        # Last slide: Follow CTA
        cta_font = get_font("bold", 24)
        cta_text = "FOLLOW FOR MORE"
        cta_bbox = cta_font.getbbox(cta_text)
        cta_w = cta_bbox[2] - cta_bbox[0]
        draw.text(
            (IMAGE_WIDTH - 80 - cta_w, brand_y + 30),
            cta_text,
            font=cta_font,
            fill=palette["highlight"]
        )
    
    return img


def _measure_wrapped_height(draw: ImageDraw.Draw, text: str,
                             font: ImageFont.FreeTypeFont,
                             max_width: int, line_spacing: int = 8) -> int:
    """Measure the total height that wrapped text would occupy, without drawing."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    total_height = 0
    for line in lines:
        bbox = font.getbbox(line)
        line_height = bbox[3] - bbox[1]
        total_height += line_height + line_spacing
    
    return total_height


# ─── Main Generation Pipeline ────────────────────────────────────────

def generate_carousel(trends: list[dict], verbose: bool = False) -> list[str]:
    """
    Generate all carousel images and save to output directory.
    
    Returns list of file paths to generated images.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if verbose:
        print("  📥 Checking fonts...")
    download_fonts()
    
    date_str = datetime.now().strftime("%B %d, %Y")
    total_slides = min(len(trends) + 1, 6)  # 1 cover + up to 4 trends (max 5 total)
    image_paths = []
    
    # Generate cover slide
    if verbose:
        print(f"  🎨 Generating cover slide...")
    cover = generate_cover_slide(trends, date_str)
    cover_path = os.path.join(OUTPUT_DIR, "slide_1_cover.jpg")
    cover.save(cover_path, "JPEG", quality=95)
    image_paths.append(cover_path)
    if verbose:
        print(f"    ✅ Saved: {cover_path}")
    
    # Generate trend slides
    for i, trend in enumerate(trends[:total_slides - 1], 1):
        if verbose:
            print(f"  🎨 Generating trend slide {i}: {trend['topic']}...")
        
        slide = generate_trend_slide(trend, i, total_slides)
        slide_path = os.path.join(OUTPUT_DIR, f"slide_{i + 1}_{trend['topic'].lower().replace(' ', '_')[:20]}.jpg")
        slide.save(slide_path, "JPEG", quality=95)
        image_paths.append(slide_path)
        
        if verbose:
            print(f"    ✅ Saved: {slide_path}")
    
    if verbose:
        print(f"\n  📸 Generated {len(image_paths)} carousel images in {OUTPUT_DIR}")
    
    return image_paths


if __name__ == "__main__":
    # Quick test: Generate sample carousel with mock data
    mock_trends = [
        {
            "topic": "AI & LLMs",
            "icon": "🤖",
            "count": 8,
            "headline": "OpenAI Releases GPT-5 With Revolutionary Reasoning Capabilities",
            "insight": "The latest model shows unprecedented performance in multi-step reasoning tasks, surpassing human benchmarks in mathematics and coding.",
            "source": "TechCrunch AI",
            "source_count": 3,
            "articles": [],
        },
        {
            "topic": "AI Safety & Ethics",
            "icon": "🛡️",
            "count": 5,
            "headline": "Anthropic Draws Line Against Military AI Applications",
            "insight": "Anthropic refuses to allow its AI in autonomous weapons, potentially costing a major Pentagon contract worth millions.",
            "source": "Wired AI",
            "source_count": 2,
            "articles": [],
        },
        {
            "topic": "Cloud & Containers",
            "icon": "☁️",
            "count": 4,
            "headline": "Kubernetes 1.30 Introduces Breakthrough Auto-Scaling",
            "insight": "New elastic scaling features reduce cloud costs by up to 40% while maintaining performance under variable loads.",
            "source": "The New Stack",
            "source_count": 2,
            "articles": [],
        },
        {
            "topic": "AI Hardware",
            "icon": "🔲",
            "count": 6,
            "headline": "Nvidia's Deal With Meta Signals New Era in Computing Power",
            "insight": "The days of buying discrete chips are over. AI companies now need full system solutions combining GPUs, CPUs, and networking.",
            "source": "Wired AI",
            "source_count": 3,
            "articles": [],
        },
    ]
    
    print("🎨 Generating sample carousel...\n")
    paths = generate_carousel(mock_trends, verbose=True)
    print(f"\n✅ Done! Open the images in: {OUTPUT_DIR}")
