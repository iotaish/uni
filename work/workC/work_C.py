import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ワークC データ取得・分析（marimo ノートブック）
    本ノートブックは、ワークCにおける以下の全課題を単一の環境で統合実行・可視化します：
    1. **ワークC-1**: フォトリフレクタによる距離--電圧特性曲線のプロット（`result_C1.png`）
    2. **ワークC-2**: 組み込みWebサーバからの照度変化データ収集（100秒・101点、`result_C2.csv`、`result_C2.png`）
    3. **ワークC-3**: 移動平均（MA）および指数移動平均（EMA）による平滑化と3段比較波形（`result_C3.png`）
    """)
    return


@app.cell
def _():
    from collections import deque
    from datetime import datetime
    import hashlib
    from pathlib import Path
    import threading
    import time
    import japanize_matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import requests

    return Path, deque, np, pd, plt, requests, threading, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 共通設定
    学籍番号およびArduino Webサーバ接続先URLを設定します。
    """)
    return


@app.cell
def _():
    student_id = "26G1012"
    student_id_num = 12  # 学籍番号の下3桁（8進数解釈を防ぐため先頭0を除く）
    server_url = f"http://192.168.{student_id_num}.2"
    return (server_url,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. ワークC-1: フォトリフレクタ遮蔽物距離と出力電圧の測定
    センサ受発光面と遮蔽物間の距離（0.5cm〜5.0cm）に対するA0電圧値をプロットし、特性曲線を保存します。
    """)
    return


@app.cell
def _():
    d = [0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50, 4.00, 4.50, 5.00]
    v = [1.19, 2.94, 3.73, 4.06, 4.34, 4.50, 4.60, 4.69, 4.72, 4.75]
    return d, v


@app.cell
def _(Path, d, plt, v):
    fig_c1, ax_c1 = plt.subplots(figsize=(6, 6))

    ax_c1.plot(d, v, "ko-", markersize=6, linewidth=1.5)
    ax_c1.set_xlabel("距離 (cm)", fontsize=16, labelpad=8)
    ax_c1.set_ylabel("電圧 (V)", fontsize=16, labelpad=8)
    ax_c1.set_xlim(0, 5.2)
    ax_c1.set_ylim(0, 5.3)
    ax_c1.tick_params(labelsize=14)
    ax_c1.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_c1 = Path("result_C1.png")
    report_c1 = Path("../../report/fig_work_C/result_C1.png")
    report_c1.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_c1, dpi=300)
    plt.savefig(report_c1, dpi=300)
    print(f"C-1 グラフ保存完了: {out_c1} / {report_c1}")
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. ワークC-2: 組み込みWebサーバ疎通と照度データ取得
    Arduino（SoftAP: `ZZAP012`）とPC間でHTTP通信を行い、100秒間の時系列電圧データを記録します。
    """)
    return


@app.cell
def _(requests):
    # 練習問題1: 外部Webサーバ接続テスト
    try:
        r_ad = requests.get("https://admission.chibatech.ac.jp", timeout=5)
        print("練習問題1 ステータスコード:", r_ad.status_code)
    except Exception as e:
        print("練習問題1 待機（オフライン環境等）:", e)
    return


@app.cell
def _(requests, server_url):
    # 練習問題3: Arduino Webサーバ疎通テスト
    try:
        r_ard = requests.get(server_url, timeout=3)
        print("練習問題3 Status Code:", r_ard.status_code)
        print("練習問題3 Value:", r_ard.json()["value"])
    except Exception as e:
        print("練習問題3 Arduino未接続または待機中:", e)
    return


@app.cell
def _(deque, np, pd, requests, server_url, threading, time):
    num_samples = 101
    sample_interval = 1.0
    val_queue = deque([np.nan] * num_samples, maxlen=num_samples)
    recorded_data = []
    latest_val = 0.0
    http_session = requests.Session()


    def fetch_worker():
        global latest_val
        try:
            res = http_session.get(server_url, timeout=sample_interval * 0.8)
            res.raise_for_status()
            latest_val = float(res.json()["value"])
        except Exception:
            pass


    def collect_100s_data():
        base_time = time.perf_counter()
        for idx in range(num_samples):
            threading.Thread(target=fetch_worker, daemon=True).start()
            time.sleep(
                max(
                    0,
                    base_time + (idx + 1) * sample_interval - time.perf_counter(),
                )
            )
            val_queue.append(latest_val)
            recorded_data.append(latest_val)
        pd.DataFrame({"voltage": recorded_data}).to_csv("result_C2.csv", index=False)
        print(f"収集完了: {len(recorded_data)} 点を result_C2.csv に保存しました")


    collect_100s_data()
    return


@app.cell
def _(Path, np, pd, plt):
    csv_path_c2 = Path("result_C2.csv")
    if csv_path_c2.exists():
        df_c2 = pd.read_csv(csv_path_c2)
        fig_c2, ax_c2 = plt.subplots(figsize=(8, 4.5))
        ax_c2.plot(
            np.arange(len(df_c2)),
            df_c2["voltage"],
            "ko-",
            markersize=3,
            linewidth=1.2,
        )
        ax_c2.set_xlabel("時間 (s)", fontsize=16, labelpad=8)
        ax_c2.set_ylabel("電圧 (V)", fontsize=16, labelpad=8)
        ax_c2.set_xlim(0, 100)
        ax_c2.set_ylim(2.0, 4.5)
        ax_c2.tick_params(labelsize=14)
        ax_c2.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()

        out_c2 = Path("result_C2.png")
        report_c2 = Path("../../report/fig_work_C/result_C2.png")
        report_c2.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_c2, dpi=300)
        plt.savefig(report_c2, dpi=300)
        print(f"C-2 グラフ保存完了: {out_c2} / {report_c2}")
        plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. ワークC-3: 時系列データの平滑化（移動平均 MA & 指数移動平均 EMA）
    ウインドウサイズ $M=5$ の移動平均（MA）および指数移動平均（EMA, $\alpha=1/3$）を算出し、3段比較グラフを描画します。
    """)
    return


@app.cell
def _(Path, np, pd, plt):
    csv_path_c3 = Path("result_C2.csv")
    if csv_path_c3.exists():
        df_c3 = pd.read_csv(csv_path_c3)
        v_raw = df_c3["voltage"]
        v_ma = v_raw.rolling(window=5).mean()
        v_ema = v_raw.ewm(span=5, adjust=False).mean()

        fig_c3, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
        t_axis = np.arange(len(v_raw))

        # 1段目: 生データ (Raw)
        ax1.plot(t_axis, v_raw, "ko-", markersize=3, linewidth=1, label="voltage")
        ax1.set_ylabel("電圧 (V)", fontsize=14)
        ax1.set_ylim(2.0, 4.5)
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="upper right", fontsize=12)
        ax1.tick_params(labelsize=12)

        # 2段目: 移動平均 (MA)
        ax2.plot(t_axis, v_ma, "ro-", markersize=3, linewidth=1, label="voltage_MA")
        ax2.set_ylabel("電圧 (V)", fontsize=14)
        ax2.set_ylim(2.0, 4.5)
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="upper right", fontsize=12)
        ax2.tick_params(labelsize=12)

        # 3段目: 指数移動平均 (EMA)
        ax3.plot(
            t_axis,
            v_ema,
            "bo-",
            markersize=3,
            linewidth=1,
            label="voltage_EMA",
        )
        ax3.set_xlabel("時間 (s)", fontsize=14, labelpad=8)
        ax3.set_ylabel("電圧 (V)", fontsize=14)
        ax3.set_ylim(2.0, 4.5)
        ax3.set_xlim(0, 100)
        ax3.grid(True, linestyle="--", alpha=0.5)
        ax3.legend(loc="upper right", fontsize=12)
        ax3.tick_params(labelsize=12)

        plt.tight_layout()
        out_c3 = Path("result_C3.png")
        report_c3 = Path("../../report/fig_work_C/result_C3.png")
        report_c3.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_c3, dpi=300)
        plt.savefig(report_c3, dpi=300)
        print(f"C-3 グラフ保存完了: {out_c3} / {report_c3}")
        plt.show()
    return


if __name__ == "__main__":
    app.run()
