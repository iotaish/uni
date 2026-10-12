#!/usr/bin/env python3
"""Generate pixel-accurate SVG annotations aligned to actual waveform peaks and edges.

Grid bounds in oscilloscope photos (TBS1000C, 4000x3000px):
- Horizontal grid: X in [480, 3180] (10 div, ~270.0 px/div)
- Vertical grid: Y in [360, 2090] (8 div, ~216.3 px/div)
All cursor dashed lines are strictly trimmed inside this grid to avoid overlapping
the top status bar or the bottom scale indicators / timestamp.
"""

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

# Default limits strictly confined within the oscilloscope grid
GRID_X_MIN = 480.0
GRID_X_MAX = 3180.0
GRID_Y_MIN = 360.0
GRID_Y_MAX = 2090.0

def make_cursor_v(x, y1=GRID_Y_MIN, y2=GRID_Y_MAX):
    """Vertical white dashed cursor line."""
    return f'    <line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8"/>'

def make_cursor_h(y, x1=GRID_X_MIN, x2=GRID_X_MAX):
    """Horizontal white dashed cursor line."""
    return f'    <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8"/>'

def make_arrow_h(x1, x2, y, val_text, color="#00E5FF", text_above=True):
    """Horizontal dimension arrow (cyan) with value badge."""
    mid_x = (x1 + x2) / 2.0
    w = 136 if len(val_text) <= 3 else 172
    tx = mid_x - w / 2.0
    ty = (y - 70.0) if text_above else (y + 16.0)
    lines = [
        f'    <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="5" marker-start="url(#arrow-cyan)" marker-end="url(#arrow-cyan)"/>',
        f'    <g transform="translate({tx:.1f}, {ty:.1f})">',
        f'      <rect width="{w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="{color}" stroke-width="2"/>',
        f'      <text x="{w/2:.1f}" y="44.0" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold" text-anchor="middle">{val_text}</text>',
        f'    </g>'
    ]
    return "\n".join(lines)

def make_arrow_v(y1, y2, x, val_text, color="#FF9100", text_right=True):
    """Vertical dimension arrow (orange) with value badge."""
    mid_y = (y1 + y2) / 2.0
    w = 136 if len(val_text) <= 3 else 172
    tx = (x + 35.0) if text_right else (x - w - 35.0)
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
    # 01 | 波形1 (1Hz正弦波): 周期 2.0 div, 振幅 7.0 div (200ms/div, 100mV/div)
    "緑": {
        "raw": "緑.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 周期 2.0 (CH2 水色ピーク間: X=1877, 2637)
            make_cursor_v(1877.0), make_cursor_v(2637.0),
            make_arrow_h(1877.0, 2637.0, 680.0, "2.0"),
            # 振幅 7.0 (CH2 水色 p-p: Y=515 山頂, Y=2047 谷底)
            make_cursor_h(515.0), make_cursor_h(2047.0),
            make_arrow_v(2047.0, 515.0, 2920.0, "7.0"),
        ]
    },
    # 02 | 波形2 (1Hz+100Hz): 周期 2.5 div, 振幅 2.0 div (200ms/div, 500mV/div)
    "赤": {
        "raw": "赤.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 周期 2.5 (CH2 低周波周期: X=1943, 2685)
            make_cursor_v(1943.0), make_cursor_v(2685.0),
            make_arrow_h(1943.0, 2685.0, 800.0, "2.5"),
            # 振幅 2.0 (CH2 出力 p-p: Y=1095 山頂, Y=1535 谷底)
            make_cursor_h(1095.0), make_cursor_h(1535.0),
            make_arrow_v(1535.0, 1095.0, 2900.0, "2.0"),
        ]
    },
    # 03 | 波形2 高周波観測 (40.0ms/div)
    "赤高": {
        "raw": "赤高.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 中間拡大観測 (波形の連続性を示すカーソル)
            make_cursor_v(1497.0), make_cursor_v(2279.0),
            make_arrow_h(1497.0, 2279.0, 880.0, "2.5"),
        ]
    },
    # 04 | 波形2 高周波拡大 (4.00ms/div): 周期 2.5 div (100Hz成分), 振幅 1.2 div (CH1高周波ノイズ)
    "赤高々": {
        "raw": "赤高々.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 周期 2.5 (100Hz 1周期 = 10ms = 2.5div at 4ms/div)
            make_cursor_v(1328.0), make_cursor_v(2061.0),
            make_arrow_h(1328.0, 2061.0, 850.0, "2.5"),
            # 振幅 1.2 (CH1 入力高周波ノイズ p-p = 1.2div)
            make_cursor_h(1201.0), make_cursor_h(1470.0),
            make_arrow_v(1470.0, 1201.0, 2580.0, "1.2"),
        ]
    },
    # 05 | 波形2 過渡期立ち上がりエッジ観測 (40.0ms/div -> 400µs/div): 時間差 0.15 div
    "赤位相差": {
        "raw": "赤位相差.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1698.0, y1=800.0, y2=1850.0),
            make_cursor_v(1745.0, y1=800.0, y2=1850.0),
            make_arrow_h(1698.0, 1745.0, 1260.0, "0.15"),
        ]
    },
    # 06 | 波形3 (1Hz+7Hz): 周期 2.5 div, 振幅 4.0 div (200ms/div, 200mV/div)
    "青": {
        "raw": "青.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 周期 2.5 (X=1804, 2601)
            make_cursor_v(1804.0), make_cursor_v(2601.0),
            make_arrow_h(1804.0, 2601.0, 750.0, "2.5"),
            # 振幅 4.0 (Y=903 山頂, Y=1811 谷底)
            make_cursor_h(903.0), make_cursor_h(1811.0),
            make_arrow_v(1811.0, 903.0, 2850.0, "4.0"),
        ]
    },
    # 07 | 波形3 高周波観測 (100ms/div)
    "青高": {
        "raw": "青高.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1480.0), make_cursor_v(2450.0),
            make_arrow_h(1480.0, 2450.0, 750.0, "3.6"),
        ]
    },
    # 08 | 波形3 高周波拡大 (40.0ms/div): 周期 3.6 div (7Hz成分), CH2振幅 0.85 div
    "青高々": {
        "raw": "青高々.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 周期 3.6 (7Hz 1周期 = 143ms ≈ 3.58div at 40ms/div)
            make_cursor_v(1422.0), make_cursor_v(2584.0),
            make_arrow_h(1422.0, 2584.0, 835.0, "3.6"),
            # 振幅 0.85 (CH2 7Hz成分 p-p = 0.85div)
            make_cursor_h(1261.0), make_cursor_h(1465.0),
            make_arrow_v(1465.0, 1261.0, 2880.0, "0.85"),
        ]
    },
    # 09 | 波形3 高周波拡大・別テイク (40.0ms/div): 周期 3.6 div
    "青高々2": {
        "raw": "青高々2.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1454.0), make_cursor_v(2610.0),
            make_arrow_h(1454.0, 2610.0, 835.0, "3.6"),
        ]
    },
    # 10 | 波形3 過渡期立ち上がりエッジ観測 (200ms/div -> 400µs/div): 時間差 0.15 div
    "青位相差": {
        "raw": "青位相差.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1554.0, y1=800.0, y2=1850.0),
            make_cursor_v(1602.0, y1=800.0, y2=1850.0),
            make_arrow_h(1554.0, 1602.0, 1260.0, "0.15"),
        ]
    },
    # 11 | 波形4 模擬脈波 (200ms/div): 周期 3.7 div, 時間差 0.2 div, 振幅 3.2 div
    "紫": {
        "raw": "紫.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 周期 3.7 (主収縮期ピーク間: X=1720, 2859) - 上部に配置
            make_cursor_v(1720.0), make_cursor_v(2859.0),
            make_arrow_h(1720.0, 2859.0, 620.0, "3.7"),
            # 時間差 0.2 (CH1とCH2のピーク間差) - 下側(Y=1450)に離して重なりを解消
            make_cursor_v(1720.0, y1=1100.0, y2=1750.0),
            make_cursor_v(1799.0, y1=1100.0, y2=1750.0),
            make_arrow_h(1720.0, 1799.0, 1420.0, "0.2"),
            # 振幅 3.2 (CH2 p-p: Y=753 山頂, Y=1781 谷底) - 右側に配置
            make_cursor_h(753.0), make_cursor_h(1781.0),
            make_arrow_v(1781.0, 753.0, 2980.0, "3.2"),
        ]
    },
    # 12 | 波形4 高周波観測 (40.0ms/div): 0.5 div
    "紫高": {
        "raw": "紫高.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1920.0), make_cursor_v(2079.0),
            make_arrow_h(1920.0, 2079.0, 950.0, "0.5"),
        ]
    },
    # 13 | 波形4 高周波拡大 (20.0ms/div): 1.0 div
    "紫高々": {
        "raw": "紫高々.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            make_cursor_v(1824.0), make_cursor_v(2148.0),
            make_arrow_h(1824.0, 2148.0, 1020.0, "1.0"),
        ]
    },
    # 14 | ワークA-2 指先脈波 (200ms/div): 最長周期 2.4, 次長周期 2.3, 時間差 0.2, 振幅 2.1
    "脈拍": {
        "raw": "脈拍.JPG", "viewBox": "80 120 3820 2560",
        "elements": [
            # 最長周期 T1: 2.4 (X=1632, 2378) - 上部 (Y=620)
            make_cursor_v(1632.0), make_cursor_v(2378.0),
            make_arrow_h(1632.0, 2378.0, 620.0, "2.4"),
            # 次長周期 T2: 2.3 (X=2378, 3080) - T1と並べて上部 (Y=620)
            make_cursor_v(3080.0),
            make_arrow_h(2378.0, 3080.0, 620.0, "2.3"),
            # 時間差 0.2 (CH1とCH2のピーク差: X=1766, 1830) - 下方 (Y=1420) に隔離
            make_cursor_v(1766.0, y1=1000.0, y2=1700.0),
            make_cursor_v(1830.0, y1=1000.0, y2=1700.0),
            make_arrow_h(1766.0, 1830.0, 1420.0, "0.2"),
            # 振幅 2.1 (CH2 p-p: Y=809 山頂, Y=1460 谷底) - 右側 (X=2980)
            make_cursor_h(809.0), make_cursor_h(1460.0),
            make_arrow_v(1460.0, 809.0, 2980.0, "2.1"),
        ]
    },
}

def main():
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

if __name__ == "__main__":
    main()
