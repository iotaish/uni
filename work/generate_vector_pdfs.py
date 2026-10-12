import os
import glob
import xml.etree.ElementTree as ET
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import numpy as np

# Font setup
font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
font_prop = fm.FontProperties(fname=font_path)

BASE_DIR = '/Users/ishpctrin/uni/aw/agilework/report/fig_work_A'
SVG_DIR = os.path.join(BASE_DIR, 'svg')
RAW_DIR = os.path.join(BASE_DIR, 'raw')
CONTACT_DIR = os.path.join(BASE_DIR, 'contact_sheets')

TILES_INFO = [
    ("緑", "01 | 緑.JPG [波形1: 低周波観測 / 200ms/div]"),
    ("赤", "02 | 赤.JPG (無印) [波形2: 低周波観測 / 200ms/div]"),
    ("赤高", "03 | 赤高.JPG (高) [波形2: 高周波観測 / 40.0ms/div]"),
    ("赤高々", "04 | 赤高々.JPG (高々) [波形2: 高周波拡大 / 4.00ms/div]"),
    ("赤位相差", "05 | 赤位相差.JPG (位相差) [波形2: 過渡期観測 / 40.0ms/div]"),
    ("青", "06 | 青.JPG (無印) [波形3: 低周波観測 / 200ms/div]"),
    ("青高", "07 | 青高.JPG (高) [波形3: 高周波観測 / 100ms/div]"),
    ("青高々", "08 | 青高々.JPG (高々) [波形3: 高周波拡大 / 40.0ms/div]"),
    ("青高々2", "09 | 青高々2.JPG (高々) [波形3: 高周波拡大・別テイク / 40.0ms/div]"),
    ("青位相差", "10 | 青位相差.JPG (位相差) [波形3: 過渡期観測 / 200ms/div]"),
    ("紫", "11 | 紫.JPG (無印) [波形4: 低周波観測 / 200ms/div]"),
    ("紫高", "12 | 紫高.JPG (高) [波形4: 高周波観測 / 40.0ms/div]"),
    ("紫高々", "13 | 紫高々.JPG (高々) [波形4: 高周波拡大 / 20.0ms/div]"),
    ("脈拍", "14 | 脈拍.JPG [ワークA-2: 指先脈波 / 200ms/div]"),
]

def parse_svg(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    vb = [float(v) for v in root.attrib.get('viewBox', '0 0 4000 3000').split()]
    vx, vy, vw, vh = vb
    
    lines = []
    badges = []
    raw_filename = None
    
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag == 'image':
            href = elem.attrib.get('href', '')
            raw_filename = os.path.basename(href)
        elif tag == 'line':
            attrib = elem.attrib
            x1 = float(attrib['x1'])
            y1 = float(attrib['y1'])
            x2 = float(attrib['x2'])
            y2 = float(attrib['y2'])
            stroke = attrib.get('stroke', '#FFFFFF')
            stroke_width = float(attrib.get('stroke-width', '3'))
            dash = attrib.get('stroke-dasharray', None)
            is_arrow = 'marker-start' in attrib or 'marker-end' in attrib
            lines.append({
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'stroke': stroke, 'stroke_width': stroke_width,
                'dash': dash, 'is_arrow': is_arrow
            })
        elif tag == 'g' and 'transform' in elem.attrib:
            # check if it contains rect and text
            t = elem.attrib['transform']
            if 'translate' in t:
                coords = t.replace('translate(', '').replace(')', '').split(',')
                tx = float(coords[0])
                ty = float(coords[1])
                rect = elem.find('{http://www.w3.org/2000/svg}rect')
                text = elem.find('{http://www.w3.org/2000/svg}text')
                if rect is not None and text is not None:
                    rw = float(rect.attrib.get('width', '100'))
                    rh = float(rect.attrib.get('height', '50'))
                    edge_color = rect.attrib.get('stroke', '#00E5FF')
                    val = text.text
                    badges.append({
                        'x': tx, 'y': ty, 'w': rw, 'h': rh,
                        'edge_color': edge_color, 'text': val
                    })
    return (vx, vy, vw, vh), raw_filename, lines, badges

def render_on_axis(ax, name, show_header=False, header_title=""):
    svg_path = os.path.join(SVG_DIR, f"{name}.svg")
    (vx, vy, vw, vh), raw_filename, lines, badges = parse_svg(svg_path)
    raw_path = os.path.join(RAW_DIR, raw_filename)
    
    img = cv2.imread(raw_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Display background image within crop [vx, vy, vw, vh]
    # Note: image coordinate: x in [0, 4000], y in [0, 3000]
    # We display full image but set limits to [vx, vx+vw] and [vy+vh, vy] (inverted Y for image)
    ax.imshow(img_rgb, extent=[0, 4000, 3000, 0], aspect='auto')
    ax.set_xlim(vx, vx + vw)
    ax.set_ylim(vy + vh, vy) # Y down
    ax.axis('off')
    
    # Draw vector lines
    for l in lines:
        if l['is_arrow']:
            # Double-headed arrow
            # Convert stroke width for matplotlib points
            lw = l['stroke_width'] * 0.75
            ax.annotate(
                '', xy=(l['x2'], l['y2']), xytext=(l['x1'], l['y1']),
                arrowprops=dict(
                    arrowstyle='<|-|>,head_length=0.45,head_width=0.25',
                    color=l['stroke'], lw=lw, shrinkA=0, shrinkB=0
                )
            )
        else:
            # Dashed line
            # Matplotlib dash pattern
            lw = l['stroke_width'] * 0.6
            ax.plot(
                [l['x1'], l['l2'] if 'l2' in l else l['x2']],
                [l['y1'], l['l2'] if 'l2' in l else l['y2']],
                color=l['stroke'], lw=lw,
                linestyle=(0, (6, 4)), alpha=0.85
            )
            
    # Draw badges
    for b in badges:
        # Center of badge
        cx = b['x'] + b['w'] / 2.0
        cy = b['y'] + b['h'] / 2.0
        # Text with round bounding box
        bbox_props = dict(
            boxstyle=f"round,pad=0.25,rounding_size=0.4",
            fc="#0A0D12", ec=b['edge_color'], lw=1.2, alpha=0.92
        )
        ax.text(
            cx, cy, b['text'],
            color='#FFFFFF', fontsize=9.5, fontweight='bold',
            ha='center', va='center', bbox=bbox_props
        )
        
    if show_header:
        # Header bar at the top
        header_h = vh * 0.055
        rect_h = patches.Rectangle(
            (vx, vy), vw, header_h,
            linewidth=0, facecolor='#0D1117', alpha=0.92, zorder=10
        )
        ax.add_patch(rect_h)
        ax.text(
            vx + vw * 0.02, vy + header_h * 0.62,
            header_title,
            color='#F0F6FC', fontsize=8.5, fontweight='bold',
            va='center', fontproperties=font_prop, zorder=11
        )

# 1. Generate Individual Vector PDFs
print("=== Generating Individual Vector PDFs ===")
for name, title in TILES_INFO:
    svg_path = os.path.join(SVG_DIR, f"{name}.svg")
    (vx, vy, vw, vh), _, _, _ = parse_svg(svg_path)
    
    fig_w = 8.0 # inches
    fig_h = 8.0 * (vh / vw)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    render_on_axis(ax, name, show_header=False)
    
    pdf_out = os.path.join(BASE_DIR, f"{name}.pdf")
    fig.savefig(pdf_out, format='pdf', dpi=150)
    plt.close(fig)
    print(f"Saved: {pdf_out} ({os.path.getsize(pdf_out) / 1024:.1f} KB)")

# 2. Generate 15-Waveform Contact Sheet Vector PDF
print("=== Generating Contact Sheet Vector PDF ===")
cols = 3
rows = 5
fig_w = 20.0
fig_h = 20.0 * (rows / cols) * (2560 / 3820)
fig, axes = plt.subplots(rows, cols, figsize=(fig_w, fig_h), dpi=150)
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.015, hspace=0.02)

for idx, (name, title) in enumerate(TILES_INFO):
    r = idx // cols
    c = idx % cols
    ax = axes[r, c]
    render_on_axis(ax, name, show_header=True, header_title=title)

# 15th tile: Summary card
ax15 = axes[4, 2]
ax15.set_facecolor('#0D1117')
ax15.axis('off')
summary_text = (
    "15 | 測定諸元一覧 ＆ アノテーション凡例\n\n"
    "【アノテーション表示規則】\n"
    "・数値表記: 目盛り読み取り値そのもの（div単位・単位省略）\n"
    "・青線 (Cyan): 時間間隔・周期・遅延時間（水平寸法線）\n"
    "・橙線 (Orange): 電圧振幅（垂直寸法線）\n"
    "・白破線 (Dashed): 波形ピーク・谷底・過渡エッジを貫くカーソル線\n\n"
    "【ワークA-1 目盛り読み取り諸元（表1.2）】\n"
    "・波形1 (1Hz正弦波): 周期 2.0, 振幅 7.0 (200ms/div, 100mV/div)\n"
    "・波形2 (1Hz+100Hz): 周期 2.5, 振幅 2.0 (200ms/div, 500mV/div)\n"
    "・波形3 (1Hz+7Hz): 周期 2.5, 振幅 4.0 (200ms/div, 200mV/div)\n"
    "・波形4 (模擬脈波): 周期 3.7, 時間差 0.2, 振幅 3.2 (200ms/div, 500mV/div)\n\n"
    "【ワークA-2 指先脈波読み取り諸元（表1.4）】\n"
    "・最長周期 T1: 2.4, 振幅 2.1, 時間差 0.2 (200ms/div, 500mV/div)\n"
    "・次長周期 T2: 2.3, 振幅 2.1, 時間差 0.2 (200ms/div, 500mV/div)\n\n"
    "※下段スケール(CH1, CH2, TIME/DIV)および右下日時スタンプ完全保持"
)
ax15.text(
    0.05, 0.95, summary_text,
    color='#C9D1D9', fontsize=11, fontproperties=font_prop,
    va='top', ha='left', transform=ax15.transAxes, linespacing=1.6
)

sheet_pdf_out = os.path.join(CONTACT_DIR, "sheet_all_15waveforms_annotated.pdf")
fig.savefig(sheet_pdf_out, format='pdf', dpi=150)
plt.close(fig)
print(f"Saved Contact Sheet PDF: {sheet_pdf_out} ({os.path.getsize(sheet_pdf_out) / 1024 / 1024:.2f} MB)")
print("ALL DONE!")
