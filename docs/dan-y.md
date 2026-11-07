# Dàn ý thuyết trình Desk Buddy

Bám `docs/progress.tex`. Khoảng 8 phút. Đọc phần **Nói** khi đang đứng ở slide đó. Phần **Nếu được hỏi** để trả lời, không đọc hết.

Buổi này báo cáo bài toán, kiến trúc và lý do lựa chọn. Chưa demo đo trên board thật.

## 0:00 Trang bìa

**Nói.** Desk Buddy là đồ án môn IoT and Applications. Báo cáo tiến độ phần tìm hiểu và thiết kế: bài toán một bàn học, kiến trúc một node, và vì sao chọn từng công nghệ.

## 0:20 The problem

**Trên slide.** Heat, humidity, dim light, heavy air. Easy to miss until focus drops. Breaks are forgotten.

**Nói.** Người học ngồi lâu trong phòng kín. Bàn có thể nóng, ẩm, thiếu sáng hoặc không khí nặng, nhưng người ngồi chỉ nhận ra khi đã mất tập trung. Một việc nữa không phải cảm biến: ngồi quá lâu thì quên nghỉ.

**Kết quả mong muốn của bài toán.** Biết được tình trạng ngay tại bàn, và được nhắc khi đến lúc nghỉ.

## 1:20 Desk Buddy

**Trên slide.** One node for one study desk. Senses the desk. Sends one reading to the laptop. Shows live numbers and history. Beeps when a break is due.

**Nói.** Sản phẩm là một node để trên một bàn. Node đọc môi trường, gửi một bản tin lên laptop. Laptop lưu lịch sử và hiện số. Khi đến giờ nghỉ, laptop gửi lệnh xuống và node kêu còi.

**Hành vi.** Một bàn, một node. Không gom nhiều phòng, không chatbot, không lịch công việc.

## 2:10 Scope of this talk

**Trên slide.** One node `node1`. One JSON every 5 seconds. Sensors, MQTT, and a web page. Today: problem, architecture, and choices.

**Nói.** Phạm vi môn học là cảm biến, giao thức và trang web. Định danh node là `node1`. Mỗi 5 giây có đúng một JSON. Phần lắp mạch, nạp firmware và bảng số đo để buổi sau.

## 2:40 Overall architecture

**Trên slide.** Hàng Up và hàng Down. Dòng cuối: The browser talks to Flask only.

**Nói hàng Up.** DHT11, MQ135 và LDR vào ESP32. ESP32 publish lên Mosquitto. Subscriber nhận bản tin và ghi JSONL hoặc MongoDB.

**Nói hàng Down.** React chỉ gọi Flask. Flask publish lệnh lên cùng broker. ESP32 nhận lệnh rồi bật còi hoặc LED.

**Hành vi hai chiều.**

- Lên: `deskbuddy/node1/telemetry`, mỗi 5 giây, một JSON.
- Xuống: `deskbuddy/node1/cmd`, chỉ khi có lệnh nghỉ, còi hoặc LED.
- Trình duyệt không nối MQTT. Mất broker thì trang vẫn mở, lệnh trả lỗi vì chưa tới broker.

**Nếu được hỏi.** Subscriber bỏ bản tin thiếu field, nhiệt độ ngoài −40 đến 80°C, ẩm ngoài 0 đến 100%, hoặc ADC ngoài 0 đến 4095.

## 3:40 Message and thresholds

**Trên slide.** Bốn field. Ngưỡng 32°C, 80%, 1800, 400. ADC 0–4095, không ppm, không lux.

**Nói.** Bản tin có `nodeId`, `ts`, `tempC`, `humidity`, `airRaw`, `lightRaw`. Nhiệt và ẩm là số đo DHT11. Khí và sáng giữ số ADC. Số khí lớn hơn là không khí nặng hơn. Số sáng lớn hơn là bàn sáng hơn.

**Hành vi cảnh báo.**

- Nóng khi `tempC` từ 32°C.
- Ẩm khi `humidity` từ 80%.
- Khí khi `airRaw` từ 1800.
- Tối khi `lightRaw` từ 400 trở xuống.

**Kết quả mong muốn.** Nhìn một JSON là biết bàn đang ở trạng thái nào, và biết cảnh báo nào đang bật. Không đổi ADC sang ppm hay lux vì chưa hiệu chuẩn.

## 4:30 Choosing the board

**Trên slide.** Choice: ESP32. Why: Wi-Fi on the chip. ADC1 still reads while Wi-Fi is on. Alternative: Uno, ESP8266, Raspberry Pi. Chân 34 và 35.

**Nói.** Chọn ESP32 vì Wi-Fi nằm trên chip và vẫn đọc được ADC khi Wi-Fi bật. MQ135 vào GPIO 34, LDR vào GPIO 35. Hai chân này thuộc ADC1.

**Vì sao không chọn phương án kia.**

- Arduino Uno không có Wi-Fi sẵn. Muốn nối mạng phải thêm mạch.
- ESP8266 có Wi-Fi nhưng chỉ một lối ADC, trong khi bàn cần hai cảm biến tương tự cùng lúc.
- Raspberry Pi chạy được cả dashboard, nhưng thừa điện và không còn là một node cảm biến nhỏ.

**Hành vi trên board, khi đã nạp.** Đọc cảm biến, publish 5 giây một lần, subscribe lệnh. Mất Wi-Fi thì tự nối lại. Lệnh còi không bị một khoảng `delay` dài chặn giữa hai lần gửi.

## 5:20 Choosing the sensors

**Nói từng hàng, chỉ cột Choice và Why. Alternative nói một câu.**

- Nhiệt, ẩm: DHT11. Đủ để biết quá 32°C và quá 80%. DHT22 chính xác hơn, BME280 thêm áp suất và đi I2C. Bài này không cần mức đó.
- Khí: MQ135, lấy chân analog, giữ ADC. Cảm biến khí số ra ppm đắt hơn và cần hiệu chuẩn. Số lớn nghĩa là không khí nặng hơn.
- Sáng: LDR qua cầu chia áp, giữ ADC. Sáng hơn thì số lớn hơn. BH1750 ra lux bằng I2C, chính xác hơn nhưng thêm một kiểu bus.
- Nhắc trên bàn: còi chủ động và LED. Mức cao là bật. Còi thụ động phải phát xung.

**Hành vi lệnh, khi có board.**

- `break` kêu ba nhịp ngắn.
- `buzzer` cùng `ms` kêu một nhịp. `ms` từ 100 đến 10000.
- `led` bật hoặc tắt.

**Nếu được hỏi chân.** DHT11 dữ liệu GPIO 4, nguồn 3V3, kéo lên 10k. LDR theo mạch 3V3, LDR, GPIO 35, 10k, GND. Còi GPIO 25. LED GPIO 26 qua trở 220 ohm.

## 6:20 Choosing the software

**Nói.** Năm lớp. Cột đậm là thứ đã chọn.

- Giao thức: MQTT, hai topic. Một topic số đo đi lên, một topic lệnh đi xuống. HTTP buộc board mở server hoặc hỏi laptop liên tục. CoAP ít phù hợp với phần web của nhóm.
- Broker: Mosquitto trên laptop thuyết trình. Chạy trong lab, không cần tài khoản đám mây.
- Dịch vụ: subscriber ghi kho, Flask là API duy nhất. Board không ghi thẳng cơ sở dữ liệu. Web chỉ nói HTTP.
- Kho: tuần này ghi file `data/telemetry.jsonl`. Có chuỗi Atlas thì cùng chương trình ghi MongoDB, truy vấn theo thời gian. Chỉ MongoDB thì mất mạng là hết demo.
- Giao diện: React. Số hiện trên trình duyệt. Nhìn Serial chỉ đủ cho người nạp mạch.

**Hành vi trên laptop, đường đã chạy bằng giả lập.**

- `bridge/simulate.py` đóng vai ESP32, publish mỗi 5 giây.
- Subscriber in JSON và ghi thêm một dòng.
- API đọc kho: bản mới nhất, lịch sử, cảnh báo, và nhận lệnh.
- Dashboard hỏi API khoảng mỗi 3 giây.
- Tắt giả lập trước khi board thật publish, vì cả hai dùng cùng topic.

**Kết quả mong muốn của đường laptop.** Thấy một JSON đúng hợp đồng đi từ broker tới file và tới trang web, trước khi có mạch.

## 7:10 Where we are

**Nói.** Đã chốt hợp đồng: topic, field, ngưỡng. Đường laptop đã chạy với chương trình giả lập. Bước sau là nạp firmware, đọc cảm biến thật, và điền bảng số đo.

**Kết quả buổi này.** Người nghe nắm bài toán, sơ đồ hai chiều, và lý do ESP32, DHT11, MQ135, LDR, MQTT, Mosquitto, Flask, React.

**Chưa coi là kết quả.** Chưa có nhiệt độ thật trên Serial, chưa có ảnh khớp giữa MQTT và dashboard, chưa có tiếng còi trên board.

## 7:40 Summary

**Nói, rồi dừng.** Một node cho sự dễ chịu của bàn học và cho giờ nghỉ. Mạch là ESP32 với DHT11, MQ135 và LDR. Số đi qua MQTT trên laptop, Flask phục vụ React, lệnh đi ngược xuống còi và LED.

## Câu kết

Thank you. Sẵn sàng nhận câu hỏi về lý do chọn, về bản tin, hoặc về phần sẽ đo ở buổi sau.
