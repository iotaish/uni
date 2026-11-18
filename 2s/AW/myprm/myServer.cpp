#include "myServer.h"

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;
WiFiServer server(80);

void initServer() {
  // IPアドレスの設定 (学籍番号下3桁: 192.168.12.2)
  WiFi.config(IPAddress(192, 168, STUDENT_ID, 2));

  // アクセスポイントの開始
  if (WiFi.beginAP(ssid, pass) != WL_AP_LISTENING) {
    Serial.println("Failed to start access point");
    while (true)
      ;
  }

  // サーバーの開始
  server.begin();
  Serial.println("Server started");
}

void handleClientRequest(double sensorValue) {
  WiFiClient client = server.available();  // クライアントの接続を待つ
  if (client) {
    String body = "{\"value\": " + String(sensorValue, 2) + "}";
    String currentLine = "";
    unsigned long startTime = millis();

    // リクエストが届かないまま1秒経過したら打ち切る (ブラウザの先読み接続対策)
    while (client.connected() && millis() - startTime < 1000) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);  // 受信したデータをシリアルモニタに出力
        if (c == '\n') {
          if (currentLine.length() == 0) {
            // HTTPヘッダを送信
            client.println("HTTP/1.1 200 OK");
            client.println("Content-Type: application/json");
            client.println("Content-Length: " + String(body.length()));
            client.println("Connection: close");
            client.println();

            // JSONデータを送信
            client.print(body);
            client.flush();  // 送信が完了するのを待ってから切断する
            break;
          } else {
            // 改行を受信したらcurrentLineをリセット
            currentLine = "";
          }
        } else if (c != '\r') {
          // キャリッジリターン以外の文字をcurrentLineに追加
          currentLine += c;
        }
      }
    }
    client.stop();  // クライアントとの接続を終了
  }
}
