import json
import os
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import paho.mqtt.client as mqtt

from shared.telemetry import CONTRACT


def sample(temp_c, humidity, air_raw, light_raw):
    return {
        "nodeId": CONTRACT["nodeId"],
        "ts": int(time.time()),
        "tempC": round(temp_c, 1),
        "humidity": round(humidity, 1),
        "airRaw": int(air_raw),
        "lightRaw": int(light_raw),
    }


def main():
    host = os.environ.get("MQTT_HOST", "127.0.0.1")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    topic = CONTRACT["topics"]["telemetry"]
    once = "--once" in sys.argv
    client = mqtt.Client()
    client.connect(host, port, 60)
    client.loop_start()
    temp_c = 27.0
    humidity = 60.0
    air_raw = 900
    light_raw = 1600
    print(f"publishing {host}:{port} {topic}")
    while True:
        temp_c = min(40, max(18, temp_c + random.uniform(-0.4, 0.4)))
        humidity = min(95, max(30, humidity + random.uniform(-1.0, 1.0)))
        air_raw = min(4095, max(200, air_raw + random.randint(-40, 40)))
        light_raw = min(4095, max(50, light_raw + random.randint(-30, 30)))
        if "--alert" in sys.argv:
            temp_c = 34.0
            air_raw = 2200
            light_raw = 200
        payload = sample(temp_c, humidity, air_raw, light_raw)
        client.publish(topic, json.dumps(payload))
        print(json.dumps(payload))
        if once:
            time.sleep(0.2)
            client.loop_stop()
            client.disconnect()
            return
        time.sleep(CONTRACT["intervalSeconds"])


if __name__ == "__main__":
    main()
