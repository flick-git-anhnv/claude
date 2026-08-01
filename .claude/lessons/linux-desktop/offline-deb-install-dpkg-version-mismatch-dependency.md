---
category: linux-desktop
tags: [dpkg, offline-install, dependency, apt, version-pinning]
severity: medium
created: 2026-07-31
updated: 2026-07-31
project-origin: 6.RemoteControlTool (Kiosk Deploy — cài curl offline qua dpkg -i)
---

# `dpkg -i` gói .deb offline fail nếu dependency trên máy đích lệch version so với lúc tải

## Tình huống gặp phải

Kiosk Deploy cài `curl` offline bằng cách nhúng sẵn 1 file `curl_amd64.deb` (tải 1 lần từ
`security.ubuntu.com`) vào `CcuUI/Resources/kiosk-deb/`, cài bằng `dpkg -i` trên máy ZCU đích
(không cần apt/mạng).

## Triệu chứng / Lỗi

Deploy báo lỗi `1-install-software.sh thất bại (exit 1)`. Log trông như đã cài THÀNH CÔNG
("Unpacking curl ... Processing triggers for man-db ...") nhưng vẫn exit 1. Chạy tay
`dpkg -i curl_amd64.deb` lại mới thấy rõ:

```
dpkg: dependency problems prevent configuration of curl:
 curl depends on libcurl4 (= 7.81.0-1ubuntu1.25); however:
  Version of libcurl4:amd64 on system is 7.81.0-1ubuntu1.7.
dpkg: error processing package curl (--install):
 dependency problems - leaving unconfigured
```

`dpkg -l curl` cho thấy status `iU` (Unpacked, chưa Configured) thay vì `ii` (đã cài đủ).

## Nguyên nhân gốc rễ (Root Cause)

`dpkg -i` (khác `apt install`) **KHÔNG tự resolve/tải dependency** — nó chỉ cài đúng file
.deb được chỉ định. Gói `curl_amd64.deb` tôi tải tại 1 THỜI ĐIỂM cụ thể yêu cầu `libcurl4`
đúng version `7.81.0-1ubuntu1.25` (bản patch security mới nhất tại lúc tải). Nếu máy đích
đã cài `libcurl4` từ TRƯỚC ở version cũ hơn (chưa update, VD `...1.7`) — dpkg unpack file
curl xong nhưng KHÔNG cấu hình được vì ràng buộc version `(= x.y.z)` không khớp.

## Giải pháp

Nhúng kèm **đúng version `libcurl4`** cùng lúc với `curl`, cài CẢ HAI trong 1 lệnh
`dpkg -i` (dpkg tự resolve version giữa các file truyền cùng lúc, không cần internet):

```bash
_sudo dpkg -i curl_amd64.deb libcurl4_amd64.deb
```

Kèm fallback: sau `dpkg -i`, kiểm tra `dpkg -s $pkg | grep "^Status: install ok installed"`
— nếu chưa "ii", thử `apt-get install -f -y` (best-effort, cần mạng) thay vì để deploy
fail cứng không rõ nguyên nhân.

## Áp dụng lại (How to reuse)

- Khi nhúng bất kỳ gói .deb nào để cài OFFLINE qua `dpkg -i` (không phải `apt install ./x.deb`
  — cách đó vẫn cần apt/network để resolve dep): PHẢI kiểm tra gói đó có dependency version-pin
  chặt (`= x.y.z`) không bằng `dpkg -I file.deb | grep Depends`, và nhúng kèm TẤT CẢ dependency
  bị pin version đó, không chỉ nhúng 1 file duy nhất.
- Log "trông như thành công" (unpacking, processing triggers) nhưng vẫn `exit 1` ở dpkg —
  luôn đọc kỹ dòng cuối cùng thật sự ("dependency problems... leaving unconfigured"), đừng
  tin vào các dòng log ở giữa.
- `dpkg -l <pkg>` cột đầu tiên (`iU` vs `ii`) là cách nhanh nhất xác nhận gói đã cấu hình
  xong thật hay chỉ mới unpack dở dang.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ File .deb tải 1 lần rồi nhúng cố định vào repo sẽ dần LỖI THỜI khi Ubuntu phát hành
  security patch mới cho dependency — máy đích được update qua apt bình thường (có mạng)
  sẽ có version mới hơn file nhúng cũ, KHÔNG PHẢI luôn khớp. Nên định kỳ refresh lại các
  file .deb nhúng offline, không coi là "tải 1 lần dùng mãi".
- ⚠️ Fallback `apt-get install -f -y` chỉ cứu được nếu máy đích CÓ mạng — máy thật sự air-gapped
  vẫn sẽ fail, cần nhúng đúng bộ dependency ngay từ đầu.

## Tham chiếu

- Project liên quan: `6.RemoteControlTool` — `scripts/linux-kiosk/1-install-software.sh` (F26)
