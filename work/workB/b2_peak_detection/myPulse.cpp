#include "myPulse.h"

#define PIN_IN A0      // アナログ入力PINの設定
#define DELAY_TIME 20  // ディレイ時間(ms)の設定

#define TOP_THRESHOLD 0   // 信号が山の部分にあるかの判定に利用する閾値
#define DOWN_THRESHOLD 0  // 下降傾向にあるかの判定に利用する閾値
#define UP_THRESHOLD 1    // 上昇傾向にあるかの判定に利用する閾値

uint16_t top() {
  uint32_t times[256];
  uint16_t values[256];
  uint8_t count = 0;
  int16_t peak_index = -1;  // -1は配列にピークがないことを示す

  uint16_t maximum = 0;
  uint8_t up_count = 0;    // 連続で閾値を超えて上昇傾向を示した回数
  uint8_t down_count = 0;  // 連続で閾値以上で下降傾向を示した回数
  uint8_t timeout = 255;
  bool peak_started = false;
  uint16_t result = 0;

  while (timeout--) {
    uint16_t value = analogRead(PIN_IN);
    uint32_t time = millis();

    // 配列にappend
    values[count] = value;
    times[count] = time;

    // up_countがUP_THRESHOLDより大きい場合，上昇傾向にあると判定する
    if (value >= TOP_THRESHOLD) {
      if (value > maximum) {
        maximum = value;
        up_count++;
        down_count = 0;
        peak_index = count;
      } else {
        down_count++;
      }
    }

    // peakの開始の判定、UP_THRESHOLD+1連続
    if (up_count > UP_THRESHOLD) peak_started = true;

    // TOP_THRESHOLD未満になり，上昇傾向と判定されていない場合は，次の山を探し直す
    if (value < TOP_THRESHOLD && !peak_started) {
      maximum = 0;
      up_count = 0;
      down_count = 0;
      peak_index = -1;
    }

    count++;

    // ここから終了判定をする

    // 上昇傾向と下降傾向の両方を確認できた場合，ピーク値を返す
    if (peak_started && down_count > DOWN_THRESHOLD) {
      result = maximum;
      break;
    }

    // 下降傾向を確認する前にTOP_THRESHOLD未満になった場合は，検出失敗とする
    if (value < TOP_THRESHOLD && peak_started) {
      result = 0;
      peak_index = -1;
      break;
    }

    delay(DELAY_TIME);
  }

  for (uint8_t i = 0; i < count; i++) {
    Serial.print(times[i] / 1000.0, 2);
    Serial.print(",");
    Serial.print(values[i]);
    Serial.print(",");
    Serial.println(result != 0 && i == peak_index ? 1 : 0);
  }

  return result;
}
