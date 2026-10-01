void setup() {
  Serial.begin(9600);  // シリアル通信の開始
  Serial.println("time,value");
}

void loop() {
  uint16_t v = analogRead(A0);  // アナログ入力を読み取る
  float t = millis() / 1000.0;

  Serial.print(t, 3);
  Serial.print(",");
  Serial.println(v);  // 読み取った値をシリアル出力

  delay(20);  // 次のループまで 20 ミリ秒待機
}
