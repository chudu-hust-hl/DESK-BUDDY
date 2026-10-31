import json
import os
from pathlib import Path

from shared.telemetry import ROOT


class FileStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def insert(self, doc):
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(doc) + "\n")
        self._trim(2000)

    def latest(self):
        rows = self._read()
        if not rows:
            return None
        return max(rows, key=lambda row: row["ts"])

    def history(self, limit):
        rows = sorted(self._read(), key=lambda row: row["ts"])
        return rows[-limit:]

    def _read(self):
        rows = []
        if not self.path.exists():
            return rows
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    def _trim(self, keep):
        rows = self._read()
        if len(rows) <= keep:
            return
        kept = rows[-keep:]
        text = "".join(json.dumps(row) + "\n" for row in kept)
        self.path.write_text(text, encoding="utf-8")


class MongoStore:
    def __init__(self, uri, database, collection):
        from pymongo import MongoClient

        self.client = MongoClient(uri, serverSelectionTimeoutMS=4000)
        self.col = self.client[database][collection]
        self.col.create_index("ts")

    def insert(self, doc):
        self.col.insert_one(dict(doc))

    def latest(self):
        return self.col.find_one({}, {"_id": 0}, sort=[("ts", -1)])

    def history(self, limit):
        cursor = self.col.find({}, {"_id": 0}).sort("ts", -1).limit(limit)
        rows = list(cursor)
        rows.reverse()
        return rows


def open_store():
    uri = os.environ.get("MONGO_URI", "").strip()
    if uri:
        database = os.environ.get("MONGO_DB", "sensor")
        collection = os.environ.get("MONGO_COLLECTION", "telemetry")
        return MongoStore(uri, database, collection)
    path = os.environ.get("DATA_FILE", str(ROOT / "data" / "telemetry.jsonl"))
    return FileStore(path)
