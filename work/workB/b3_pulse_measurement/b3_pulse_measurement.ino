#include "myPulse.h"  //myPulse.hをインクルードする

unsigned long start;

void setup() {
  Serial.begin(115200);  // シリアル通信の開始
  Serial.println("time,pulse");
  start = millis() / 1000.0;
}

void loop() {
  float t = millis() / 1000.0;
  if (t - start <= 60) {
    uint8_t v = rate();
    Serial.print(t, 3);
    Serial.print(",");
    Serial.println(v);
  }
}
