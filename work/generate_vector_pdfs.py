#!/usr/bin/env python3
"""Convert annotated waveform SVGs directly to high-fidelity vector PDFs via rsvg-convert.

Renders raw oscilloscope background photos and vector annotations natively
using rsvg-convert. Also generates the 15-waveform contact sheet PDF.
The SVG files in report/fig_work_A/svg/ are the single source of truth (SSOT).
"""

import base64
import html
from pathlib import Path
import re
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = PROJECT_ROOT / "report" / "fig_work_A"
SVG_DIR = FIG_DIR / "svg"
RAW_DIR = FIG_DIR / "raw"
CONTACT_DIR = FIG_DIR / "contact_sheets"
RSVG_BIN = Path("/opt/homebrew/bin/rsvg-convert")


def render_svg_to_pdf(svg_path: Path, out_pdf_path: Path) -> bool:
    if not svg_path.exists():
        print(f"Skipping {svg_path.name}: file not found")
        return False

    svg_text = svg_path.read_text(encoding="utf-8")
    stem = svg_path.stem
    raw_path = RAW_DIR / f"{stem}.JPG"
    if raw_path.exists():
        b64_data = base64.b64encode(raw_path.read_bytes()).decode("ascii")
        svg_text = svg_text.replace(f"../raw/{stem}.JPG", f"data:image/jpeg;base64,{b64_data}")

    cmd = [str(RSVG_BIN), "-f", "pdf", "-o", str(out_pdf_path), "-"]
    res = subprocess.run(cmd, input=svg_text.encode("utf-8"), capture_output=True)

    if res.returncode != 0:
        print(f"Error rendering {svg_path.name}: {res.stderr.decode('utf-8')}")
        return False

    size_kb = out_pdf_path.stat().st_size / 1024
    print(f"Rendered: {out_pdf_path.name} ({size_kb:.1f} KB)")
    return True


def generate_contact_sheet_pdf() -> Path:
    html_text = (CONTACT_DIR / "contact_sheet.html").read_text(encoding="utf-8")
    card_pattern = re.compile(
        r'<div class="card">\s*<div class="card-header">(.*?)</div>\s*<div class="card-body">\s*<object data="\.\./svg/(.*?)\.svg"',
        re.DOTALL,
    )
    tiles = card_pattern.findall(html_text)

    sum_match = re.search(
        r'<div class="card-header">(15 \| .*?)</div>\s*<div class="card-body card-summary-body"[^>]*>(.*?)</div>',
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

    cols, rows = 3, 5
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
        raw_path = RAW_DIR / f"{name}.JPG"
        if raw_path.exists():
            raw_b64 = base64.b64encode(raw_path.read_bytes()).decode("ascii")
            svg_text = svg_text.replace(f"../raw/{name}.JPG", f"data:image/jpeg;base64,{raw_b64}")

        p = subprocess.run(
            [str(RSVG_BIN), "-f", "png", "-w", str(tile_w), "-h", str(wave_h), "-"],
            input=svg_text.encode("utf-8"),
            capture_output=True,
        )
        if p.returncode != 0:
            raise RuntimeError(f"Failed to render {name}: {p.stderr.decode()}")
        b64_png = base64.b64encode(p.stdout).decode("ascii")
        escaped_title = html.escape(title)

        svg_parts.append(f"""  <g transform="translate({x}, {y})">
    <rect width="{tile_w}" height="{tile_h}" rx="8" ry="8" fill="#161b22" stroke="#30363d" stroke-width="1.5" />
    <path d="M 0 8 Q 0 0 8 0 L {tile_w-8} 0 Q {tile_w} 0 {tile_w} 8 L {tile_w} {hdr_h} L 0 {hdr_h} Z" fill="#21262d" />
    <rect x="0" y="0" width="5" height="{hdr_h}" fill="#58a6ff" />
    <text x="16" y="28" fill="#f0f6fc" font-family="sans-serif" font-size="18" font-weight="bold">{escaped_title}</text>
    <image href="data:image/png;base64,{b64_png}" x="0" y="{hdr_h}" width="{tile_w}" height="{wave_h}" />
  </g>""")

    # 15th tile: summary
    x15 = pad_x + 2 * (tile_w + gap_x)
    y15 = pad_y + 4 * (tile_h + gap_y)
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
    svg_parts.append(f"""  <g transform="translate({x15}, {y15})">
    <rect width="{tile_w}" height="{tile_h}" rx="8" ry="8" fill="#0d1117" stroke="#30363d" stroke-width="1.5" />
    <path d="M 0 8 Q 0 0 8 0 L {tile_w-8} 0 Q {tile_w} 0 {tile_w} 8 L {tile_w} {hdr_h} L 0 {hdr_h} Z" fill="#21262d" />
    <rect x="0" y="0" width="5" height="{hdr_h}" fill="#58a6ff" />
    <text x="16" y="28" fill="#f0f6fc" font-family="sans-serif" font-size="18" font-weight="bold">{escaped_sum_title}</text>
    {sum_text_block}
  </g>""")

    svg_parts.append("</svg>")
    out_pdf = CONTACT_DIR / "sheet_all_15waveforms_annotated.pdf"
    p = subprocess.run(
        [str(RSVG_BIN), "-f", "pdf", "-o", str(out_pdf), "-"],
        input="\n".join(svg_parts).encode("utf-8"),
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"rsvg-convert failed: {p.stderr.decode()}")

    size_kb = out_pdf.stat().st_size / 1024
    print(f"Generated contact sheet: {out_pdf.name} ({size_kb:.1f} KB)")
    return out_pdf


def main() -> None:
    print(f"Using {RSVG_BIN} for native SVG->PDF vector rendering...")
    svg_files = sorted(SVG_DIR.glob("*.svg"))
    success_count = 0

    for svg_file in svg_files:
        out_pdf = FIG_DIR / f"{svg_file.stem}.pdf"
        if render_svg_to_pdf(svg_file, out_pdf):
            success_count += 1

    print(f"Successfully rendered {success_count}/{len(svg_files)} individual PDFs.")
    generate_contact_sheet_pdf()


if __name__ == "__main__":
    main()
