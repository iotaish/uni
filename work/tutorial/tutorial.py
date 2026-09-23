from pathlib import Path

import matplotlib
import matplotlib.font_manager
import matplotlib.pyplot as plt
import pandas as pd

# スクリプト自身のディレクトリを取得
BASE_DIR = Path(__file__).resolve().parent

# 日本語フォントの設定（macOS/Linux/Windows対応）
_JP_FONTS = [
    "Hiragino Sans",
    "Yu Gothic",
    "Meiryo",
    "MS Gothic",
    "Noto Sans CJK JP",
    "IPAexGothic",
]
installed = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
jp_font = next((f for f in _JP_FONTS if f in installed), None)
if jp_font:
    plt.rcParams["font.family"] = jp_font
plt.rcParams["axes.unicode_minus"] = False

fig = plt.figure(figsize=(8, 4))
ax = fig.subplots()

# 修正箇所: スクリプトと同じ階層から読み込み・保存
csv_path = BASE_DIR / "tutorial_data.csv"
output_path = BASE_DIR / "../../report/fig" / "result_tutorial.png"

data = pd.read_csv(csv_path)
t = data["time"].values
v = data["value"].values
ax.plot(t, v, "ko-", markersize=6)
ax.set_xlabel("時間 (s)", fontsize=20, labelpad=8)
ax.set_ylabel("デジタル出力値", fontsize=20, labelpad=8)
ax.tick_params(labelsize=16)
plt.tight_layout()
plt.savefig(output_path)
plt.show()
