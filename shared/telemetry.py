import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = json.loads((ROOT / "shared" / "contract.json").read_text())

REQUIRED = ("nodeId", "ts", "tempC", "humidity", "airRaw", "lightRaw")


def normalize(payload):
    if not isinstance(payload, dict):
        return None
    if any(key not in payload for key in REQUIRED):
        return None
    try:
        doc = {
            "nodeId": str(payload["nodeId"]).strip(),
            "ts": int(payload["ts"]),
            "tempC": round(float(payload["tempC"]), 1),
            "humidity": round(float(payload["humidity"]), 1),
            "airRaw": int(payload["airRaw"]),
            "lightRaw": int(payload["lightRaw"]),
            "receivedAt": datetime.now(timezone.utc).isoformat(),
        }
    except (TypeError, ValueError):
        return None
    if not doc["nodeId"]:
        return None
    if not -40 <= doc["tempC"] <= 80:
        return None
    if not 0 <= doc["humidity"] <= 100:
        return None
    if not 0 <= doc["airRaw"] <= 4095 or not 0 <= doc["lightRaw"] <= 4095:
        return None
    return doc


def alerts_for(doc):
    if not doc:
        return []
    limits = CONTRACT["thresholds"]
    found = []
    if doc["tempC"] >= limits["tempHighC"]:
        found.append(
            {
                "code": "hot",
                "field": "tempC",
                "value": doc["tempC"],
                "threshold": limits["tempHighC"],
                "message": "Nhiệt độ bàn cao. Nên nghỉ hoặc làm mát chỗ ngồi.",
            }
        )
    if doc["humidity"] >= limits["humidityHigh"]:
        found.append(
            {
                "code": "humid",
                "field": "humidity",
                "value": doc["humidity"],
                "threshold": limits["humidityHigh"],
                "message": "Độ ẩm cao so với ngưỡng đã chốt.",
            }
        )
    if doc["airRaw"] >= limits["airHighRaw"]:
        found.append(
            {
                "code": "air",
                "field": "airRaw",
                "value": doc["airRaw"],
                "threshold": limits["airHighRaw"],
                "message": "Chất lượng không khí kém. Chỉ số ADC tương đối, không phải ppm.",
            }
        )
    if doc["lightRaw"] <= limits["lightLowRaw"]:
        found.append(
            {
                "code": "dark",
                "field": "lightRaw",
                "value": doc["lightRaw"],
                "threshold": limits["lightLowRaw"],
                "message": "Bàn đang tối. Bật đèn để giữ tập trung.",
            }
        )
    return found


def clamp_limit(raw, default=50, upper=500):
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = default
    return max(1, min(value, upper))
