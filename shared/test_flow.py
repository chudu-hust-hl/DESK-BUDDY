import contextlib
import io
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
os.environ["MONGO_URI"] = ""
os.environ["DATA_FILE"] = str(Path(tempfile.mkdtemp()) / "telemetry.jsonl")

from shared.store import FileStore, open_store
from shared.telemetry import CONTRACT, alerts_for, normalize
from bridge.subscriber import handle

import backend.app as api


def test_normalize_rejects_bad_payloads():
    assert normalize({"tempC": 27}) is None
    assert normalize({"nodeId": "node1", "ts": 1, "tempC": 200, "humidity": 10, "airRaw": 1, "lightRaw": 1}) is None
    good = normalize(
        {"nodeId": "node1", "ts": 1710000000, "tempC": 27.4, "humidity": 61, "airRaw": 412, "lightRaw": 1800}
    )
    assert good["tempC"] == 27.4
    assert good["airRaw"] == 412


def test_store_and_api_roundtrip():
    store = open_store()
    assert isinstance(store, FileStore)
    store.insert(normalize({"nodeId": "node1", "ts": 100, "tempC": 27, "humidity": 50, "airRaw": 400, "lightRaw": 1500}))
    store.insert(normalize({"nodeId": "node1", "ts": 200, "tempC": 34, "humidity": 82, "airRaw": 2200, "lightRaw": 200}))
    api.store = store

    latest = api.app.test_client().get("/api/latest")
    body = latest.get_json()
    assert body["data"]["ts"] == 200
    codes = {item["code"] for item in body["alerts"]}
    assert codes == {"hot", "humid", "air", "dark"}

    history = api.app.test_client().get("/api/history?limit=1")
    assert history.get_json()["data"][0]["ts"] == 200

    alerts = api.app.test_client().get("/api/alerts")
    assert alerts.get_json()["active"]
    assert alerts.get_json()["thresholds"]["tempHighC"] == 32

    empty = api.app.test_client().post("/api/commands", json={})
    assert empty.status_code == 400
    assert alerts_for(None) == []

    printed = io.StringIO()
    message = SimpleNamespace(
        topic=CONTRACT["topics"]["telemetry"],
        payload=b'{"nodeId":"node1","ts":5,"tempC":27,"humidity":40,"airRaw":10,"lightRaw":1000}',
    )
    with contextlib.redirect_stdout(printed):
        handle(message, store)
    assert '"tempC": 27.0' in printed.getvalue()
    saved = [row for row in store.history(10) if row["ts"] == 5]
    assert saved and saved[0]["lightRaw"] == 1000


if __name__ == "__main__":
    test_normalize_rejects_bad_payloads()
    test_store_and_api_roundtrip()
    print("ok")
