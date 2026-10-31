# Desk Buddy

Một node ESP32 đo môi trường bàn học, gửi một JSON qua MQTT, lưu lịch sử và hiện dashboard. Phạm vi bài tập lớn là cảm biến, giao thức và ứng dụng. Không gồm chatbot hay quản lý công việc.

Hợp đồng dùng chung nằm ở [shared/contract.json](shared/contract.json).

- Topic lên: `deskbuddy/node1/telemetry`
- Topic xuống: `deskbuddy/node1/cmd`
- Payload: `nodeId`, `ts`, `tempC`, `humidity`, `airRaw`, `lightRaw`
- Chân ADC1: MQ135 GPIO 34, LDR GPIO 35. DHT11 GPIO 4. Buzzer GPIO 25. LED GPIO 26.

`airRaw` và `lightRaw` là số ADC 0–4095. MQ135 không được hiệu thành ppm.

## Chạy trên máy

Cài Mosquitto, rồi:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r bridge/requirements.txt -r backend/requirements.txt
```

Ba tiến trình:

```bash
python bridge/subscriber.py
python backend/app.py
cd Frontend_Dashboard && npm install && npm start
```

Dashboard mở ở cổng 3000, API ở cổng 5000. Chưa có ESP32 thì phát mẫu bằng `python bridge/simulate.py`. Tắt simulate trước khi ESP32 publish, vì cả hai dùng cùng topic.

Không đặt `MONGO_URI` thì dữ liệu ghi vào `data/telemetry.jsonl`. Có chuỗi Atlas của nhóm thì export `MONGO_URI` trước khi chạy subscriber và API. Không commit chuỗi này.

Wi-Fi và broker của node sửa trong [firmware/desk_buddy/config.h](firmware/desk_buddy/config.h). Nạp [firmware/01_dht_serial/01_dht_serial.ino](firmware/01_dht_serial/01_dht_serial.ino) trước để thấy nhiệt độ trên Serial, rồi mới nạp [firmware/desk_buddy/desk_buddy.ino](firmware/desk_buddy/desk_buddy.ino).

Thư viện Arduino: DHT sensor library, PubSubClient.

Kịch bản demo và phần việc trong báo cáo: [docs/DEMO.md](docs/DEMO.md), [docs/BAO_CAO.md](docs/BAO_CAO.md).

Chỉ nạp sketch trong `firmware/`. Lần cắm đầu chỉ cần DHT11 trên GPIO 4. MQ135, LDR, còi và LED cắm sau.
