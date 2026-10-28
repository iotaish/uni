#include "myLEDMatrix.h"

int analogValue = 0;
double measuredVoltage = 0.0;

void setup() {
  initLEDMatrix();
}

void loop() {
  analogValue = analogRead(A0);
  // A0ピンのAD変換値 (0〜1023) を電圧値 (0.0〜5.0V) に変換
  measuredVoltage = (double)analogValue / 1023.0 * 5.0;
  updateDisplayC1(measuredVoltage);
  delay(100);
}
