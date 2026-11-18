#include "myPulse.h"

void setup() {
  Serial.begin(115200);
  Serial.println("time,pulse");
}

void loop() {
  float t = millis() / 1000.0;
  if (t < 60.0) {
    uint8_t v = rate();
    if (v > 0) {
      Serial.print(t, 2);
      Serial.print(",");
      Serial.println(v);
    }
  }
}
