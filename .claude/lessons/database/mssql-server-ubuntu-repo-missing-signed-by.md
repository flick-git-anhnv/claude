---
category: database
tags: [mssql-server, ubuntu, apt, gpg, signed-by, linux-install]
severity: medium
created: 2026-07-28
updated: 2026-07-28
project-origin: iPGSv4 CCU (Ubuntu VM deployment)
---

# Cài SQL Server / mssql-tools trên Ubuntu qua repo Microsoft báo lỗi NO_PUBKEY dù đã import key đúng

## Tình huống gặp phải

Cài SQL Server Express trên Ubuntu 22.04 (VM VirtualBox) theo đúng hướng dẫn chính thức của Microsoft: tải GPG key về, `gpg --dearmor` ra `/usr/share/keyrings/microsoft-prod.gpg`, rồi tải file `.list` repo trực tiếp từ Microsoft (`curl -o .../mssql-server.list https://packages.microsoft.com/config/ubuntu/22.04/mssql-server-2022.list`, và tương tự cho `mssql-release.list` khi cài `mssql-tools18`).

## Triệu chứng / Lỗi

```
Err:2 https://packages.microsoft.com/ubuntu/22.04/mssql-server-2022 jammy InRelease
  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY EB3E94ADBE1229CF
E: The repository '...' is not signed.
```

Lỗi xảy ra **dù đã `gpg --dearmor` đúng key vào đúng path** — dễ nhầm tưởng là key tải sai hoặc key hỏng.

## Nguyên nhân gốc rễ (Root Cause)

File `.list` mà Microsoft cung cấp qua URL `packages.microsoft.com/config/ubuntu/22.04/*.list` trả về nội dung **không có tham số `signed-by`**, ví dụ:
```
deb [arch=amd64,arm64,armhf] https://packages.microsoft.com/ubuntu/22.04/mssql-server-2022 jammy main
```
Trên Ubuntu 22.04, apt-key legacy (`/etc/apt/trusted.gpg`) đã bị deprecate — nếu dòng `deb` không chỉ định `signed-by=<path-to-keyring>`, apt **không biết dùng file keyring nào vừa tạo** để verify chữ ký, nên coi như repo chưa được ký dù key đã có sẵn trên máy.

## Giải pháp

Sau khi tải file `.list` về, phải tự thêm `signed-by` trỏ đúng vào keyring đã dearmor — không dùng nguyên file Microsoft cung cấp:

```bash
# Cách 1: ghi đè hẳn dòng deb (biết trước tên gói/version)
echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/mssql-server-2022 jammy main" | sudo tee /etc/apt/sources.list.d/mssql-server.list

# Cách 2: sed chèn signed-by vào file .list bất kỳ đã tải (áp dụng chung cho mssql-release.list, mssql-tools...)
sudo sed -i 's#^deb #deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] #' /etc/apt/sources.list.d/<ten-file>.list

sudo apt-get update   # phải hết sạch NO_PUBKEY/Err trước khi apt-get install
```

## Áp dụng lại (How to reuse)

- Bất kỳ khi nào cài package từ repo Microsoft trên Ubuntu 22.04+ theo hướng dẫn "tải file .list có sẵn" (SQL Server, mssql-tools, .NET SDK, VS Code, Edge...) → **luôn kiểm tra file `.list` tải về có `signed-by=` chưa** trước khi chạy `apt-get update`.
- Dấu hiệu nhận biết ngay: `apt-get update` báo `NO_PUBKEY <fingerprint>` **dù `gpg --dearmor` đã chạy thành công và file keyring tồn tại** → 99% là thiếu `signed-by` trong file `.list`, không phải do key sai.
- Lỗi này lặp lại ở NHIỀU file `.list` khác nhau trong cùng 1 lần cài (gặp cả ở `mssql-server.list` lẫn `mssql-release.list` khi cài `mssql-tools18`) — nên fix 1 lần bằng lệnh `sed` chung thay vì sửa tay từng file.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng vội nghi ngờ key bị hỏng và tải lại key nhiều lần — verify bằng `head -3 file.asc` xem có đúng `-----BEGIN PGP PUBLIC KEY BLOCK-----` không, nếu đúng thì key ổn, vấn đề nằm ở file `.list`.
- ⚠️ `cat /etc/apt/sources.list.d/<file>.list` để xem trực tiếp dòng `deb` có `signed-by=` hay chưa — đừng đoán, kiểm tra thật.
- ⚠️ Không dùng `apt-key add` (deprecated, bị apt cảnh báo và sẽ bị loại bỏ hoàn toàn ở version sau) dù nhiều hướng dẫn cũ trên mạng vẫn chỉ cách này.

## Tham chiếu

- Project: iPGSv4, VM Ubuntu 22.04.2 LTS (VirtualBox), cài SQL Server 2022 Express
- File script áp dụng fix: `temp/install-sql-server-ubuntu/setup-sql-server.sh` (project iPGSv4)
- Liên quan: [[sqlclient-migration-ssl-cert-trust-error]] (cùng luồng setup SQL Server cho môi trường Linux)
