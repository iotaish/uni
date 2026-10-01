#include "myPulse.h"  //myPulse.hをインクルードする

unsigned long start;

void setup() {
  Serial.begin(115200);  // シリアル通信の開始
  Serial.println("time,pulse");
  start = millis();
}

void loop() {
  if (millis() - start <= 60 * 1000) {
    uint8_t v = rate();
    float t = millis() / 1000.0;
    Serial.print(t, 3);
    Serial.print(",");
    Serial.println(v);
  }
}
