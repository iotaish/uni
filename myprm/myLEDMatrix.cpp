#include "myLEDMatrix.h"

ArduinoLEDMatrix matrix;
int c, r;

byte frame[8][12] = {
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}};

byte digits[5][30]{
    {1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
    {1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1,
     1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1},
    {1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
     1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1},
    {1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1,
     0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1},
    {1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1,
     1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1},
};

void initLEDMatrix() {
  matrix.begin();
}

void displayDigit(int d, int s_r, int s_c) {
  for (int r = 0; r < 5; r++) {
    for (int c = 0; c < 3; c++) {
      frame[s_r + r][s_c + c] = digits[r][d * 3 + c];
    }
  }
  matrix.renderBitmap(frame, 8, 12);
}

void updateDisplay(int v) {
  displayDigit(v % 10, 2, 9);
  displayDigit((v / 10) % 10, 2, 5);
  displayDigit((v / 100) % 10, 2, 1);
}

void displayDigitC1(int d, int s_r, int s_c) {
  for (int r = 0; r < 5; r++) {
    for (int c = 0; c < 3; c++) {
      frame[s_r + r][s_c + c] = digits[r][d * 3 + c];
    }
  }
  frame[7][4] = 1;  // 小数点の表示
  matrix.renderBitmap(frame, 8, 12);
}

void updateDisplayC1(double v) {
  displayDigitC1(int(v * 100) % 10, 2, 9);
  displayDigitC1((int(v * 100) / 10) % 10, 2, 5);
  displayDigitC1((int(v * 100) / 100) % 10, 2, 1);
}
