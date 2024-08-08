#include <HID-Project.h>

const uint8_t reportId = 1;
const size_t reportSize = 64;
uint8_t reportBuffer[reportSize];

void setup() {
  RawHID.begin(reportBuffer, reportSize);
}

void loop() {
  if (RawHID.available() > 0) {
    if (RawHID.read() > 0) {
      BootKeyboard.begin();
      BootKeyboard.press('o');
      BootKeyboard.release('o');
      BootKeyboard.end();
    }
  }
}