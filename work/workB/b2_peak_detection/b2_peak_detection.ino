#include "myPulse.h"  //myPulse.hをインクルードする

void setup() {
  Serial.begin(115200);  // シリアル通信の開始
  Serial.println("time,value,peak");
}

void loop() {
  top();  // myPulse.hのtop関数を呼び出しを繰り返す
}
