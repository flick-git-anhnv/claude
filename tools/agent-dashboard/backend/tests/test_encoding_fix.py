"""Tests for encoding fixes — _sanitize_text và _extract_user_turn_text.

Root cause được fix:
  - Windows locale.getpreferredencoding() = 'cp1252' → open() không chỉ encoding
    sẽ đọc UTF-8 file bị sai → mojibake hoặc lone surrogates.
  - Các code path đọc JSONL đã được xác nhận dùng encoding="utf-8" tường minh.
  - _sanitize_text() trong chain.py làm sạch surrogate cho dữ liệu cũ có thể bị ảnh hưởng.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from agent_dashboard.db.chain import _extract_user_turn_text, _sanitize_text
from agent_dashboard.tail_reader import TailReader


# ══════════════════════════════════════════════════════════════════════════════
# 1. Tests for _sanitize_text
# ══════════════════════════════════════════════════════════════════════════════

class TestSanitizeText:
    """Unit tests cho _sanitize_text() — defensive cleanup của lone surrogates."""

    def test_clean_text_unchanged(self):
        """Text không có surrogate → trả nguyên bản (fast path)."""
        text = "kiểm tra, và hoàn thiện các tính năng đang dở"
        assert _sanitize_text(text) == text

    def test_empty_string_unchanged(self):
        assert _sanitize_text("") == ""

    def test_ascii_unchanged(self):
        text = "Hello world 123"
        assert _sanitize_text(text) == text

    def test_lone_surrogate_removed(self):
        """Lone surrogate U+DC9D (từ byte 0x9D qua errors='surrogateescape') bị loại."""
        garbled = "gi\udc9d"  # byte 0x9D → U+DC9D qua surrogateescape
        result = _sanitize_text(garbled)
        assert "\udc9d" not in result, "Lone surrogate phải bị loại"
        assert "gi" in result, "Phần text sạch phải được giữ lại"

    def test_lone_surrogate_dc90_removed(self):
        """Lone surrogate U+DC90 (từ byte 0x90) bị loại."""
        garbled = "text\udc90more"
        result = _sanitize_text(garbled)
        assert "\udc90" not in result
        assert "text" in result
        assert "more" in result

    def test_multiple_surrogates_removed(self):
        """Nhiều lone surrogates trong 1 string đều bị loại."""
        garbled = "\udc9d\udc90\udcA0"
        result = _sanitize_text(garbled)
        for c in garbled:
            assert c not in result, f"Surrogate {ord(c):04X} phải bị loại"

    def test_mixed_text_surrogates_cleans_partial(self):
        """Text hợp lệ xen kẽ surrogate → giữ phần hợp lệ."""
        garbled = "và ho\udc9dn thi\udc90n"
        result = _sanitize_text(garbled)
        assert "\udc9d" not in result
        assert "\udc90" not in result
        # Phần text sạch phải còn lại
        assert "và ho" in result
        assert "n thi" in result

    def test_valid_vietnamese_no_surrogate(self):
        """Tiếng Việt hợp lệ qua _sanitize_text vẫn nguyên vẹn."""
        text = "Đọc báo cáo, phân tích và đề xuất giải pháp tối ưu."
        assert _sanitize_text(text) == text

    def test_return_type_always_str(self):
        """Luôn trả str, không bao giờ None."""
        assert isinstance(_sanitize_text(""), str)
        assert isinstance(_sanitize_text("abc\udc9d"), str)


# ══════════════════════════════════════════════════════════════════════════════
# 2. Tests for _extract_user_turn_text với encoding edge cases
# ══════════════════════════════════════════════════════════════════════════════

class TestExtractUserTurnTextEncoding:
    """Tests _extract_user_turn_text với input có thể chứa surrogate."""

    def _make_payload(self, text_content: str, is_tool_result: bool = False) -> str:
        if is_tool_result:
            content = [{"type": "tool_result", "tool_use_id": "t1", "content": text_content}]
        else:
            content = [{"type": "text", "text": text_content}]
        return json.dumps({
            "type": "user",
            "message": {
                "role": "user",
                "content": content,
            },
            "timestamp": "2026-08-08T10:00:00Z",
        })

    def test_clean_vietnamese_text_extracted_correctly(self):
        payload = self._make_payload("kiểm tra và hoàn thiện các tính năng")
        result = _extract_user_turn_text(payload)
        assert result == "kiểm tra và hoàn thiện các tính năng"

    def test_surrogate_in_user_text_is_cleaned(self):
        """User text chứa lone surrogate → surrogate bị loại trong output."""
        garbled_text = "gi\udc9d hơn"  # lone surrogate giữa text
        payload = self._make_payload(garbled_text)
        result = _extract_user_turn_text(payload)
        assert result is not None, "Phải trích được text"
        assert "\udc9d" not in result, "Surrogate phải bị làm sạch"
        assert "gi" in result
        assert "hơn" in result

    def test_tool_result_event_returns_none(self):
        """tool_result event → None (bỏ qua, không hiển thị trong history)."""
        payload = self._make_payload("some tool output", is_tool_result=True)
        assert _extract_user_turn_text(payload) is None

    def test_text_truncated_to_120_chars(self):
        """Text dài hơn 120 chars → cắt đúng 120."""
        long_text = "a" * 200
        payload = self._make_payload(long_text)
        result = _extract_user_turn_text(payload)
        assert result is not None
        assert len(result) == 120

    def test_text_after_sanitize_still_truncated_correctly(self):
        """Sau khi sanitize, text vẫn cắt đúng 120 chars."""
        long_text_with_surrogate = "a" * 50 + "\udc9d" + "b" * 100
        payload = self._make_payload(long_text_with_surrogate)
        result = _extract_user_turn_text(payload)
        assert result is not None
        assert len(result) <= 120
        assert "\udc9d" not in result

    def test_string_content_format_cleaned(self):
        """content là string (format cũ) → sanitize rồi trả về."""
        garbled = "text\udc90ok"
        data = {"type": "user", "message": {"role": "user", "content": garbled}}
        result = _extract_user_turn_text(json.dumps(data))
        assert result is not None
        assert "\udc90" not in result
        assert "text" in result
        assert "ok" in result

    def test_none_payload_returns_none(self):
        assert _extract_user_turn_text(None) is None

    def test_empty_payload_returns_none(self):
        assert _extract_user_turn_text("") is None

    def test_invalid_json_returns_none(self):
        assert _extract_user_turn_text("not-valid-json{{{") is None


# ══════════════════════════════════════════════════════════════════════════════
# 3. TailReader encoding safety — xác nhận binary mode đúng với Vietnamese
# ══════════════════════════════════════════════════════════════════════════════

class TestTailReaderUtf8Safety:
    """Xác nhận TailReader đọc UTF-8 Vietnamese đúng, không có mojibake."""

    def test_vietnamese_text_decoded_correctly(self, tmp_path: pathlib.Path):
        """Tiếng Việt UTF-8 trong JSONL → decode đúng, không bị garbled."""
        f = tmp_path / "session.jsonl"
        line_text = "kiểm tra, và hoàn thiện các tính năng đang dở"
        payload = json.dumps({"type": "user", "message": {"content": line_text}})
        raw_bytes = (payload + "\n").encode("utf-8")
        f.write_bytes(raw_bytes)

        reader = TailReader()
        lines = reader.read_new_lines(str(f))
        assert len(lines) == 1

        data = json.loads(lines[0])
        extracted = data["message"]["content"]
        assert extracted == line_text, (
            f"Text bị garbled: expected {repr(line_text)}, got {repr(extracted)}"
        )

    def test_multibyte_boundary_safe(self, tmp_path: pathlib.Path):
        """Multi-byte UTF-8 sequences không bị split ở chunk boundary."""
        f = tmp_path / "session.jsonl"
        # Tạo 2 lines: line 1 kết thúc đúng boundary, line 2 có tiếng Việt
        line1 = json.dumps({"type": "assistant"}) + "\n"
        line2 = json.dumps({"type": "user", "text": "Đây là nội dung tiếng Việt"}) + "\n"
        f.write_bytes((line1 + line2).encode("utf-8"))

        reader = TailReader()
        lines = reader.read_new_lines(str(f))
        assert len(lines) == 2

        data2 = json.loads(lines[1])
        assert data2["text"] == "Đây là nội dung tiếng Việt"

    def test_invalid_utf8_bytes_replaced_not_crash(self, tmp_path: pathlib.Path):
        """Byte không hợp lệ UTF-8 → thay bằng \\ufffd, không crash, không surrogate."""
        f = tmp_path / "session.jsonl"
        # Tạo JSON line với 1 byte không hợp lệ UTF-8 (0x80 đứng một mình)
        valid_part = b'{"type":"user","text":"hello'
        invalid_byte = b"\x80"  # byte này không hợp lệ nếu đứng một mình trong UTF-8
        rest = b' world"}\n'
        f.write_bytes(valid_part + invalid_byte + rest)

        reader = TailReader()
        lines = reader.read_new_lines(str(f))
        # Phải đọc được line, không crash
        assert len(lines) == 1
        line_str = lines[0]

        # Không có lone surrogate (chứng tỏ KHÔNG dùng errors='surrogateescape')
        assert not any(0xD800 <= ord(c) <= 0xDFFF for c in line_str), (
            "TailReader không được tạo lone surrogate — chứng tỏ errors='replace' đúng"
        )
        # Replacement character U+FFFD phải có mặt thay cho byte lỗi
        assert "�" in line_str, "Byte lỗi phải được thay bằng U+FFFD"
