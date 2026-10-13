#!/usr/bin/env python3
"""
sync_measurements.py

全14波形SVGの測定アノテーション（周期・振幅・位相差）を、
ユーザーの手本に基づく「中点基準 (Center-Origin)」構造で一括生成・同期するスクリプト。

手本構造:
  親: transform="translate(x_mid, y_mid)"
  振幅 (垂直):
    - 上端線: y = -half
    - 下端線: y = +half
    - 矢印: (0, -half) -> (0, +half)
    - バッジ: translate(30.0, 0.0)
  周期・位相差 (水平):
    - 左端線: x = -half
    - 右端線: x = +half
    - 矢印: (-half, 0) -> (+half, 0)
    - バッジ: translate(-w/2, -70.0)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import re

SVG_DIR = Path(__file__).resolve().parent.parent / "report" / "fig_work_A" / "svg"

@dataclass
class PeriodMeas:
    id: str
    cx: float               # 水平中心 X (変数)
    cy: float               # 矢印 Y
    half: float             # 半周期・半遅延 dx/2 (変数)
    badge: str              # 表示div値
    y_range: Tuple[float, float] = (-250.0, 250.0)  # 補助線のY範囲 (中点相対)
    badge_w: int = 110

    def render(self) -> str:
        hw = self.badge_w / 2.0
        y1, y2 = self.y_range
        return f"""    <g id="{self.id}" class="measurement" transform="translate({self.cx:.1f}, {self.cy:.1f})" data-half-span="{self.half:.1f}">
      <line x1="-{self.half:.1f}" y1="{y1:.1f}" x2="-{self.half:.1f}" y2="{y2:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8" />
      <line x1="{self.half:.1f}" y1="{y1:.1f}" x2="{self.half:.1f}" y2="{y2:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8" />
      <line x1="-{self.half:.1f}" y1="0.0" x2="{self.half:.1f}" y2="0.0" stroke="#E040FB" stroke-width="5" marker-start="url(#arrow-magenta)" marker-end="url(#arrow-magenta)" />
      <g transform="translate(-{hw:.1f}, -70.0)">
        <rect width="{self.badge_w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#E040FB" stroke-width="2" />
        <text x="{hw:.1f}" y="44.0" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold" text-anchor="middle">{self.badge}</text>
      </g>
    </g>"""

@dataclass
class AmplitudeMeas:
    id: str
    cx: float               # 矢印 X
    cy: float               # 垂直中心 Y (変数)
    half: float             # 半振幅 dy/2 (変数)
    badge: str              # 表示div値
    x_range_top: Tuple[float, float] = (-100.0, 100.0)      # 上端線のX範囲 (中点相対)
    x_range_bottom: Tuple[float, float] = (-100.0, 100.0)   # 下端線のX範囲 (中点相対)
    badge_offset_x: float = 30.0                            # バッジのXオフセット (+30.0: 右, -140.0: 左)
    badge_w: int = 110

    def render(self) -> str:
        hw = self.badge_w / 2.0
        tx1, tx2 = self.x_range_top
        bx1, bx2 = self.x_range_bottom
        return f"""    <g id="{self.id}" class="measurement" transform="translate({self.cx:.1f}, {self.cy:.1f})" data-half-span="{self.half:.1f}">
      <line x1="{tx1:.1f}" y1="-{self.half:.1f}" x2="{tx2:.1f}" y2="-{self.half:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8" />
      <line x1="{bx1:.1f}" y1="{self.half:.1f}" x2="{bx2:.1f}" y2="{self.half:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10" opacity="0.8" />
      <line x1="0.0" y1="-{self.half:.1f}" x2="0.0" y2="{self.half:.1f}" stroke="#00E676" stroke-width="5" marker-start="url(#arrow-green)" marker-end="url(#arrow-green)" />
      <g transform="translate({self.badge_offset_x:.1f}, 0.0)">
        <rect width="{self.badge_w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#00E676" stroke-width="2" />
        <text x="{hw:.1f}" y="44.0" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold" text-anchor="middle">{self.badge}</text>
      </g>
    </g>"""


# 全14波形の測定定義データベース (中点と半スパン変数を明示)
MEASUREMENTS = {
    "紫.svg": [
        # CH1低周波周期: 1712 -> 2863 (下向き補助線 0..500)
        PeriodMeas(id="meas-period-ch1", cx=2287.5, cy=620.0, half=575.5, badge="4.4", y_range=(0.0, 500.0)),
        # 位相差: 1715 -> 1755
        PeriodMeas(id="meas-phase-diff", cx=1735.0, cy=1300.0, half=20.0, badge="0.15", y_range=(-250.0, 250.0), badge_w=140),
        # CH1振幅 (橙): 1080 -> 1729
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2680.0, cy=1404.5, half=324.5, badge="3.0", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
        # CH2振幅 (シアン): ユーザー手本そのもの (cy=1450.0, half=385.0)
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2980.0, cy=1450.0, half=385.0, badge="3.2", x_range_top=(-100.0, 100.0), x_range_bottom=(-80.0, 200.0)),
    ],
    "紫高.svg": [
        # 全画面周期: 550 -> 3250
        PeriodMeas(id="meas-period-fullscreen", cx=1900.0, cy=750.0, half=1350.0, badge="10.3", y_range=(-500.0, 500.0), badge_w=140),
    ],
    "紫高々.svg": [],  # アノテーション非表示
    "緑.svg": [
        # 周期: 1868 -> 2641
        PeriodMeas(id="meas-period", cx=2254.5, cy=680.0, half=386.5, badge="3.0", y_range=(-250.0, 250.0)),
        # CH2振幅 (シアン): 440 -> 2050
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2920.0, cy=1245.0, half=805.0, badge="7.4", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "脈拍.svg": [
        # CH2周期 (シアン山頂間): 955 -> 1824
        PeriodMeas(id="meas-period-ch2", cx=1389.5, cy=620.0, half=434.5, badge="3.3", y_range=(-100.0, 100.0)),
        # 位相差: 1760 -> 1824
        PeriodMeas(id="meas-phase-diff", cx=1792.0, cy=1350.0, half=32.0, badge="0.2", y_range=(-80.0, 80.0)),
        # CH2振幅 (シアン 2135): 1115 -> 1579 (dy=464)
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2135.0, cy=1347.0, half=232.0, badge="2.1", x_range_top=(-80.0, 80.0), x_range_bottom=(-80.0, 80.0)),
        # CH1振幅 (黄色 2800): 1157 -> 1589 (dy=432)
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2800.0, cy=1373.0, half=216.0, badge="2.0", x_range_top=(-80.0, 80.0), x_range_bottom=(-80.0, 80.0)),
    ],
    "赤.svg": [
        # 周期: 1920 -> 2699
        PeriodMeas(id="meas-period", cx=2309.5, cy=800.0, half=389.5, badge="3.0", y_range=(-250.0, 250.0)),
        # CH1振幅: 1080 -> 1635
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2900.0, cy=1357.5, half=277.5, badge="2.6", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "赤位相差.svg": [
        # 位相差: 2085 -> 2200
        PeriodMeas(id="meas-phase-diff", cx=2142.5, cy=1260.0, half=57.5, badge="0.44", y_range=(-300.0, 300.0), badge_w=140),
    ],
    "赤高.svg": [
        # 周期: 2234 -> 2764
        PeriodMeas(id="meas-period", cx=2499.0, cy=880.0, half=265.0, badge="2.0", y_range=(-250.0, 250.0)),
        # CH1振幅 (左側 1500): 1265 -> 1631
        AmplitudeMeas(id="meas-amplitude-ch1", cx=1500.0, cy=1448.0, half=183.0, badge="1.7", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "赤高々.svg": [
        # 周期: 1614 -> 2230
        PeriodMeas(id="meas-period", cx=1922.0, cy=850.0, half=308.0, badge="2.4", y_range=(-200.0, 200.0)),
        # リップル振幅: 1120 -> 1400
        AmplitudeMeas(id="meas-amplitude-ripple", cx=2450.0, cy=1260.0, half=140.0, badge="1.3", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "青.svg": [
        # 周期: 1801 -> 2600
        PeriodMeas(id="meas-period", cx=2200.5, cy=680.0, half=399.5, badge="3.0", y_range=(-250.0, 250.0)),
        # CH1振幅: 1083 -> 1674
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2750.0, cy=1378.5, half=295.5, badge="2.7", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
        # CH2振幅: 935 -> 1800
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2980.0, cy=1367.5, half=432.5, badge="4.0", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "青位相差.svg": [
        # 位相差: 1555 -> 1595
        PeriodMeas(id="meas-phase-diff", cx=1575.0, cy=1150.0, half=20.0, badge="0.15", y_range=(-300.0, 300.0), badge_w=140),
    ],
    "青高.svg": [
        # 周期: 2220 -> 2430
        PeriodMeas(id="meas-period", cx=2325.0, cy=750.0, half=105.0, badge="0.8", y_range=(-200.0, 200.0)),
        # CH1振幅: 888 -> 1225
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2650.0, cy=1056.5, half=168.5, badge="1.6", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
        # CH2振幅: 747 -> 1760
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2950.0, cy=1253.5, half=506.5, badge="4.7", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "青高々.svg": [
        # 周期: 1270 -> 1840
        PeriodMeas(id="meas-period", cx=1555.0, cy=1100.0, half=285.0, badge="2.2", y_range=(-200.0, 200.0)),
        # CH1振幅: 1250 -> 1680
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2650.0, cy=1465.0, half=215.0, badge="2.0", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
        # CH2振幅: 1478 -> 1780
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2920.0, cy=1629.0, half=151.0, badge="1.4", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
    "青高々2.svg": [
        # 周期: 1015 -> 1616
        PeriodMeas(id="meas-period", cx=1315.5, cy=1150.0, half=300.5, badge="2.3", y_range=(-200.0, 200.0)),
        # CH1振幅: 1258 -> 1681
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2650.0, cy=1469.5, half=211.5, badge="2.0", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
        # CH2振幅: 1316 -> 1576
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2920.0, cy=1446.0, half=130.0, badge="1.2", x_range_top=(-100.0, 100.0), x_range_bottom=(-100.0, 100.0)),
    ],
}

def sync_svg(svg_filename: str):
    svg_path = SVG_DIR / svg_filename
    if not svg_path.exists():
        print(f"Skipping {svg_filename}: file not found")
        return

    raw_name = svg_filename.replace(".svg", ".JPG")
    meas_list = MEASUREMENTS.get(svg_filename, [])

    if meas_list:
        rendered_meas = "\n".join(m.render() for m in meas_list)
        annotations_block = f"""  <g id="annotations">\n{rendered_meas}\n  </g>"""
    else:
        annotations_block = """  <g id="annotations">\n    <!-- アノテーション非表示 -->\n  </g>"""

    # 完全なSVGをクリーンに構築
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="80 120 3820 2560" width="100%" height="100%">
  <defs>
    <marker id="arrow-magenta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6"
      orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#E040FB" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6"
      orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#00E676" />
    </marker>
  </defs>
  <image href="../raw/{raw_name}" width="4000" height="3000" />
{annotations_block}
</svg>
"""

    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Updated {svg_filename} ({len(meas_list)} measurements synced)")

def main():
    print("Syncing all 14 waveform SVGs with center-origin measurement architecture...")
    for filename in sorted(MEASUREMENTS.keys()):
        sync_svg(filename)
    print("Sync completed successfully.")

if __name__ == "__main__":
    main()
