import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import paho.mqtt.client as mqtt

from shared.store import open_store
from shared.telemetry import CONTRACT, normalize


def handle(message, store):
    topic = CONTRACT["topics"]["telemetry"]
    if message.topic != topic:
        return
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print("rejected:", exc)
        return
    doc = normalize(payload)
    if doc is None:
        print("rejected:", payload)
        return
    print(json.dumps(doc, ensure_ascii=False))
    try:
        store.insert(doc)
    except Exception as exc:
        print("store failed:", exc)


def main():
    host = os.environ.get("MQTT_HOST", "127.0.0.1")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    topic = CONTRACT["topics"]["telemetry"]
    store = open_store()
    client = mqtt.Client()

    def on_message(client, userdata, message):
        handle(message, store)

    client.on_message = on_message
    client.connect(host, port, 60)
    client.subscribe(topic)
    print(f"listening {host}:{port} {topic}")
    client.loop_forever()


if __name__ == "__main__":
    main()
