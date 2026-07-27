---
category: camera-integration
tags: [milesight, sdk, camera, rtsp, lpr, channel, port]
severity: high
created: 2026-06-24
updated: 2026-06-24
project-origin: iPGSv4 (commit: add milesight camera)
---

# Tích Hợp SDK Milesight: Cấu Hình, Port, Channel

## Tình huống gặp phải

Tích hợp camera IP Milesight vào hệ thống iPGS để xem live stream và nhận sự kiện LPR. SDK Milesight dùng SDK riêng (không phải ONVIF thuần).

## Các điểm quan trọng khi tích hợp

### 1. Port và Channel dùng kiểu số (numeric), KHÔNG dùng string

```csharp
// SAI — dễ gây lỗi silent:
camera.Port = "554";
camera.Channel = "1";

// ĐÚNG — dùng int/numeric type:
camera.Port = 554;
camera.Channel = 1;
```

⚠️ UI input từ TextBox phải parse/validate trước khi gán:
```csharp
if (!int.TryParse(txtPort.Text, out int port))
{
    ShowError("Port phải là số nguyên");
    return;
}
camera.Port = port;
```

---

### 2. Cấu hình camera Milesight tối thiểu

```csharp
var config = new MilesightCameraConfig
{
    IpAddress = "192.168.1.100",
    Port = 80,          // HTTP port (default 80, không phải RTSP 554)
    Username = "admin",
    Password = "password",
    Channel = 1,        // 1-based index, không phải 0-based
    StreamType = StreamType.Main  // hoặc Sub
};
```

⚠️ **Port mặc định Milesight là 80 (HTTP API)**, không phải 554 (RTSP trực tiếp). RTSP URL build từ HTTP port.

---

### 3. RTSP URL format của Milesight

```
rtsp://{username}:{password}@{ip}:{rtsp_port}/main
rtsp://{username}:{password}@{ip}:{rtsp_port}/sub
```

RTSP port mặc định: **554** (riêng biệt với HTTP port 80).

Ví dụ: `rtsp://admin:password@192.168.1.100:554/main`

---

### 4. Chọn Zone / Channel trực tiếp từ UI

Khi có nhiều camera, cho phép chọn zone/channel trực tiếp khi config — không cần navigate màn hình khác:

```csharp
// Bind ComboBox với list channel
CbChannel.ItemsSource = Enumerable.Range(1, 16).ToList();
CbChannel.SelectedItem = config.Channel;

// Bind ComboBox với list zone
CbZone.ItemsSource = zoneService.GetAllZones();
CbZone.SelectedItem = CbZone.Items
    .Cast<ZoneModel>()
    .FirstOrDefault(z => z.Id == config.ZoneId);
```

---

### 5. Xử lý kết nối lại (reconnect)

```csharp
// Không để kết nối chết ngầm — phải có heartbeat hoặc timeout check
private async Task StartWithReconnect(CancellationToken ct)
{
    while (!ct.IsCancellationRequested)
    {
        try
        {
            await _camera.ConnectAsync();
            await _camera.StartStreamAsync();
            await WaitForDisconnectAsync(ct);
        }
        catch (Exception ex)
        {
            _logger.LogWarning("Camera disconnected: {msg}", ex.Message);
            await Task.Delay(5000, ct); // Chờ 5s rồi reconnect
        }
    }
}
```

---

## Áp dụng lại

- Khi config camera → dùng `int` cho port và channel, không dùng string
- Khi build RTSP URL → nhớ HTTP port ≠ RTSP port
- Khi thiết kế UI config → cho chọn zone ngay tại màn hình config, không navigate
- Khi stream bị đứt → implement reconnect loop với delay

## Chú ý / Cạm bẫy

- ⚠️ Channel Milesight bắt đầu từ **1**, không phải 0
- ⚠️ SDK có thể trả về NULL stream nếu channel sai — kiểm tra null trước khi render
- ⚠️ HTTP port và RTSP port là hai giá trị khác nhau — đừng nhầm
- ⚠️ Credentials phải URL-encode nếu có ký tự đặc biệt trong RTSP URL

## Tham chiếu

- Project: iPGSv4
- Commits liên quan: `add milesight camera`, `Use numeric port/channel and UI tweaks`, `Thêm chọn zone trực tiếp khi config camera`
