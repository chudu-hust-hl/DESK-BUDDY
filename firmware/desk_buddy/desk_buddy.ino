// Desk Buddy node.
// Libraries: DHT sensor library (Adafruit), PubSubClient.
// Contract: shared/contract.json
//   publish deskbuddy/node1/telemetry
//   subscribe deskbuddy/node1/cmd
// ADC1 pins stay readable while Wi-Fi is connected. Do not move MQ135 or LDR to GPIO 2 or 12.

#include <WiFi.h>
#include <PubSubClient.h>
#include <time.h>
#include "DHT.h"
#include "config.h"

#define DHTPIN 4
#define DHTTYPE DHT11
#define MQ135_PIN 34
#define LDR_PIN 35
#define BUZZER_PIN 25
#define LED_PIN 26

#define TELEMETRY_TOPIC "deskbuddy/node1/telemetry"
#define COMMAND_TOPIC "deskbuddy/node1/cmd"
#define PUBLISH_MS 5000

DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

unsigned long lastPublish = 0;
unsigned long buzzerUntil = 0;
bool breakActive = false;
int breakStep = 0;
unsigned long breakNext = 0;

const int BREAK_STEPS[] = {120, 100, 120, 100, 200, 150};
const int BREAK_STEP_COUNT = 6;

void serviceActuators() {
  unsigned long now = millis();
  if (breakActive) {
    if (now < breakNext) {
      return;
    }
    bool on = (breakStep % 2) == 0;
    digitalWrite(BUZZER_PIN, on ? HIGH : LOW);
    breakNext = now + BREAK_STEPS[breakStep];
    breakStep++;
    if (breakStep >= BREAK_STEP_COUNT) {
      breakActive = false;
      digitalWrite(BUZZER_PIN, LOW);
    }
    return;
  }
  if (buzzerUntil != 0 && now >= buzzerUntil) {
    digitalWrite(BUZZER_PIN, LOW);
    buzzerUntil = 0;
  }
}

void startBreak() {
  breakActive = true;
  breakStep = 0;
  breakNext = millis();
  buzzerUntil = 0;
}

int commandMs(const char* json) {
  const char* mark = strstr(json, "\"ms\"");
  if (!mark) {
    return 800;
  }
  const char* colon = strchr(mark, ':');
  if (!colon) {
    return 800;
  }
  int value = atoi(colon + 1);
  if (value < 100) {
    return 100;
  }
  if (value > 10000) {
    return 10000;
  }
  return value;
}

bool hasFlag(const char* json, const char* key, bool value) {
  char pattern[32];
  snprintf(pattern, sizeof(pattern), "\"%s\":%s", key, value ? "true" : "false");
  if (strstr(json, pattern)) {
    return true;
  }
  snprintf(pattern, sizeof(pattern), "\"%s\": %s", key, value ? "true" : "false");
  return strstr(json, pattern) != nullptr;
}

void handleCommand(const char* json) {
  Serial.print("cmd ");
  Serial.println(json);
  if (hasFlag(json, "break", true)) {
    startBreak();
    return;
  }
  if (hasFlag(json, "buzzer", true)) {
    breakActive = false;
    digitalWrite(BUZZER_PIN, HIGH);
    buzzerUntil = millis() + commandMs(json);
  } else if (hasFlag(json, "buzzer", false)) {
    breakActive = false;
    buzzerUntil = 0;
    digitalWrite(BUZZER_PIN, LOW);
  }
  if (hasFlag(json, "led", true)) {
    digitalWrite(LED_PIN, HIGH);
  } else if (hasFlag(json, "led", false)) {
    digitalWrite(LED_PIN, LOW);
  }
}

void onMqtt(char* topic, byte* payload, unsigned int length) {
  char body[192];
  if (length >= sizeof(body)) {
    length = sizeof(body) - 1;
  }
  memcpy(body, payload, length);
  body[length] = 0;
  handleCommand(body);
}

void connectWifi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  Serial.print("Wi-Fi ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 40) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi failed, retry on next loop");
  }
}

void syncClock() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  for (int i = 0; i < 20; i++) {
    if (time(nullptr) > 1700000000) {
      Serial.println("NTP ok");
      return;
    }
    delay(250);
  }
  Serial.println("NTP not ready, ts will fall back to uptime");
}

void connectMqtt() {
  if (mqtt.connected() || WiFi.status() != WL_CONNECTED) {
    return;
  }
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqtt);
  Serial.print("MQTT ");
  Serial.println(MQTT_HOST);
  if (mqtt.connect("deskbuddy-node1")) {
    mqtt.subscribe(COMMAND_TOPIC);
    Serial.println("MQTT connected");
  } else {
    Serial.print("MQTT failed rc=");
    Serial.println(mqtt.state());
  }
}

unsigned long currentTs() {
  time_t now = time(nullptr);
  if (now > 1700000000) {
    return (unsigned long)now;
  }
  return millis() / 1000;
}

void publishTelemetry() {
  float humidity = dht.readHumidity();
  float tempC = dht.readTemperature();
  int airRaw = analogRead(MQ135_PIN);
  int lightRaw = analogRead(LDR_PIN);

  Serial.print("airRaw=");
  Serial.print(airRaw);
  Serial.print(" lightRaw=");
  Serial.println(lightRaw);

  if (isnan(humidity) || isnan(tempC)) {
    Serial.println("Skip publish: DHT11 read failed");
    return;
  }
  Serial.print("tempC=");
  Serial.print(tempC, 1);
  Serial.print(" humidity=");
  Serial.println(humidity, 1);

  char body[192];
  snprintf(
    body,
    sizeof(body),
    "{\"nodeId\":\"%s\",\"ts\":%lu,\"tempC\":%.1f,\"humidity\":%.1f,\"airRaw\":%d,\"lightRaw\":%d}",
    NODE_ID,
    currentTs(),
    tempC,
    humidity,
    airRaw,
    lightRaw
  );
  Serial.println(body);
  if (!mqtt.connected()) {
    return;
  }
  mqtt.publish(TELEMETRY_TOPIC, body);
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  analogReadResolution(12);
  analogSetPinAttenuation(MQ135_PIN, ADC_11db);
  analogSetPinAttenuation(LDR_PIN, ADC_11db);
  delay(2000);
  connectWifi();
  if (WiFi.status() == WL_CONNECTED) {
    syncClock();
  }
  connectMqtt();
}

void loop() {
  connectWifi();
  connectMqtt();
  mqtt.loop();
  serviceActuators();
  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;
    publishTelemetry();
  }
}
