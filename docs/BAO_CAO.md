# Báo cáo Desk Buddy

Mỗi người viết phần mình phụ trách. Sơ đồ kiến trúc và bảng số đo viết chung, lấy từ một lần chạy thật.

## Chung

Desk Buddy là một node bàn học. ESP32 đọc DHT11, MQ135 và LDR, publish một JSON mỗi 5 giây. Python ghi lịch sử. Flask phục vụ dashboard và đẩy lệnh xuống node. Một node là đủ. Trường `nodeId` để dành khi nói hướng mở rộng.

```text
DHT11 + MQ135 + LDR -> ESP32 -> Mosquitto -> Python -> MongoDB hoặc file
Flask đọc kho -> React
React -> Flask -> Mosquitto -> ESP32 -> buzzer / LED
```

## Người 1. Tầng thiết bị và MQTT

- Linh kiện: ESP32, DHT11, MQ135, LDR, hai điện trở 10k, còi chủ động, LED và 220 ohm.
- DHT11 data GPIO 4, nguồn 3V3, pull-up 10k.
- MQ135 chân AO vào GPIO 34. LDR theo mạch 3V3 – LDR – GPIO 35 – 10k – GND. Cả hai là ADC1, 12 bit, suy hao 11 dB, vẫn đọc được khi Wi-Fi đã nối.
- Buzzer GPIO 25, LED GPIO 26.
- Publish `deskbuddy/node1/telemetry`, QoS 0, không retain. Subscribe `deskbuddy/node1/cmd`.
- `ts` lấy từ NTP, giờ UTC. Nếu NTP chưa xong thì dùng số giây từ lúc bật máy.
- Mất Wi-Fi hoặc broker thì vòng lặp nối lại, không chặn lệnh còi bằng `delay` dài giữa hai lần gửi.
- Lệnh `break` kêu ba nhịp. `buzzer` và `ms` kêu một nhịp. `led` giữ hoặc tắt đèn.

## Người 2. Lưu trữ

- Subscriber chỉ nhận đúng topic telemetry. Bản tin thiếu field, nhiệt độ ngoài −40..80°C, ẩm ngoài 0..100% hoặc ADC ngoài 0..4095 thì bỏ và in `rejected`.
- Bản ghi thêm `receivedAt` lúc máy bridge nhận, khác với `ts` trên node.
- Có `MONGO_URI` thì ghi MongoDB, collection có index `ts`, truy vấn `sort` và `limit` chứ không kéo cả collection. Không có URI thì ghi `data/telemetry.jsonl` để demo khi mất mạng.
- Chuỗi Atlas và mật khẩu Wi-Fi không để trong git. Mẫu biến môi trường là `.env.example`. Wi-Fi của board sửa trong `firmware/desk_buddy/config.h`.

## Người 3. API

- `GET /api/latest` trả mẫu mới nhất và cảnh báo của mẫu đó.
- `GET /api/history?limit=` mặc định 50, tối đa 500, thứ tự thời gian tăng dần để vẽ biểu đồ.
- `GET /api/alerts` trả cảnh báo đang hoạt động, tối đa 30 lần vượt ngưỡng gần đây, và bốn ngưỡng.
- Ngưỡng: nhiệt độ ≥ 32°C, ẩm ≥ 80%, khí ≥ 1800, sáng ≤ 400.
- `POST /api/commands` chỉ nhận `buzzer`, `led`, `break`, `ms`. Web không nói MQTT trực tiếp. Flask publish hộ lên topic lệnh. Broker chết thì API trả 503, đồng hồ trên web vẫn chạy.

## Người 4. Ứng dụng

- Ba trang: Bàn học, Cảnh báo, Nhắc nghỉ. Đã bỏ invoice, geography, team và dữ liệu mẫu của template.
- Bốn số hiện tại và bốn biểu đồ lịch sử, poll 3 giây.
- Pomodoro 25 phút tập trung và 5 phút nghỉ. Hết phiên tập trung thì gửi `{ "break": true }`.
- Khi API tắt, trang ghi lỗi thay vì giữ số giả.

## Kết quả đo

Điền sau một lần chạy với phần cứng thật:

| Lần | tempC | humidity | airRaw | lightRaw | Dashboard khớp MQTT |
| --- | ----- | -------- | ------ | -------- | ------------------- |
| 1   |       |          |        |          |                     |
| 2   |       |          |        |          |                     |
| 3   |       |          |        |          |                     |
