#!/usr/bin/env python3
"""Generate pixel-accurate SVG annotations aligned to actual waveform peaks and edges."""

from pathlib import Path

SVG_DIR = Path("/Users/ishpctrin/uni/aw/agilework/report/fig_work_A/svg")

# Template for SVG
SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="100%" height="100%">
  <defs>
    <marker id="arrow-cyan" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#00E5FF"/>
    </marker>
    <marker id="arrow-orange" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#FF9100"/>
    </marker>
  </defs>
  <image href="../raw/{raw_file}" width="4000" height="3000"/>
  <g id="annotations">
{annotations}
  </g>
</svg>
"""

def make_cursor_v(x, y1=380.0, y2=2250.0):
    return f'    <line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8"/>'

def make_cursor_h(y, x1=500.0, x2=3450.0):
    return f'    <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8"/>'

def make_arrow_h(x1, x2, y, val_text, color="#00E5FF"):
    mid_x = (x1 + x2) / 2.0
    w = 136 if len(val_text) <= 3 else 172
    tx = mid_x - w / 2.0
    ty = y - 70.0
    lines = [
        f'    <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="5" marker-start="url(#arrow-cyan)" marker-end="url(#arrow-cyan)"/>',
        f'    <g transform="translate({tx:.1f}, {ty:.1f})">',
        f'      <rect width="{w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="{color}" stroke-width="2"/>',
        f'      <text x="{w/2:.1f}" y="44.0" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold" text-anchor="middle">{val_text}</text>',
        f'    </g>'
    ]
    return "\n".join(lines)

def make_arrow_v(y1, y2, x, val_text, color="#FF9100"):
    mid_y = (y1 + y2) / 2.0
    w = 136 if len(val_text) <= 3 else 172
    tx = x + 35.0
    ty = mid_y - 30.0
    lines = [
        f'    <line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="5" marker-start="url(#arrow-orange)" marker-end="url(#arrow-orange)"/>',
        f'    <g transform="translate({tx:.1f}, {ty:.1f})">',
        f'      <rect width="{w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="{color}" stroke-width="2"/>',
        f'      <text x="{w/2:.1f}" y="44.0" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold" text-anchor="middle">{val_text}</text>',
        f'    </g>'
    ]
    return "\n".join(lines)

DEFINITIONS = {
    "緑": {
        "raw": "緑.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1877.0), make_cursor_v(2637.0),
            make_arrow_h(1877.0, 2637.0, 750.0, "2.0"),
            make_cursor_h(489.0), make_cursor_h(2195.0),
            make_arrow_v(2195.0, 489.0, 2950.0, "7.0"),
        ]
    },
    "赤": {
        "raw": "赤.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1943.0), make_cursor_v(2685.0),
            make_arrow_h(1943.0, 2685.0, 800.0, "2.5"),
            make_cursor_h(1095.0), make_cursor_h(1535.0),
            make_arrow_v(1535.0, 1095.0, 2910.0, "2.0"),
        ]
    },
    "赤高": {
        "raw": "赤高.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1497.0), make_cursor_v(2279.0),
            make_arrow_h(1497.0, 2279.0, 880.0, "2.5"),
            make_cursor_h(1201.0), make_cursor_h(1470.0),
            make_arrow_v(1470.0, 1201.0, 2576.0, "1.2"),
        ]
    },
    "赤高々": {
        "raw": "赤高々.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1328.0), make_cursor_v(2061.0),
            make_arrow_h(1328.0, 2061.0, 850.0, "2.5"),
        ]
    },
    "赤位相差": {
        "raw": "赤位相差.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1698.0, y1=450.0, y2=2200.0),
            make_cursor_v(1745.0, y1=450.0, y2=2200.0),
            make_arrow_h(1698.0, 1745.0, 1300.0, "0.15"),
        ]
    },
    "青": {
        "raw": "青.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1804.0), make_cursor_v(2601.0),
            make_arrow_h(1804.0, 2601.0, 767.0, "2.5"),
            make_cursor_h(903.0), make_cursor_h(1811.0),
            make_arrow_v(1811.0, 903.0, 2837.0, "4.0"),
        ]
    },
    "青高": {
        "raw": "青高.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(935.0), make_cursor_v(2018.0),
            make_arrow_h(935.0, 2018.0, 747.0, "3.6"),
            make_cursor_h(1113.0), make_cursor_h(1514.0),
            make_arrow_v(1514.0, 1113.0, 2899.0, "1.7"),
        ]
    },
    "青高々": {
        "raw": "青高々.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1422.0), make_cursor_v(2584.0),
            make_arrow_h(1422.0, 2584.0, 835.0, "3.6"),
            make_cursor_h(1261.0), make_cursor_h(1465.0),
            make_arrow_v(1465.0, 1261.0, 2906.0, "0.85"),
        ]
    },
    "青高々2": {
        "raw": "青高々2.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1454.0), make_cursor_v(2610.0),
            make_arrow_h(1454.0, 2610.0, 835.0, "3.6"),
        ]
    },
    "青位相差": {
        "raw": "青位相差.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1554.0, y1=450.0, y2=2200.0),
            make_cursor_v(1602.0, y1=450.0, y2=2200.0),
            make_arrow_h(1554.0, 1602.0, 1310.0, "0.15"),
        ]
    },
    "紫": {
        "raw": "紫.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1720.0), make_cursor_v(2859.0),
            make_arrow_h(1720.0, 2859.0, 728.0, "3.7"),
            make_cursor_v(1720.0, y1=900.0, y2=1900.0),
            make_cursor_v(1799.0, y1=900.0, y2=1900.0),
            make_arrow_h(1720.0, 1799.0, 1150.0, "0.2"),
            make_cursor_h(753.0), make_cursor_h(1781.0),
            make_arrow_v(1781.0, 753.0, 2880.0, "3.2"),
        ]
    },
    "紫高": {
        "raw": "紫高.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1920.0), make_cursor_v(2079.0),
            make_arrow_h(1920.0, 2079.0, 993.0, "0.5"),
        ]
    },
    "紫高々": {
        "raw": "紫高々.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1824.0), make_cursor_v(2148.0),
            make_arrow_h(1824.0, 2148.0, 1080.0, "1.0"),
        ]
    },
    "脈拍": {
        "raw": "脈拍.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1632.0), make_cursor_v(2378.0),
            make_arrow_h(1632.0, 2378.0, 760.0, "2.4"),
            make_cursor_v(2378.0), make_cursor_v(3080.0),
            make_arrow_h(2378.0, 3080.0, 760.0, "2.3"),
            make_cursor_v(1766.0, y1=950.0, y2=1900.0),
            make_cursor_v(1830.0, y1=950.0, y2=1900.0),
            make_arrow_h(1766.0, 1830.0, 1150.0, "0.2"),
            make_cursor_h(809.0), make_cursor_h(1460.0),
            make_arrow_v(1460.0, 809.0, 2920.0, "2.1"),
        ]
    },
}

for name, d in DEFINITIONS.items():
    svg_content = SVG_TEMPLATE.format(
        viewBox=d["viewBox"],
        raw_file=d["raw"],
        annotations="\n".join(d["elements"])
    )
    svg_path = SVG_DIR / f"{name}.svg"
    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Generated pixel-accurate SVG: {svg_path.name}")

print("All SVGs updated successfully!")
