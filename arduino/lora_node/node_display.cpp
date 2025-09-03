#include "node_display.h"
#include "node_battery.h"
#include <Wire.h>
#include <WiFi.h>
#include "LoraNode.h"
#include "version.h"

SSD1306Wire display(0x3c, SDA_OLED, SCL_OLED, GEOMETRY_128_64);
OLEDDisplayUi ui(&display);

#define VEXT GPIO_NUM_36

volatile int currentFrame = 0;
unsigned long lastFrameSwitch = 0;
const unsigned long frameSwitchInterval = 30000; // 30 seconden

void frame1(OLEDDisplay *display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
    display->setFont(ArialMT_Plain_16);
    display->drawString(x, y, WiFi.softAPSSID());
}

void frame2(OLEDDisplay *display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
    display->setFont(ArialMT_Plain_16);
    display->drawString(x, y, "Batterij " + String(Node_battery_percent()) + "%");
}

void frame3(OLEDDisplay *display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
    display->setFont(ArialMT_Plain_16);
    display->drawString(x, y, "nodes: " + String(LoraNode::getOnlineCount()) );
}

void frame4(OLEDDisplay *display, OLEDDisplayUiState* state, int16_t x, int16_t y) {
    display->setFont(ArialMT_Plain_16);
    display->drawString(x, y, "version: " + String(RELEASE_ID) );
}

FrameCallback frames[4] = { frame1, frame2, frame3, frame4 };

void overlay(OLEDDisplay *display, OLEDDisplayUiState* state) {
    int bat = Node_battery_percent();
    display->setFont(ArialMT_Plain_16);
    String ssid = WiFi.softAPSSID();
    //display->drawString(0, 0, ssid);
//    display->drawString(0, 0, String(bat) + "%");
}

void heltec_display_power(bool on) {
    if (on) {
      pinMode(RST_OLED, OUTPUT);
      digitalWrite(RST_OLED, HIGH);
      delay(1);
      digitalWrite(RST_OLED, LOW);
      delay(20);
      digitalWrite(RST_OLED, HIGH);
    } else {
      display.displayOff();
    }
}

void Node_display_setup() {
    battery_init();

    pinMode(VEXT, OUTPUT);
    digitalWrite(VEXT, LOW);  // ✅ laag = OLED krijgt stroom
    delay(10);

    heltec_display_power(true);

    display.setContrast(255);
    display.flipScreenVertically();

    display.init();
    display.clear();
    display.setContrast(255);

    display.setTextAlignment(TEXT_ALIGN_LEFT);
//    display.setFont(ArialMT_Plain_16);
//    display.drawString(0, 16, "Battery: " + String(Node_battery_percent()) + "%");

    ui.setTargetFPS(30);
    ui.setFrames(frames, 4);
    ui.setOverlays(new OverlayCallback[1]{ overlay }, 1);
    ui.init();
}

void Node_display_update() {
    int remainingTimeBudget = ui.update();

    // Iedere 30 seconden naar volgende frame
    unsigned long now = millis();
    if (now - lastFrameSwitch > frameSwitchInterval) {
        currentFrame = (currentFrame + 1) % 4; // aantal frames
        ui.switchToFrame(currentFrame);
        lastFrameSwitch = now;
    }
}
