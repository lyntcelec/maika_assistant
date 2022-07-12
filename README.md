# maika-assistant

[![OLLI|MAIKA](https://file.hstatic.net/200000264521/file/logo_1a5aee12000e4c38aebe7a155097c856.png)](https://olli.vn)

# Installation instructions

- Copy thư mục `custom_components/maika_assistant` vào `<your config dir>/custom_components/maika_assistant`

```
<config directory>/
|-- custom_components/
|   |-- maika_assistant/
|       |-- __init__.py
|       |-- connection.py
|       |-- const.py
|       |-- manifest.json
|       |-- etc...
```

- Restart Home Assistant để cập nhật component maika_assistant
- Mở app Maika chọn tính năng smart home và thực hiện account linking: `Quản lý tài khoản liên kết` -> `Kết Nối Tài Khoản Mới`-> trong mục `Chọn nhà cung cấp`, chọn `Home Assistant`

  <img src="images/IMG-0928.PNG" height="800em" />

- Trước khi bấm nút `Next` vui lòng copy `Key` như hình trên và chép vào `api_key` trong file `configuration.yaml` của Home Assistant như config bên dưới, sau đó restart Home Assistant để cập nhật config
- \*\*\* Lưu ý sau khi bấm `Next` nếu ở màn hình login xuất hiện lỗi `400 bad request` hãy thêm config `http ` như bên dưới, thực hiện lại bước `liên kết tài khoản` và lấy key mới nhất.
- url: hãy chép đường dẫn mà server của bạn đang hoạt động ở môi trường mạng nội bộ , có thể là localhost hoặc ip: http://localhost:8123 (hãy thử với trường hợp này trước), http://192.168.1.99:8123, https://192.168.1.99:8123.

### Cấu hình No SSL (HTTP)

```yaml
maika_assistant:
  project_id: "MAIKA"
  url: http://localhost:8123
  api_key: ac4d03d06de629a465a7fc53b7c1c734e04c3c729b3673e6326c0f354b49423771802938ad4191318d1f4df78a8990da
  report_state: true

http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.0/24
    - 127.0.0.1
    - ::1
```

### Cấu hình SSL (HTTPS)

```yaml
maika_assistant:
  project_id: "MAIKA"
  url: https://localhost:8123
  api_key: ac4d03d06de629a465a7fc53b7c1c734e04c3c729b3673e6326c0f354b49423771802938ad4191318d1f4df78a8990da
  report_state: true

http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.0/24
    - 127.0.0.1
    - ::1
```

- Quay lại app Maika bấm `Next` để kết thúc quá trình account linking

# Configuration

- Component này được viết từ google_assistant component, tham khảo config từ google_assistant bạn có thể expose domain hoặc entity theo nhu cầu.
- https://www.home-assistant.io/integrations/google_assistant

```
# Example configuration.yaml entry
maika_assistant:
  api_key: YOUR_KEY
  report_state: true
  exposed_domains:
    - switch
    - light
  entity_config:
    switch.kitchen:
      name: CUSTOM_NAME_FOR_MAIKA_ASSISTANT
      aliases:
        - BRIGHT_LIGHTS
        - ENTRY_LIGHTS
    light.living_room:
      expose: false
      room: LIVING_ROOM
```

# License

This project is under the MIT license.

# reference

https://www.home-assistant.io/integrations/google_assistant
