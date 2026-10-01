#include "myPulse.h"  //myPulse.hをインクルードする

unsigned long start;

void setup() {
  Serial.begin(115200);  // シリアル通信の開始
  Serial.println("time,value,peak");
  start = millis() / 1000.0;
}

void loop() {
  float t = millis() / 1000.0;
  if (t - start <= 5) {
    uint16_t v = analogRead(A0);  // アナログ入力を読み取る
    uint16_t u = top() != 0 ? 1 : 0;

    Serial.print(t, 3);
    Serial.print(",");
    Serial.print(v);  // 読み取った値をシリアル出力
    Serial.print(",");
    Serial.println(u);  // ピーク検出の有無をシリアル出
  }
}
