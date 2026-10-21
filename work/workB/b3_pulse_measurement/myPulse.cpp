#include "myPulse.h"

#define PIN_IN A0      // アナログ入力PINの設定
#define DELAY_TIME 20  // ディレイ時間(ms)の設定

#define TOP_THRESHOLD 400  // 信号が山の部分にあるかの判定に利用する閾値
#define DOWN_THRESHOLD 2   // 下降傾向にあるかの判定に利用する閾値
#define UP_THRESHOLD 1     // 上昇傾向にあるかの判定に利用する閾値

// アナログ入力で読み込んだ信号からピークを検出する関数
uint16_t top() {
  uint16_t maximum = 0;       // 最大値の保存用
  uint16_t value = 0;         // 読み込んだ信号の保存用
  uint8_t up_count = 0;       // 上昇傾向を判定するためのカウント
  uint8_t down_count = 0;     // 下降傾向を判定するためのカウント
  uint8_t timeout = 255;      // タイムアウトまでのカウント
  bool peak_started = false;  // 上昇傾向にあると判定されたか

  while (timeout--) {
    value = analogRead(PIN_IN);  // アナログ入力で値を読み取る

    if (value >= TOP_THRESHOLD) {  // 読み込んだ値が山の閾値以上である場合のみピーク検出の処理を行う
      if (value > maximum) {       // 読み込んだ値が最大値より大きい場合，maximum, up_count, down_countを更新する
        maximum = value;           // 最大値（maximum）を更新する
        up_count++;                // 最大値が更新されたため，up_countを増やす
        down_count = 0;            // 最大値が更新されたため，down_countを初期化する
      } else {
        down_count++;  // 最大値を更新しなかったため，down_countを増やす
      }
    }

    // up_countがUP_THRESHOLDより大きい場合，上昇傾向にあると判定する
    if (up_count > UP_THRESHOLD) peak_started = true;

    // TOP_THRESHOLD未満になり，上昇傾向と判定されていない場合は，次の山を探し直す
    if (value < TOP_THRESHOLD && !peak_started) {
      maximum = 0;
      up_count = 0;
      down_count = 0;
    }

    // 上昇傾向と下降傾向の両方を確認できた場合，ピーク値を返す
    if (peak_started && down_count > DOWN_THRESHOLD) return maximum;

    // 下降傾向を確認する前にTOP_THRESHOLD未満になった場合は，検出失敗とする
    if (value < TOP_THRESHOLD && peak_started) return 0;

    delay(DELAY_TIME);
  }
  return 0;  // timeout回数までにピークが見つからなかったら0を返す
}

// 脈拍を測定し返す関数
uint8_t rate() {
  uint16_t p1 = top();
  if (p1 == 0) return 0;
  uint32_t t1 = millis();

  uint16_t p2 = top();
  if (p2 == 0) return 0;
  uint32_t t2 = millis();

  if (t2 <= t1) return 0;

  uint32_t period = t2 - t1;
  float bpm = 60000.0 / period;

  return (uint8_t)(bpm + 0.5);
}
