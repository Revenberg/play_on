#include <Arduino.h>
#include "rpi4.h"
#include "version.h"
#include "LoraNode.h"

void RPI4::setup() {
    Serial.begin(115200);
    delay(200);
    Serial.println("[RPI4] Setup complete");
  Serial.println(String("[RPI4] RELEASE_ID: ") + RELEASE_ID);
}

void RPI4::loop() {
  // Ook USB berichten van de Pi lezen
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    Serial.print("RPi stuurde: ");
    Serial.println(msg);

    LoraNode::handlePacket(msg);
  }
}