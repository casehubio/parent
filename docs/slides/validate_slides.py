#!/usr/bin/env python3
"""
CaseHub Slidev Validation Script
Checks all exported slides for:
  1. Column alignment  — left/right top-aligned (grid slides only)
  2. Uniform title-to-content gap — within tolerance of median
  3. No content clipping — large amount of content in bottom strip

Usage:
  cd docs/slides
  npx slidev export --format png --output /tmp/slide_pngs presentation.md
  python3 validate_slides.py

Exit code: 0 = all pass, 1 = issues found
"""

import os, sys, glob, re, statistics
from PIL import Image

PNG_DIR       = "/tmp/slide_pngs"
MD_FILE       = os.path.join(os.path.dirname(__file__), "presentation.md")
BOTTOM_STRIP  = 30      # px from bottom — check for content here
OVERFLOW_MIN  = 3000    # dark pixels threshold — 3000+ = multiple full text rows cut off
DARK_THRESH   = 60      # pixel value below which = "dark" (text)
DARK_MIN      = 12      # min dark pixels per row to count as content
DARK_BOLD     = 22      # min dark pixels per row to count as BOLD header
ALIGN_TOL     = 15      # px — max diff between left/right col tops
GAP_TOL       = 65      # px — max deviation from median gap
GAP_MAX       = 400     # px — gaps above this = intentionally centered layout (skip)
# Slides to skip for column-alignment check (parser offset causes wrong metadata)
# Re-evaluate if slide count changes significantly
SKIP_COL_CHECK = {40}        # casehub-devtown User Flow — single col, falsely tagged as grid
SKIP_GAP_CHECK = {47, 48}   # The Flywheel + Build on Platform — center layout, large gap intentional
SLIDE_H       = 1104
SLIDE_W       = 1960
MID_X         = SLIDE_W // 2


# ── Markdown parsing ──────────────────────────────────────────────────────────

def parse_markdown(path):
    """
    Parse presentation.md to get per-slide metadata.
    Correctly handles Slidev format where --- appears as both front-matter
    delimiter and slide separator.
    """
    if not os.path.exists(path):
        return {}

    with open(path) as f:
        lines = f.readlines()

    slides = {}
    slide_num = 0
    i = 0
    current_frontmatter = ""
    current_content = []
    in_frontmatter = False

    def save_slide():
        nonlocal slide_num
        if not current_content and not current_frontmatter:
            return
        slide_num += 1
        fm = current_frontmatter
        body = "\n".join(current_content)
        slides[slide_num] = {
            'is_section': bool(re.search(r'layout:\s*(section|center)', fm)),
            'has_grid':   '<div class="grid grid-cols-2' in body,
        }

    while i < len(lines):
        line = lines[i].rstrip('\n')

        if line == '---':
            if i == 0 or (not in_frontmatter and not current_content):
                # Start of front matter
                in_frontmatter = True
                current_frontmatter = ""
                i += 1
                # Read until closing ---
                while i < len(lines) and lines[i].rstrip('\n') != '---':
                    current_frontmatter += lines[i]
                    i += 1
                in_frontmatter = False
                i += 1  # skip closing ---
                continue
            else:
                # Slide separator — save current slide, start new
                save_slide()
                current_frontmatter = ""
                current_content = []
                i += 1
                # Check if next line starts front matter
                if i < len(lines) and lines[i].rstrip('\n') != '---':
                    # Might be front matter or content
                    # Look ahead for another ---
                    j = i
                    while j < len(lines) and lines[j].rstrip('\n') != '---' and j - i < 20:
                        j += 1
                    if j < len(lines) and lines[j].rstrip('\n') == '---' and j - i <= 8:
                        # It's a front-matter block
                        while i < len(lines) and lines[i].rstrip('\n') != '---':
                            current_frontmatter += lines[i]
                            i += 1
                        i += 1  # skip closing ---
                continue
        else:
            current_content.append(line)
            i += 1

    save_slide()  # last slide
    return slides


# ── Pixel helpers ─────────────────────────────────────────────────────────────

def first_row(pixels, x0, x1, y0=50, y1=None, min_dark=DARK_MIN):
    y1 = y1 or SLIDE_H
    for y in range(y0, y1):
        if sum(1 for x in range(x0, x1) if pixels[x, y][0] < DARK_THRESH) >= min_dark:
            return y
    return None


def last_row(pixels, x0, x1, y0=50, y1=None, min_dark=DARK_MIN):
    y1 = y1 or SLIDE_H
    result = None
    for y in range(y0, y1):
        if sum(1 for x in range(x0, x1) if pixels[x, y][0] < DARK_THRESH) >= min_dark:
            result = y
    return result


def overflow_px(pixels):
    """Count dark pixels in bottom strip. High counts = content pushed off slide."""
    return sum(
        1
        for y in range(SLIDE_H - BOTTOM_STRIP, SLIDE_H)
        for x in range(80, SLIDE_W - 80)
        if pixels[x, y][0] < DARK_THRESH
    )


def measure_gap(pixels):
    """
    Gap from end of title/subtitle to start of first body bold content.
    Returns (subtitle_bottom, content_top, gap) or (None, None, None).
    """
    subtitle_bot = last_row(pixels, 50, SLIDE_W - 50, y0=50, y1=320, min_dark=3)
    if subtitle_bot is None:
        return None, None, None
    content_top = first_row(pixels, 50, SLIDE_W - 50,
                            y0=subtitle_bot + 15, min_dark=DARK_BOLD)
    if content_top is None:
        return subtitle_bot, None, None
    return subtitle_bot, content_top, content_top - subtitle_bot


def col_alignment(pixels):
    """First BOLD content in left vs right column."""
    left_y  = first_row(pixels, 50, MID_X - 60, y0=220, min_dark=DARK_BOLD)
    right_y = first_row(pixels, MID_X + 60, SLIDE_W - 50, y0=220, min_dark=DARK_BOLD)
    if left_y is None or right_y is None:
        return None, None, None
    return left_y, right_y, abs(left_y - right_y)


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    md_info = parse_markdown(MD_FILE)

    files = sorted(
        glob.glob(f"{PNG_DIR}/*.png"),
        key=lambda f: int(os.path.basename(f).replace('.png', ''))
    )
    if not files:
        print(f"ERROR: no PNGs in {PNG_DIR}")
        print("Run: npx slidev export --format png --output /tmp/slide_pngs presentation.md")
        sys.exit(1)

    print(f"Validating {len(files)} slides  ({len(md_info)} parsed from markdown)\n")

    # Collect measurements
    rows = []
    for path in files:
        n   = int(os.path.basename(path).replace('.png', ''))
        img = Image.open(path).convert('RGB')
        px  = img.load()
        meta = md_info.get(n, {})

        sub_y, con_y, gap        = measure_gap(px)
        left_y, right_y, col_dif = col_alignment(px) if meta.get('has_grid') else (None, None, None)

        rows.append({
            'n':          n,
            'is_section': meta.get('is_section', False),
            'has_grid':   meta.get('has_grid', False),
            'overflow':   overflow_px(px),
            'sub_y':      sub_y, 'con_y': con_y, 'gap': gap,
            'left_y':     left_y, 'right_y': right_y, 'col_dif': col_dif,
        })

    # Median gap — content slides only
    valid_gaps = [
        r['gap'] for r in rows
        if r['gap'] is not None and not r['is_section'] and 20 < r['gap'] < 400
    ]
    med = statistics.median(valid_gaps) if valid_gaps else 120
    print(f"Median title→content gap: {med:.0f}px  (tolerance ±{GAP_TOL}px)  "
          f"(n={len(valid_gaps)} slides)\n")

    issues = []
    print(f"{'#':>3}  {'Overflow':>9}  {'ColAlign':>11}  {'Gap':>6}  Result")
    print("─" * 68)

    for r in rows:
        n    = r['n']
        flags = []

        # 1. Overflow
        if r['overflow'] > OVERFLOW_MIN:
            ovf = f"⚠{r['overflow']:>7}"
            flags.append(f"CLIPPED ({r['overflow']} dark px in bottom {BOTTOM_STRIP}px)")
        else:
            ovf = f"  {'ok':>7}"

        # 2. Column alignment (grid slides only, skip known false-positive offsets)
        if r['has_grid'] and n not in SKIP_COL_CHECK:
            if r['col_dif'] is None:
                col = "   no data "
            elif r['col_dif'] > ALIGN_TOL:
                col = f"  ⚠Δ{r['col_dif']:>4}px "
                flags.append(f"MISALIGNED L={r['left_y']} R={r['right_y']} Δ={r['col_dif']}px")
            else:
                col = f"  ok Δ{r['col_dif']:>2}px "
        elif r['is_section']:
            col = "   section  "
        else:
            col = "   single   "

        # 3. Gap (skip section slides and slides without body)
        if r['is_section'] or r['gap'] is None or r['gap'] <= 20 or n in SKIP_GAP_CHECK:
            gap = "     —"
        elif r['gap'] > GAP_MAX:
            gap = f"  {r['gap']:>4}"  # very large gap = intentional centering, skip
        else:
            dev = abs(r['gap'] - med)
            gap = f"  {r['gap']:>4}" if dev <= GAP_TOL else f"⚠{r['gap']:>4}"
            if dev > GAP_TOL:
                flags.append(f"GAP {r['gap']}px (median={med:.0f}, Δ={dev:.0f}px)")

        status = "✓" if not flags else "⚠  " + " | ".join(flags)
        print(f"{n:>3}  {ovf}  {col}  {gap}  {status}")
        if flags:
            issues.append({'n': n, **r, 'flags': flags})

    print(f"\n{'═'*68}")
    if not issues:
        print("✓  ALL SLIDES PASS")
    else:
        print(f"⚠  {len(issues)} slides need attention:\n")
        for i in issues:
            tag = "[GRID]" if i['has_grid'] else "[SECTION]" if i['is_section'] else "[SINGLE]"
            print(f"  Slide {i['n']:>2} {tag}: " + " | ".join(i['flags']))

    return len(issues) > 0


if __name__ == '__main__':
    sys.exit(1 if run() else 0)
