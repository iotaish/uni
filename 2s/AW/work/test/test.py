import sys

import cv2
import matplotlib
import matplotlib.font_manager
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ---- 日本語フォントの設定（japanize_matplotlib は使わない）----
# 環境にインストール済みの日本語フォントを探して使う．
_JP_FONTS = [
    "Hiragino Sans",
    "Yu Gothic",
    "Meiryo",
    "MS Gothic",
    "Noto Sans CJK JP",
    "IPAexGothic",
    "IPAPGothic",
    "IPAGothic",
    "TakaoPGothic",
]


def _find_jp_font():
    installed = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    return next((f for f in _JP_FONTS if f in installed), None)


if _find_jp_font() is None and "google.colab" in sys.modules:
    # Colab には日本語フォントが無いためインストールする（初回のみ数十秒かかる）
    import glob
    import subprocess

    print("日本語フォントをインストールしています（初回のみ）...")
    subprocess.run(
        "apt-get -y -qq install fonts-ipafont-gothic", shell=True, capture_output=True
    )
    for _path in glob.glob("/usr/share/fonts/**/ipa*.ttf", recursive=True):
        matplotlib.font_manager.fontManager.addfont(_path)

_jp_font = _find_jp_font()
if _jp_font is None:
    print("警告: 日本語フォントが見つかりません．グラフ中の日本語が文字化けします．")
plt.rcParams["font.family"] = _jp_font or "sans-serif"
plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化けを防ぐ
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["pdf.fonttype"] = 42  # PDF / EPS に日本語フォントを埋め込む
plt.rcParams["ps.fonttype"] = 42
print("使用する日本語フォント:", plt.rcParams["font.family"][0])

# ---- matplotlib のテスト（複数系列の折れ線グラフ） ----
x = np.arange(0, 2.0 * np.pi, 0.2)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y, "ko-", linewidth=1, label="ko-")
ax.plot(x + 0.5, y, "r^--", linewidth=1, label="r^--")
ax.plot(x + 1.0, y, "bx:", linewidth=1, label="bx:")
ax.plot(x + 1.5, y, "gs-.", linewidth=1, label="gs-.")
ax.plot(x + 2.0, y, "yd-", linewidth=1, label="yd-.")

ax.set_xlim(0, 2.0 * np.pi + 2.0)
ax.set_ylim(-1.2, 1.2)
ax.set_xlabel("$X$", fontsize=20, labelpad=8)
ax.set_ylabel(
    "$y$",
    fontsize=20,
    labelpad=8,
)
ax.tick_params(labelsize=16)
ax.legend()
plt.title("複数系列の折れ線グラフ", fontsize=16)
plt.tight_layout()
plt.show()

# ---- SciPy：正規分布の累積分布関数（CDF） ----
z_values = np.arange(-3.0, 3.1, 0.1)
cdf_values = stats.norm.cdf(z_values)
df = pd.DataFrame({"z": z_values, "下側確率": cdf_values})
print("---- SciPy CDF テーブル ----")
print(df)

# ---- OpenCV：基本機能のテスト ----
print("OpenCV version:", cv2.__version__)
try:
    dummy = np.zeros((10, 10), dtype=np.uint8)
    blurred = cv2.GaussianBlur(dummy, (3, 3), 0)
    edges = cv2.Canny(blurred, 100, 200)
    print("OpenCVの基本処理は正常に動作しています。")
except Exception as e:
    print("OpenCVの処理でエラーが発生しました:", e)
