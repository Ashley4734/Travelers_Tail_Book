#!/usr/bin/env python3
"""
Generate book cover for "The Traveler's Key" by Ashley Harris
"""

from PIL import Image, ImageDraw, ImageFont
import math

# Cover dimensions (standard paperback: 6x9 inches at 300 DPI)
WIDTH = 1800
HEIGHT = 2700

# Create new image with dark gradient background
img = Image.new('RGB', (WIDTH, HEIGHT), color='black')
draw = ImageDraw.Draw(img)

# Create a cosmic gradient background (dark blue to purple to black)
for y in range(HEIGHT):
    # Create gradient from top to bottom
    ratio = y / HEIGHT

    if ratio < 0.3:
        # Top: Deep blue
        r = int(10 + (30 - 10) * (ratio / 0.3))
        g = int(15 + (20 - 15) * (ratio / 0.3))
        b = int(50 + (80 - 50) * (ratio / 0.3))
    elif ratio < 0.6:
        # Middle: Purple
        local_ratio = (ratio - 0.3) / 0.3
        r = int(30 + (60 - 30) * local_ratio)
        g = int(20 + (10 - 20) * local_ratio)
        b = int(80 + (90 - 80) * local_ratio)
    else:
        # Bottom: Dark
        local_ratio = (ratio - 0.6) / 0.4
        r = int(60 - 50 * local_ratio)
        g = int(10 - 5 * local_ratio)
        b = int(90 - 80 * local_ratio)

    draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(r, g, b))

# Add starfield effect
import random
random.seed(42)
for _ in range(200):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.choice([1, 1, 1, 2, 2, 3])
    brightness = random.randint(150, 255)
    draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness))

# Draw mystical portal/doorway in center
portal_center_x = WIDTH // 2
portal_center_y = HEIGHT // 2 + 100

# Draw glowing portal rings
for ring in range(8, 0, -1):
    radius = ring * 50
    alpha_val = int(255 * (ring / 8) * 0.3)

    # Create golden glow
    r = min(255, 200 + ring * 5)
    g = min(255, 170 + ring * 3)
    b = 50 + ring * 10

    # Draw filled circle for glow effect
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse(
        [portal_center_x - radius, portal_center_y - radius,
         portal_center_x + radius, portal_center_y + radius],
        fill=(r, g, b, alpha_val)
    )
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

# Draw central portal
portal_radius = 80
draw.ellipse(
    [portal_center_x - portal_radius, portal_center_y - portal_radius,
     portal_center_x + portal_radius, portal_center_y + portal_radius],
    fill=(255, 220, 100)
)

# Draw an open book silhouette in the portal
book_width = 60
book_height = 40
book_left = portal_center_x - book_width // 2
book_top = portal_center_y - book_height // 2

# Left page
draw.polygon([
    (book_left, book_top + 5),
    (portal_center_x - 3, book_top),
    (portal_center_x - 3, book_top + book_height),
    (book_left, book_top + book_height - 5)
], fill=(40, 20, 60))

# Right page
draw.polygon([
    (portal_center_x + 3, book_top),
    (book_left + book_width, book_top + 5),
    (book_left + book_width, book_top + book_height - 5),
    (portal_center_x + 3, book_top + book_height)
], fill=(50, 25, 70))

# Draw mystical symbols around portal
num_symbols = 12
symbol_radius = 180
for i in range(num_symbols):
    angle = (2 * math.pi * i) / num_symbols
    sx = portal_center_x + int(symbol_radius * math.cos(angle))
    sy = portal_center_y + int(symbol_radius * math.sin(angle))

    # Draw small glowing symbols
    symbol_size = 8
    draw.ellipse([sx - symbol_size, sy - symbol_size, sx + symbol_size, sy + symbol_size],
                 fill=(180, 150, 255))

    # Add connecting lines
    inner_x = portal_center_x + int(100 * math.cos(angle))
    inner_y = portal_center_y + int(100 * math.sin(angle))
    draw.line([(inner_x, inner_y), (sx, sy)], fill=(120, 100, 200, 128), width=2)

# Try to load fonts, fall back to default if unavailable
try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 120)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 50)
    author_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 60)
except:
    print("Warning: Could not load TrueType fonts, using default")
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    author_font = ImageFont.load_default()

# Add title text with glow effect
title_text = "THE TRAVELER'S"
title2_text = "KEY"

# Position for title (top area)
title_y = 250

# Draw title with glow
for offset in [(0, 0), (2, 2), (-2, -2), (2, -2), (-2, 2)]:
    # Glow effect
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2 + offset[0]
    draw.text((x, title_y + offset[1]), title_text, font=title_font, fill=(255, 200, 100, 200))

    bbox2 = draw.textbbox((0, 0), title2_text, font=title_font)
    text_width2 = bbox2[2] - bbox2[0]
    x2 = (WIDTH - text_width2) // 2 + offset[0]
    draw.text((x2, title_y + 130 + offset[1]), title2_text, font=title_font, fill=(255, 200, 100, 200))

# Draw main title text
bbox = draw.textbbox((0, 0), title_text, font=title_font)
text_width = bbox[2] - bbox[0]
x = (WIDTH - text_width) // 2
draw.text((x, title_y), title_text, font=title_font, fill=(255, 255, 255))

bbox2 = draw.textbbox((0, 0), title2_text, font=title_font)
text_width2 = bbox2[2] - bbox2[0]
x2 = (WIDTH - text_width2) // 2
draw.text((x2, title_y + 130), title2_text, font=title_font, fill=(255, 255, 255))

# Add author name at bottom
author_text = "ASHLEY HARRIS"
bbox = draw.textbbox((0, 0), author_text, font=author_font)
text_width = bbox[2] - bbox[0]
author_x = (WIDTH - text_width) // 2
author_y = HEIGHT - 300

# Draw author with subtle glow
draw.text((author_x + 2, author_y + 2), author_text, font=author_font, fill=(100, 80, 150))
draw.text((author_x, author_y), author_text, font=author_font, fill=(220, 200, 255))

# Add genre subtitle
genre_text = "A PORTAL FANTASY ADVENTURE"
bbox = draw.textbbox((0, 0), genre_text, font=subtitle_font)
text_width = bbox[2] - bbox[0]
genre_x = (WIDTH - text_width) // 2
genre_y = HEIGHT - 200

draw.text((genre_x, genre_y), genre_text, font=subtitle_font, fill=(180, 160, 200))

# Save the cover
output_file = "The_Travelers_Key_Cover.png"
img.save(output_file, quality=95, dpi=(300, 300))
print(f"Book cover saved as {output_file}")
print(f"Dimensions: {WIDTH}x{HEIGHT} pixels (6x9 inches at 300 DPI)")
