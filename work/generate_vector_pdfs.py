#!/usr/bin/env python3
"""Generate lightweight, high-fidelity waveform images and contact sheet (JPEG).

- Single Source of Truth (SSOT): SVG files in report/fig_work_A/svg/
- Individual waveforms: rendered directly to crisp ~100KB JPEGs via rsvg-convert & Pillow.
- Contact sheet: rendered to a high-resolution JPEG (~1.3MB, well below 100MB constraint).
"""

import base64
import html
import io
from pathlib import Path
import re
import subprocess
import sys

# Load venv site-packages if available
venv_site = Path(__file__).resolve().parents[0] / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site.exists():
    sys.path.insert(0, str(venv_site))

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = PROJECT_ROOT / "report" / "fig_work_A"
SVG_DIR = FIG_DIR / "svg"
RAW_DIR = FIG_DIR / "raw"
CONTACT_DIR = FIG_DIR / "contact_sheets"
RSVG_BIN = Path("/opt/homebrew/bin/rsvg-convert")


def render_individual_waveform(svg_path: Path, target_width: int = 1200, quality: int = 78) -> None:
    stem = svg_path.stem
    raw_path = RAW_DIR / f"{stem}.JPG"
    svg_text = svg_path.read_text(encoding="utf-8")
    if raw_path.exists():
        raw_b64 = base64.b64encode(raw_path.read_bytes()).decode("ascii")
        svg_text = svg_text.replace(f"../raw/{stem}.JPG", f"data:image/jpeg;base64,{raw_b64}")

    p = subprocess.run(
        [str(RSVG_BIN), "-u", "-f", "png", "-w", str(target_width), "-"],
        input=svg_text.encode("utf-8"),
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Failed to render {stem}: {p.stderr.decode('utf-8')}")

    img = Image.open(io.BytesIO(p.stdout)).convert("RGB")

    # Save ~100KB JPEG
    out_jpg = FIG_DIR / f"{stem}.jpg"
    img.save(out_jpg, format="JPEG", quality=quality, optimize=True)
    print(f"Rendered {stem}: JPG {out_jpg.stat().st_size / 1024:.1f} KB")


def generate_contact_sheet() -> None:
    html_text = (CONTACT_DIR / "contact_sheet.html").read_text(encoding="utf-8")
    card_pattern = re.compile(
        r'<div class="card">\s*<div class="card-header">(.*?)</div>\s*<div class="card-body">\s*<object data="\.\./svg/(.*?)\.svg"',
        re.DOTALL,
    )
    tiles = card_pattern.findall(html_text)

    sum_match = re.search(
        r'<div class="card-header">(12 \| .*?)</div>\s*<div class="card-body card-summary-body"[^>]*>(.*?)</div>',
        html_text,
        re.DOTALL,
    )
    sum_title = sum_match.group(1).strip()
    sum_body = (
        sum_match.group(2)
        .strip()
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )

    cols, rows = 3, 4
    tile_w = 960
    wave_h = round(tile_w * 2560 / 3820)
    hdr_h = 44
    tile_h = hdr_h + wave_h
    gap_x, gap_y = 24, 28
    pad_x, pad_y = 32, 36

    total_w = pad_x * 2 + tile_w * cols + gap_x * (cols - 1)
    total_h = pad_y * 2 + tile_h * rows + gap_y * (rows - 1)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}">',
        f'<rect width="{total_w}" height="{total_h}" fill="#0d1117" />',
    ]

    for idx, (title, name) in enumerate(tiles):
        r, c = divmod(idx, cols)
        x = pad_x + c * (tile_w + gap_x)
        y = pad_y + r * (tile_h + gap_y)

        svg_text = (SVG_DIR / f"{name}.svg").read_text(encoding="utf-8")
        jpg_path = FIG_DIR / f"{name}.jpg"
        if jpg_path.exists():
            jpg_b64 = base64.b64encode(jpg_path.read_bytes()).decode("ascii")
            svg_text = svg_text.replace(f"../raw/{name}.JPG", f"data:image/jpeg;base64,{jpg_b64}")

        vb_m = re.search(r'viewBox="([^"]*)"', svg_text)
        vb = vb_m.group(1) if vb_m else "80 120 3820 2560"

        inner_svg = re.sub(r"^\s*<svg[^>]*>", "", svg_text, flags=re.DOTALL)
        inner_svg = re.sub(r"</svg>\s*$", "", inner_svg, flags=re.DOTALL)

        prefix = f"t{idx}_"
        ids = re.findall(r'id="([^"]+)"', inner_svg)
        for i_val in set(ids):
            inner_svg = inner_svg.replace(f'id="{i_val}"', f'id="{prefix}{i_val}"')
            inner_svg = inner_svg.replace(f'url(#{i_val})', f'url(#{prefix}{i_val})')
            inner_svg = inner_svg.replace(f'href="#{i_val}"', f'href="#{prefix}{i_val}"')

        escaped_title = html.escape(title)

        svg_parts.append(f"""  <g transform="translate({x}, {y})">
    <rect width="{tile_w}" height="{tile_h}" rx="8" ry="8" fill="#161b22" stroke="#30363d" stroke-width="1.5" />
    <path d="M 0 8 Q 0 0 8 0 L {tile_w-8} 0 Q {tile_w} 0 {tile_w} 8 L {tile_w} {hdr_h} L 0 {hdr_h} Z" fill="#21262d" />
    <rect x="0" y="0" width="5" height="{hdr_h}" fill="#58a6ff" />
    <text x="16" y="28" fill="#f0f6fc" font-family="sans-serif" font-size="18" font-weight="bold">{escaped_title}</text>
    <svg x="0" y="{hdr_h}" width="{tile_w}" height="{wave_h}" viewBox="{vb}">
      {inner_svg}
    </svg>
    <rect width="{tile_w}" height="{tile_h}" rx="8" ry="8" fill="none" stroke="#30363d" stroke-width="1.5" />
  </g>""")

    # 12th tile: summary
    r, c = divmod(11, cols)
    x12 = pad_x + c * (tile_w + gap_x)
    y12 = pad_y + r * (tile_h + gap_y)
    escaped_sum_title = html.escape(sum_title)

    lines = sum_body.split("\n")
    tspan_lines = []
    text_y = 74
    for l in lines:
        escaped_l = html.escape(l)
        tspan_lines.append(
            f'<text x="20" y="{text_y}" fill="#c9d1d9" font-family="monospace" font-size="16" xml:space="preserve">{escaped_l}</text>'
        )
        text_y += 26

    sum_text_block = "\n    ".join(tspan_lines)
    svg_parts.append(f"""  <g transform="translate({x12}, {y12})">
    <rect width="{tile_w}" height="{tile_h}" rx="8" ry="8" fill="#0d1117" stroke="#30363d" stroke-width="1.5" />
    <path d="M 0 8 Q 0 0 8 0 L {tile_w-8} 0 Q {tile_w} 0 {tile_w} 8 L {tile_w} {hdr_h} L 0 {hdr_h} Z" fill="#21262d" />
    <rect x="0" y="0" width="5" height="{hdr_h}" fill="#58a6ff" />
    <text x="16" y="28" fill="#f0f6fc" font-family="sans-serif" font-size="18" font-weight="bold">{escaped_sum_title}</text>
    {sum_text_block}
    <rect width="{tile_w}" height="{tile_h}" rx="8" ry="8" fill="none" stroke="#30363d" stroke-width="1.5" />
  </g>""")

    svg_parts.append("</svg>")
    full_svg_text = "\n".join(svg_parts)

    p = subprocess.run(
        [str(RSVG_BIN), "-u", "-f", "png", "-w", str(total_w), "-"],
        input=full_svg_text.encode("utf-8"),
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"rsvg-convert failed: {p.stderr.decode()}")

    img = Image.open(io.BytesIO(p.stdout)).convert("RGB")

    # Save high-resolution JPEG (~1.3MB, well below 100MB constraint)
    out_jpg = CONTACT_DIR / "sheet_all_15waveforms_annotated.jpg"
    img.save(out_jpg, format="JPEG", quality=88, optimize=True)

    print(f"Generated Contact Sheet: JPG {out_jpg.stat().st_size / 1024 / 1024:.2f} MB")


def main() -> None:
    print("Generating ~100KB JPEGs for individual waveforms...")
    svg_files = sorted(SVG_DIR.glob("*.svg"))
    for svg_file in svg_files:
        render_individual_waveform(svg_file, target_width=1200, quality=78)

    print("\nGenerating contact sheet (JPEG)...")
    generate_contact_sheet()
    print("\nDone!")


if __name__ == "__main__":
    main()
