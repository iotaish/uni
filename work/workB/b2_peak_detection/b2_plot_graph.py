import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## １. ライブラリのインポート
    以下を実行してライブラリをインポート
    """)
    return


@app.cell
def _():
    import serial
    import csv
    import os
    import hashlib
    from datetime import datetime
    import threading
    import numpy as np
    import matplotlib.pyplot as plt
    import japanize_matplotlib
    import pandas as pd

    return csv, datetime, hashlib, pd, plt, serial, threading


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. ファイル名の設定
    出力されるCSVとPNGのファイル名を設定

    以下の「変更する箇所」で，学籍番号とArduinoで設定した閾値を入力
    """)
    return


@app.cell
def _():
    ################### 変更する箇所 ###################
    student_id = 'XXXXXXXX' #自分の学籍番号を省略せずに設定
    top_threshold = 0       #Arduinoのプログラムで設定したTOP_THRESHOLDの値を設定する
    down_threshold = 0      #Arduinoのプログラムで設定したDOWN_THRESHOLDの値を設定する
    ################### 変更ここまで #########################

    file_name = f'b2_{student_id}_top{top_threshold}_down{down_threshold}' #上記の設定により自動でファイル名が設定される
    return down_threshold, file_name, student_id, top_threshold


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ３. シリアル通信によるデータの読み込み
    port='/dev/tty'の y と ' の間にカーソルを合わせ . を入力すると候補が表示されるので，usbmodem.....を選択
    実行後にArduinoからの信号待ち状態に入る

    eを入力し，Enterで終了するとそれまでにArudinoから送信されたデータがファイルに出力される
    """)
    return


@app.cell
def _(csv, datetime, file_name, serial, student_id, threading):
    ################### 変更する箇所：シリアルポート ###################
    ## ttyの後ろに.を入力すると候補が表示されるのでusbmodemの方を選択（数値は各々のMacやArduinoによって異なる）
    ##例：ser = serial.Serial(port='/dev/tty.usbmodem4827E2E0D9D02', baudrate=115200, timeout=1) 
    ser = serial.Serial(port='/dev/tty', baudrate=115200, timeout=1)
    _data = []
    exit_flag = False
    ###################  これ以降は修正の必要はない  ###################

    def save_to_csv(data):
        with open(f'{file_name}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)

    def log_to_file(port):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_data = [current_time, port, file_name]
        log_file = f'b2_{student_id}_log.csv'  # ミリ秒まで取得
        try:
            with open(log_file, 'x', newline='') as log:
                writer = csv.writer(log)
                writer.writerow(['Timestamp', 'Port', 'OutputFile'])
                writer.writerow(log_data)
        except FileExistsError:  # ヘッダー行
            with open(log_file, 'a', newline='') as log:
                writer = csv.writer(log)
                writer.writerow(log_data)

    def read_serial():
        global exit_flag
        while not exit_flag:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line, flush=True)
                parsed_line = line.replace('",', ',').replace('"', '')
                parts = parsed_line.split(',')
                if len(parts) == 3:
                    _data.append([parts[0].strip(), parts[1].strip(), parts[2].strip()])

    def wait_for_exit():
        global exit_flag
        while not exit_flag:
            if input() == 'e':
                exit_flag = True
                save_to_csv(_data)
                log_to_file(ser.port)
                print('終了キーが押されました。データを保存して終了します。')
    print('シリアル通信の読み込み開始，Arduinoのリセットボタンを押して下さい．', flush=True)
    print('ArduinoのTX LEDが消灯後，eを入力しEnterで終了し，ファイルが出力されます', flush=True)  # キー入力を待機
    input_thread = threading.Thread(target=wait_for_exit)
    input_thread.start()
    read_serial()
    input_thread.join()
    ser.close()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ４. 図の描画

    CSVの出力を元にグラフを作成して画像ファイル(PNG形式)で出力する
    2. ファイル名の設定で設定した名前に基づいてcsvの読み込みと，pngの出力が行われる
    """)
    return


@app.cell
def _(
    datetime,
    down_threshold,
    file_name,
    hashlib,
    pd,
    plt,
    student_id,
    top_threshold,
):
    fig = plt.figure(figsize=(8, 4))
    ax = fig.subplots()
    try:
        _data = pd.read_csv(f'{file_name}.csv')
    except pd.errors.EmptyDataError as e:
        raise ValueError('CSVファイルが空です。Arduinoの出力形式を確認してください。') from e
    required_columns = ['time', 'value', 'peak']
    missing_columns = [column for column in required_columns if column not in _data.columns]
    if missing_columns:
        raise ValueError(f'CSV形式が正しくありません。不足している列: {missing_columns}')
    if _data.empty:
        raise ValueError('CSVに測定データがありません。Arduinoの出力を確認してください。')
    canonical_data = _data[['time', 'value', 'peak']].to_csv(index=False, lineterminator='\n', float_format='%.10g')
    full_data_hash = hashlib.sha256(canonical_data.encode('utf-8')).hexdigest()
    data_id = full_data_hash[:12]
    t = _data['time'].values
    v = _data['value'].values
    ax.plot(t, v, marker='o', color='#000000', linestyle='-', markersize=4)
    peak_t = _data['time'][_data['peak'] == 1].values
    peak_v = _data['value'][_data['peak'] == 1].values
    ax.plot(peak_t, peak_v, marker='x', color='red', linestyle='None', markersize=8)
    ax.xaxis.set_tick_params(labelsize=16)
    ax.yaxis.set_tick_params(labelsize=16)
    ax.xaxis.labelpad = 8
    ax.yaxis.labelpad = 8
    ax.axhline(y=top_threshold, linestyle='--', linewidth=1.5, color='orange')
    ax.set_xlabel('time (s)', fontsize=20)
    ax.set_ylabel('value', fontsize=20)
    plot_created_at = datetime.now()
    plot_time_text = plot_created_at.strftime('%Y-%m-%d %H:%M:%S')
    plot_time_filename = plot_created_at.strftime('%Y%m%d_%H%M%S')
    ax.set_title(f'学籍番号: {student_id}  TOP={top_threshold}, DOWN={down_threshold}\n図作成時刻: {plot_time_text}  データID: {data_id}', fontsize=12)
    plt.tight_layout()
    output_png = f'{file_name}_{plot_time_filename}_{data_id}.png'
    plt.savefig(output_png, dpi=150)
    print(f'画像ファイルを保存しました: {output_png}')
    plt.show()
    return


if __name__ == "__main__":
    app.run()
