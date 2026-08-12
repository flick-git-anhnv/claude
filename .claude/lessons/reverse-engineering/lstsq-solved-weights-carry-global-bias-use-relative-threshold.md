---
name: lstsq-solved-weights-carry-global-bias-use-relative-threshold
description: Weight/bias phục hồi bằng im2col+least-squares từ feature-map thật có thể mang theo một độ lệch (bias) hệ thống trên toàn ảnh — dùng ngưỡng TUYỆT ĐỐI trên logit/sigmoid sẽ luôn sai (mọi vị trí đều "positive"); phải dùng ngưỡng TƯƠNG ĐỐI (percentile) vì tín hiệu thật vẫn nổi bật rõ so với nền
metadata:
  type: reverse-engineering
---

## Bối cảnh
Sau khi phục hồi toàn bộ 45/45 weight thật của mạng RetinaFace-style qua kỹ thuật im2col+lstsq (xem [[recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps]]), model chạy sạch (0 NaN/Inf) và mọi layer riêng lẻ verify đúng qua so khớp tensor thật (corr 0.85–0.9998). Nhưng khi decode ra bounding box thật bằng công thức chuẩn `sigmoid(cls_face - cls_bg) > 0.5`, kết quả VÔ NGHĨA: xác suất "có mặt" ~99.9% ở MỌI vị trí trên ảnh — kể cả trên chính ảnh dùng để capture/verify weight.

## Chẩn đoán sai lầm ban đầu
Nghi ngờ: weight sai, kênh cls bị đảo, hệ phương trình thiếu xác định (underdetermined) ở các head phân giải nhỏ (4×4, 8×8 so với 577 ẩn của conv 3×3×64). Đã bổ sung 49 ảnh hiệu chuẩn (random) để tăng equations/unknowns lên hàng chục-hàng trăm lần cho mọi layer — resid giảm xuống ~1e-7 cho gần hết các head, nhưng vấn đề "99.9% khắp nơi" TRÊN ẢNH MỚI vẫn y hệt không đổi.

## Nguyên nhân thật
In ra bản đồ logit đầy đủ (không chỉ min/max) mới thấy: nền (background) có baseline ~7.0 (không phải ~0 như kỳ vọng của softmax cân bằng), và vùng thật sự có mặt nhô cao rõ rệt lên ~10–14 (chênh +3 đến +7 so với nền) — tín hiệu THẬT SỰ TỒN TẠI VÀ RÕ RÀNG, chỉ là bị "ngập" trong một độ lệch dương toàn cục khiến `sigmoid(anything - 7) ≈ 0.999` ở mọi nơi. Độ lệch này đến từ chính bản chất phép giải lstsq: nghiệm minimum-norm/least-squares cho conv+bias không đảm bảo bias tuyệt đối khớp phân bố gốc khi lan truyền qua nhiều lớp có sai số tích lũy nhỏ (đặc biệt các cạnh residual/FPN xấp xỉ, xem [[recover-cnn-weights-via-im2col-lstsq-from-captured-featuremaps]] mục "2 cạnh FPN chưa giải sạch").

## Cách xác nhận
Lấy **ground-truth thật** từ chính SDK gốc (hook lấy `FaceInfo.toString()` sau khi gọi `detectFaces()` thật — trả về toạ độ box chính xác đã qua verify công nghiệp), rồi so trực tiếp bản đồ logit tại đúng vị trí đó: logit tại vị trí GT luôn thuộc nhóm cao nhất ảnh, dù giá trị tuyệt đối (~10-14) không "trông giống" một xác suất chuẩn hoá.

## Cách fix
Thay `threshold = 0.5` (tuyệt đối) bằng `threshold = percentile(all_logits, 99.5)` (tương đối, theo phân vị của TOÀN BỘ logit trong ảnh đang xử lý) trước khi áp NMS. Sau khi sửa: box dự đoán trùng khớp rõ rệt với GT thật của SDK gốc (nhìn bằng mắt overlap gần như hoàn hảo trên khuôn mặt).

## Cách áp dụng
Bất cứ khi nào weight/bias được phục hồi bằng hồi quy tuyến tính (không phải huấn luyện end-to-end với loss chuẩn hoá), đừng vội kết luận "model sai" chỉ vì ngưỡng tuyệt đối cho kết quả vô nghĩa — luôn in ra toàn bộ bản đồ giá trị (không chỉ min/max/mean) để kiểm tra có TƯƠNG PHẢN CỤC BỘ rõ rệt hay không trước khi đổ lỗi cho weight. Nếu có tương phản rõ nhưng lệch baseline, chuyển sang ngưỡng tương đối (percentile/z-score theo từng ảnh) thay vì tiếp tục "sửa" weight vốn đã đúng.
