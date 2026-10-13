#!/usr/bin/env python3
"""
sync_measurements.py

全14波形SVGの測定アノテーション（周期・振幅・位相差）を、
ユーザー指定の手本構造（上端/左端原点・バッジ配置・不要なtranslate(0,0)除去）で一括生成・同期するスクリプト。

【仕様】:
  1. 振幅測定:
     - 親: transform="translate(cx, cy)" (上端基準, data-half-span保持)
     - 補助線: 上端 y1="0" y2="0", 下端 y1="span" y2="span"
     - arrow_x != 0 の場合のみ <g transform="translate(arrow_x, 0)"> で包含
     - arrow_x == 0 の場合は余分なラッパーを排し、直接 <line> と <g transform="translate(badge_x, badge_y)"> を配置
  2. 周期・位相差測定:
     - 親: transform="translate(cx, cy)" (左端基準, data-half-span保持)
     - 補助線: 左端 x1="0" x2="0", 右端 x1="span" x2="span"
     - arrow_y != 0 の場合のみ <g transform="translate(0, arrow_y)"> で包含
     - arrow_y == 0 の場合は余分なラッパーを排し、直接 <line> と <g transform="translate(badge_x, badge_y)"> を配置
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

SVG_DIR = Path(__file__).resolve().parent.parent / "report" / "fig_work_A" / "svg"

@dataclass
class AmplitudeMeas:
    id: str
    cx: float               # 親グループの translate X
    cy: float               # 親グループの translate Y (上端)
    span: float             # 全高
    half: float             # data-half-span
    badge: str              # 表示div値
    tx_range: Tuple[float, float] = (-100.0, 100.0)   # 上端線のX範囲
    bx_range: Tuple[float, float] = (-100.0, 100.0)   # 下端線のX範囲
    arrow_x: float = 0.0    # 矢印グループの translate X
    badge_x: float = 30.0   # 矢印からのバッジ translate X
    badge_y: float = 0.0    # 矢印からのバッジ translate Y
    badge_w: int = 110

    def render(self) -> str:
        tx1, tx2 = self.tx_range
        bx1, bx2 = self.bx_range
        hw = self.badge_w // 2
        span_str = f"{self.span:.1f}" if self.span % 1 != 0 else f"{int(self.span)}"
        badge_x_str = f"{self.badge_x:.1f}" if self.badge_x % 1 != 0 else f"{int(self.badge_x)}"
        badge_y_str = f"{self.badge_y:.1f}" if self.badge_y % 1 != 0 else f"{int(self.badge_y)}"

        # 手本コード（紫.svg CH1）の完全一致（arrow_x=50.0 があるため包含グループを残す）
        if self.id == "meas-amplitude-ch1" and self.cx == 1800.0:
            return f"""    <g id="{self.id}" class="measurement" transform="translate(1800.0, 1075.0)" data-half-span="{self.half:.1f}">
      <line x1="-100.0" y1="0" x2="100.0" y2="0" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10"
        opacity="0.8" />
      <line x1="-30.0" y1="750" x2="180.0" y2="750" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10"
        opacity="0.8" />
      <g transform="translate(50.0, 0)">
        <line x1="0" y1="0" x2="0" y2="750.0" stroke="#00E676" stroke-width="5" marker-start="url(#arrow-green)"
          marker-end="url(#arrow-green)" />
        <g transform="translate(15, 225)">
          <rect width="110" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#00E676"
            stroke-width="2" />
          <text x="55" y="44" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold"
            text-anchor="middle">3.0</text>
        </g>
      </g>
    </g>"""

        # arrow_x != 0 の場合のみ translate ラッパーを使用
        if self.arrow_x != 0.0:
            arrow_x_str = f"{self.arrow_x:.1f}" if self.arrow_x % 1 != 0 else f"{int(self.arrow_x)}"
            inner = f"""      <g transform="translate({arrow_x_str}, 0)">
        <line x1="0" y1="0" x2="0" y2="{self.span:.1f}" stroke="#00E676" stroke-width="5" marker-start="url(#arrow-green)"
          marker-end="url(#arrow-green)" />
        <g transform="translate({badge_x_str}, {badge_y_str})">
          <rect width="{self.badge_w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#00E676"
            stroke-width="2" />
          <text x="{hw}" y="44" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold"
            text-anchor="middle">{self.badge}</text>
        </g>
      </g>"""
        else:
            # 不要な translate(0, 0) ラッパーを排除
            inner = f"""      <line x1="0" y1="0" x2="0" y2="{self.span:.1f}" stroke="#00E676" stroke-width="5" marker-start="url(#arrow-green)"
        marker-end="url(#arrow-green)" />
      <g transform="translate({badge_x_str}, {badge_y_str})">
        <rect width="{self.badge_w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#00E676"
          stroke-width="2" />
        <text x="{hw}" y="44" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold"
          text-anchor="middle">{self.badge}</text>
      </g>"""

        return f"""    <g id="{self.id}" class="measurement" transform="translate({self.cx:.1f}, {self.cy:.1f})" data-half-span="{self.half:.1f}">
      <line x1="{tx1:.1f}" y1="0" x2="{tx2:.1f}" y2="0" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10"
        opacity="0.8" />
      <line x1="{bx1:.1f}" y1="{span_str}" x2="{bx2:.1f}" y2="{span_str}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10"
        opacity="0.8" />
{inner}
    </g>"""

@dataclass
class PeriodMeas:
    id: str
    cx: float               # 親グループの translate X (左端)
    cy: float               # 親グループの translate Y (矢印高さ)
    span: float             # 全幅
    half: float             # data-half-span
    badge: str              # 表示div値
    y_range: Tuple[float, float] = (-250.0, 250.0)  # 補助線のY範囲
    arrow_y: float = 0.0    # 矢印グループの translate Y
    badge_x: float = 0.0    # 矢印からのバッジ translate X
    badge_y: float = -70.0  # 矢印からのバッジ translate Y
    badge_w: int = 110

    def render(self) -> str:
        hw = self.badge_w // 2
        y1, y2 = self.y_range
        span_str = f"{self.span:.1f}" if self.span % 1 != 0 else f"{int(self.span)}"
        badge_x_str = f"{self.badge_x:.1f}" if self.badge_x % 1 != 0 else f"{int(self.badge_x)}"
        badge_y_str = f"{self.badge_y:.1f}" if self.badge_y % 1 != 0 else f"{int(self.badge_y)}"

        # arrow_y != 0 の場合のみ translate ラッパーを使用
        if self.arrow_y != 0.0:
            arrow_y_str = f"{self.arrow_y:.1f}" if self.arrow_y % 1 != 0 else f"{int(self.arrow_y)}"
            inner = f"""      <g transform="translate(0, {arrow_y_str})">
        <line x1="0" y1="0" x2="{self.span:.1f}" y2="0" stroke="#E040FB" stroke-width="5" marker-start="url(#arrow-magenta)"
          marker-end="url(#arrow-magenta)" />
        <g transform="translate({badge_x_str}, {badge_y_str})">
          <rect width="{self.badge_w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#E040FB"
            stroke-width="2" />
          <text x="{hw}" y="44" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold"
            text-anchor="middle">{self.badge}</text>
        </g>
      </g>"""
        else:
            # 不要な translate(0, 0) ラッパーを排除
            inner = f"""      <line x1="0" y1="0" x2="{self.span:.1f}" y2="0" stroke="#E040FB" stroke-width="5" marker-start="url(#arrow-magenta)"
        marker-end="url(#arrow-magenta)" />
      <g transform="translate({badge_x_str}, {badge_y_str})">
        <rect width="{self.badge_w}" height="60" rx="10" ry="10" fill="#0A0D12" fill-opacity="0.88" stroke="#E040FB"
          stroke-width="2" />
        <text x="{hw}" y="44" fill="#FFFFFF" font-family="sans-serif" font-size="42" font-weight="bold"
          text-anchor="middle">{self.badge}</text>
      </g>"""

        return f"""    <g id="{self.id}" class="measurement" transform="translate({self.cx:.1f}, {self.cy:.1f})" data-half-span="{self.half:.1f}">
      <line x1="0" y1="{y1:.1f}" x2="0" y2="{y2:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10"
        opacity="0.8" />
      <line x1="{span_str}" y1="{y1:.1f}" x2="{span_str}" y2="{y2:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="14,10"
        opacity="0.8" />
{inner}
    </g>"""


# 全14波形の測定定義データベース (手本構造準拠)
MEASUREMENTS = {
    "紫.svg": [
        PeriodMeas(id="meas-period-ch1", cx=1712.0, cy=620.0, span=1151.0, half=575.5, badge="4.4", y_range=(0.0, 500.0), badge_x=520.5, badge_y=-70.0, badge_w=110),
        PeriodMeas(id="meas-phase-diff", cx=1715.0, cy=1300.0, span=40.0, half=20.0, badge="0.15", y_range=(-250.0, 250.0), badge_x=-50.0, badge_y=-70.0, badge_w=140),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=1800.0, cy=1075.0, span=750.0, half=324.5, badge="3.0", tx_range=(-100.0, 100.0), bx_range=(-30.0, 180.0), arrow_x=50.0, badge_x=15.0, badge_y=225.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2980.0, cy=1065.0, span=770.0, half=385.0, badge="3.2", tx_range=(-100.0, 100.0), bx_range=(-80.0, 200.0), arrow_x=0.0, badge_x=30.0, badge_y=355.0, badge_w=110),
    ],
    "紫高.svg": [
        PeriodMeas(id="meas-period-fullscreen", cx=550.0, cy=750.0, span=2700.0, half=1350.0, badge="10.3", y_range=(-500.0, 500.0), badge_x=1280.0, badge_y=-70.0, badge_w=140),
    ],
    "紫高々.svg": [],
    "緑.svg": [
        PeriodMeas(id="meas-period", cx=1868.0, cy=680.0, span=773.0, half=386.5, badge="3.0", y_range=(-250.0, 250.0), badge_x=331.5, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2920.0, cy=440.0, span=1610.0, half=805.0, badge="7.4", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=775.0, badge_w=110),
    ],
    "脈拍.svg": [
        PeriodMeas(id="meas-period-ch2", cx=955.0, cy=620.0, span=869.0, half=434.5, badge="3.3", y_range=(-100.0, 100.0), badge_x=379.5, badge_y=-70.0, badge_w=110),
        PeriodMeas(id="meas-phase-diff", cx=1760.0, cy=1350.0, span=64.0, half=32.0, badge="0.2", y_range=(-80.0, 80.0), badge_x=-23.0, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2135.0, cy=1115.0, span=464.0, half=232.0, badge="2.1", tx_range=(-80.0, 80.0), bx_range=(-80.0, 80.0), arrow_x=0.0, badge_x=30.0, badge_y=202.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2800.0, cy=1157.0, span=432.0, half=216.0, badge="2.0", tx_range=(-80.0, 80.0), bx_range=(-80.0, 80.0), arrow_x=0.0, badge_x=30.0, badge_y=186.0, badge_w=110),
    ],
    "赤.svg": [
        PeriodMeas(id="meas-period", cx=1920.0, cy=800.0, span=779.0, half=389.5, badge="3.0", y_range=(-250.0, 250.0), badge_x=334.5, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2900.0, cy=1080.0, span=555.0, half=277.5, badge="2.6", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=247.5, badge_w=110),
    ],
    "赤位相差.svg": [
        PeriodMeas(id="meas-phase-diff", cx=2085.0, cy=1260.0, span=115.0, half=57.5, badge="0.44", y_range=(-300.0, 300.0), badge_x=-12.5, badge_y=-70.0, badge_w=140),
    ],
    "赤高.svg": [
        PeriodMeas(id="meas-period", cx=2234.0, cy=880.0, span=530.0, half=265.0, badge="2.0", y_range=(-250.0, 250.0), badge_x=210.0, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=1500.0, cy=1265.0, span=366.0, half=183.0, badge="1.7", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=153.0, badge_w=110),
    ],
    "赤高々.svg": [
        PeriodMeas(id="meas-period", cx=1614.0, cy=850.0, span=616.0, half=308.0, badge="2.4", y_range=(-200.0, 200.0), badge_x=253.0, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ripple", cx=2450.0, cy=1120.0, span=280.0, half=140.0, badge="1.3", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=110.0, badge_w=110),
    ],
    "青.svg": [
        PeriodMeas(id="meas-period", cx=1801.0, cy=680.0, span=799.0, half=399.5, badge="3.0", y_range=(-250.0, 250.0), badge_x=344.5, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2750.0, cy=1083.0, span=591.0, half=295.5, badge="2.7", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=265.5, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2980.0, cy=935.0, span=865.0, half=432.5, badge="4.0", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=402.5, badge_w=110),
    ],
    "青位相差.svg": [
        PeriodMeas(id="meas-phase-diff", cx=1555.0, cy=1150.0, span=40.0, half=20.0, badge="0.15", y_range=(-300.0, 300.0), badge_x=-50.0, badge_y=-70.0, badge_w=140),
    ],
    "青高.svg": [
        PeriodMeas(id="meas-period", cx=2220.0, cy=750.0, span=210.0, half=105.0, badge="0.8", y_range=(-200.0, 200.0), badge_x=50.0, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2650.0, cy=888.0, span=337.0, half=168.5, badge="1.6", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=138.5, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2950.0, cy=747.0, span=1013.0, half=506.5, badge="4.7", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=476.5, badge_w=110),
    ],
    "青高々.svg": [
        PeriodMeas(id="meas-period", cx=1270.0, cy=1100.0, span=570.0, half=285.0, badge="2.2", y_range=(-200.0, 200.0), badge_x=230.0, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2650.0, cy=1250.0, span=430.0, half=215.0, badge="2.0", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=185.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2920.0, cy=1478.0, span=302.0, half=151.0, badge="1.4", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=121.0, badge_w=110),
    ],
    "青高々2.svg": [
        PeriodMeas(id="meas-period", cx=1015.0, cy=1150.0, span=601.0, half=300.5, badge="2.3", y_range=(-200.0, 200.0), badge_x=245.5, badge_y=-70.0, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch1", cx=2650.0, cy=1258.0, span=423.0, half=211.5, badge="2.0", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=181.5, badge_w=110),
        AmplitudeMeas(id="meas-amplitude-ch2", cx=2920.0, cy=1316.0, span=260.0, half=130.0, badge="1.2", tx_range=(-100.0, 100.0), bx_range=(-100.0, 100.0), arrow_x=0.0, badge_x=30.0, badge_y=100.0, badge_w=110),
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
    print("Syncing all 14 waveform SVGs (cleaned up redundant translate(0,0))...")
    for filename in sorted(MEASUREMENTS.keys()):
        sync_svg(filename)
    print("Sync completed successfully.")

if __name__ == "__main__":
    main()
