"""Batch runner for Arduino peak detection combinations.

marimo ノートブック (b2_plot_graph.py) の名前付きセルを直接インポートし、
myPulse.cpp と b2_plot_graph.py の閾値更新、Arduino への書き込み、
シリアル受信セルおよびグラフ描画セルの実行を自動ループします。
"""

from __future__ import annotations

import glob
import itertools
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml
from b2_plot_graph import capture_serial, plot_graph, setup_params


def find_serial_port() -> str:
    """利用可能なArduinoのシリアルポートを検出する."""
    preferred = [
        "/dev/tty.usbmodemACA7043A47282",
        "/dev/cu.usbmodemACA7043A47282",
    ]
    for p in preferred:
        if Path(p).exists():
            return p
    ports = glob.glob("/dev/tty.usbmodem*") + glob.glob("/dev/cu.usbmodem*")
    if ports:
        return ports[0]
    raise RuntimeError("Arduinoのシリアルポートが見つかりません。接続を確認してください。")


def update_my_pulse_cpp(file_path: Path, top: int, down: int) -> None:
    """myPulse.cpp 内の TOP_THRESHOLD と DOWN_THRESHOLD を更新する."""
    content = file_path.read_text(encoding="utf-8")
    content = re.sub(
        r"#define\s+TOP_THRESHOLD\s+\d+",
        f"#define TOP_THRESHOLD {top}",
        content,
    )
    content = re.sub(
        r"#define\s+DOWN_THRESHOLD\s+\d+",
        f"#define DOWN_THRESHOLD {down}",
        content,
    )
    file_path.write_text(content, encoding="utf-8")


def update_plot_graph_py(file_path: Path, top: int, down: int) -> None:
    """b2_plot_graph.py 内の top_threshold と down_threshold を更新する."""
    content = file_path.read_text(encoding="utf-8")
    content = re.sub(
        r"top_threshold\s*=\s*\d+",
        f"top_threshold = {top}",
        content,
    )
    content = re.sub(
        r"down_threshold\s*=\s*\d+",
        f"down_threshold = {down}",
        content,
    )
    file_path.write_text(content, encoding="utf-8")


def upload_to_arduino(sketch_dir: Path, port: str, fqbn: str) -> None:
    """arduino-cli を使用してスケッチをコンパイル＆アップロードする."""
    cmd = [
        "arduino-cli",
        "compile",
        "--fqbn",
        fqbn,
        "-u",
        "-p",
        port,
        str(sketch_dir),
    ]
    print(f"-> Arduino 書き込み実行中: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("--- stderr ---")
        print(result.stderr)
        raise RuntimeError(f"Arduinoへの書き込みに失敗しました (exit code: {result.returncode})")
    print("-> 書き込み完了")


def main() -> None:
    fqbn = "arduino:renesas_uno:unor4wifi"

    script_dir = Path(__file__).resolve().parent
    comb_yaml_path = script_dir.parent / "combination.yaml"
    pulse_cpp_path = script_dir / "myPulse.cpp"
    plot_graph_path = script_dir / "b2_plot_graph.py"

    if not comb_yaml_path.exists():
        print(f"エラー: {comb_yaml_path} が見つかりません。")
        sys.exit(1)

    os.chdir(script_dir)

    # b2_plot_graph.py の設定セル (setup_params) から初期設定値を取得
    _, params = setup_params.run()
    student_id: str = params["student_id"]
    initial_top: int = params["top_threshold"]
    initial_down: int = params["down_threshold"]

    with comb_yaml_path.open(encoding="utf-8") as f:
        conf = yaml.safe_load(f)

    top_values: list[int] = conf.get("TOP", [])
    down_values: list[int] = conf.get("DOWN", [])

    combinations = list(itertools.product(top_values, down_values))
    print(f"=== 組み合わせ実行開始 (全 {len(combinations)} 通り) ===")
    print(f"学籍番号: {student_id}")
    print(f"TOP: {top_values}")
    print(f"DOWN: {down_values}\n")

    port = find_serial_port()
    print(f"検出シリアルポート: {port}\n")

    try:
        for idx, (top, down) in enumerate(combinations, 1):
            print(f"[{idx}/{len(combinations)}] TOP={top}, DOWN={down} の処理を開始")
            file_base = f"b2_{student_id}_top{top}_down{down}"

            # 1. ソースコードの閾値を協調的に更新
            update_my_pulse_cpp(pulse_cpp_path, top=top, down=down)
            update_plot_graph_py(plot_graph_path, top=top, down=down)
            print("-> myPulse.cpp および b2_plot_graph.py の閾値を更新")

            # 2. Arduino へアップロード
            upload_to_arduino(sketch_dir=script_dir, port=port, fqbn=fqbn)
            time.sleep(1.0)

            # 3. marimo のシリアル通信セル (capture_serial) を実行
            capture_serial.run(file_name=file_base, student_id=student_id)
            csv_path = script_dir / f"{file_base}.csv"
            if not csv_path.exists() or csv_path.stat().st_size == 0:
                print("警告: データを受信できませんでした。次の組み合わせに進みます。")
                continue

            # 4. marimo の図描画セル (plot_graph) を実行
            plot_graph.run(
                file_name=file_base,
                student_id=student_id,
                top_threshold=top,
                down_threshold=down,
            )
            print(f"[{idx}/{len(combinations)}] 完了\n")
    finally:
        # 実行完了後（または中断時）に元の最適閾値へ復元
        update_my_pulse_cpp(pulse_cpp_path, top=initial_top, down=initial_down)
        update_plot_graph_py(plot_graph_path, top=initial_top, down=initial_down)
        print(f"-> 閾値設定を初期値 (TOP={initial_top}, DOWN={initial_down}) に復元しました")

    print("=== 全組み合わせの処理が完了しました ===")


if __name__ == "__main__":
    main()
