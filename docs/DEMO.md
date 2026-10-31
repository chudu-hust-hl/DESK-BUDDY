# Kịch bản demo một node

Chuẩn bị trước khi vào phòng:

- Điện thoại phát Wi-Fi. ESP32 và laptop cùng mạng đó.
- Mosquitto chạy trên laptop. `MQTT_HOST` trong `firmware/desk_buddy/config.h` là IP laptop.
- Một terminal chạy `python bridge/subscriber.py`.
- Một terminal chạy `python backend/app.py`.
- Trình duyệt mở dashboard cổng 3000.
- MQTT Explorer subscribe `deskbuddy/node1/#` để giảng viên nhìn thấy gói tin.

Thứ tự khoảng 5 phút:

1. Chỉ Serial của ESP32. Che DHT11 rồi mở ra, nhiệt độ và độ ẩm đổi trên dòng `tempC` / `humidity`. Nói rõ lát cắt đầu chỉ là cảm biến, chưa mạng.
2. Mở MQTT Explorer. Mỗi 5 giây có một JSON đúng hợp đồng trên `deskbuddy/node1/telemetry`. Subscriber in cùng bản tin và MongoDB hoặc `data/telemetry.jsonl` có thêm dòng.
3. Dashboard. Bốn ô và bốn biểu đồ đổi sau tối đa 3 giây. Che LDR theo mạch 3V3 – LDR – GPIO 35 – 10k – GND: số `lightRaw` giảm khi tối. Thổi gần MQ135: `airRaw` tăng. Nhắc đây là ADC tương đối, không phải ppm.
4. Vượt ngưỡng. Làm nóng, che sáng hoặc đưa `airRaw` qua 1800. Trang Cảnh báo hiện câu đang xảy ra. Ngưỡng nằm trong `shared/contract.json`.
5. Nhắc nghỉ. Bấm Thử còi trên trang Nhắc nghỉ. ESP32 kêu ba nhịp vì nhận `{"break": true}` trên `deskbuddy/node1/cmd`. Nếu broker tắt, web vẫn đếm giờ và báo không gửi được lệnh.

Điểm dễ gãy: Wi-Fi phòng lab chặn máy lạ, và ADC2 (GPIO 2, 12) đọc sai khi Wi-Fi bật. Demo dùng GPIO 34 và 35.
