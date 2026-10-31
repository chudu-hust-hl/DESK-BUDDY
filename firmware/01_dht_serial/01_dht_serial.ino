// Lát cắt 1: chỉ DHT11 ra Serial. Chưa Wi-Fi, chưa MQTT.
// Nạp file này trước để chắc cảm biến và chân GPIO 4 đã đúng.
// Library: DHT sensor library by Adafruit.

#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  Serial.println("DHT11 serial check. Waiting for the first sample...");
  delay(2000);
}

void loop() {
  float humidity = dht.readHumidity();
  float tempC = dht.readTemperature();

  if (isnan(humidity) || isnan(tempC)) {
    Serial.println("Failed to read DHT11");
  } else {
    Serial.print("tempC=");
    Serial.print(tempC, 1);
    Serial.print(" humidity=");
    Serial.println(humidity, 1);
  }
  delay(2000);
}
