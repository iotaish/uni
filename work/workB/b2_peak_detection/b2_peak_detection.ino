#include "myPulse.h"

void setup() {
  Serial.begin(115200);
  Serial.println("time,value,peak");
}

void loop() {
  float t = millis() / 1000.0;
  if (t < 5.0) {
    top();
  }
}
