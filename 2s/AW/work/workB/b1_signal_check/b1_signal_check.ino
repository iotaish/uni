void setup() {
  Serial.begin(9600);
  Serial.println("time,value");
}

void loop() {
  float t = millis() / 1000.0;
  if (t < 5.0) {
    uint16_t v = analogRead(A0);

    Serial.print(t, 2);
    Serial.print(",");
    Serial.println(v);

    delay(20);
  }
}
