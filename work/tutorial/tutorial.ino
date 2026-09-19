const int outputPin = 4;    // デジタル出⼒ピンの設定
const int threshold = 400;  // アナログ⼊⼒の閾値

void setup() {
  Serial.begin(9600);          // シリアル通信の開始
  pinMode(outputPin, OUTPUT);  // 出⼒ピンのモード設定
}

void loop() {
  uint16_t v = analogRead(A0);  // アナログ⼊⼒を読み取る
  Serial.println(v);            // 読み取った値をシリアルモニタに出⼒
  if (v > threshold) {  // アナログ⼊⼒の値が閾値を超えるかどうかで出⼒を制御
    digitalWrite(outputPin, HIGH);
  } else {
    digitalWrite(outputPin, LOW);
  }
  delay(50);  // 次のループまで 50 ミリ秒待機
}
