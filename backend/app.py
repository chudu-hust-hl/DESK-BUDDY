import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import paho.mqtt.client as mqtt
from flask import Flask, request
from flask_cors import CORS

from shared.store import open_store
from shared.telemetry import CONTRACT, alerts_for, clamp_limit

app = Flask(__name__)
CORS(app)
store = open_store()


def publish_command(command):
    host = os.environ.get("MQTT_HOST", "127.0.0.1")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    topic = CONTRACT["topics"]["command"]
    client = mqtt.Client()
    client.connect(host, port, 10)
    client.publish(topic, json.dumps(command))
    client.disconnect()
    return topic


def clean_command(body):
    if not isinstance(body, dict):
        return None
    command = {}
    if "buzzer" in body:
        command["buzzer"] = bool(body["buzzer"])
    if "led" in body:
        command["led"] = bool(body["led"])
    if "break" in body:
        command["break"] = bool(body["break"])
    if "ms" in body:
        command["ms"] = clamp_limit(body["ms"], default=800, upper=10000)
        if command["ms"] < 100:
            command["ms"] = 100
    if not any(key in command for key in ("buzzer", "led", "break")):
        return None
    return command


@app.get("/api/health")
def health():
    return {"ok": True, "nodeId": CONTRACT["nodeId"], "topics": CONTRACT["topics"]}


@app.get("/api/latest")
def latest():
    doc = store.latest()
    return {"data": doc, "alerts": alerts_for(doc)}


@app.get("/api/history")
def history():
    limit = clamp_limit(request.args.get("limit"), default=50, upper=500)
    return {"data": store.history(limit)}


@app.get("/api/alerts")
def alerts():
    latest_doc = store.latest()
    recent = []
    for row in store.history(100):
        for alert in alerts_for(row):
            recent.append({**alert, "ts": row["ts"], "nodeId": row["nodeId"]})
    recent = recent[-30:]
    recent.reverse()
    return {
        "active": alerts_for(latest_doc),
        "recent": recent,
        "thresholds": CONTRACT["thresholds"],
    }


@app.post("/api/commands")
def commands():
    command = clean_command(request.get_json(silent=True))
    if command is None:
        return {"error": "Lệnh cần buzzer, led hoặc break."}, 400
    try:
        topic = publish_command(command)
    except Exception as exc:
        return {"error": f"Không tới được MQTT broker: {exc}"}, 503
    return {"ok": True, "topic": topic, "command": command}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
