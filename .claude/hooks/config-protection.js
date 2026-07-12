#!/usr/bin/env node
/**
 * Config Protection Hook — KZTEK Workspace
 *
 * Chặn agent sửa các file lint/format/config quan trọng đã tồn tại.
 * Mục đích: ép agent sửa source code thay vì làm yếu config để lách qua
 * lỗi lint/build. Học từ ecc/scripts/hooks/config-protection.js (affaan-m/ecc).
 *
 * Input  : JSON qua stdin — {"tool_name": "Edit|Write", "tool_input": {"file_path": "..."}}
 * Exit 0 : cho phép (không phải file bảo vệ, hoặc file chưa tồn tại)
 * Exit 2 : chặn (file bảo vệ đã tồn tại đang bị sửa)
 *
 * Danh sách file bảo vệ (KZTEK):
 *   .gitignore, appsettings.json, appsettings.*.json,
 *   .eslintrc*, eslint.config.*, .editorconfig
 */

'use strict';

const fs   = require('fs');
const path = require('path');

const MAX_STDIN = 1024 * 1024; // 1MB

// --- Danh sách file tên chính xác (Set lookup O(1)) ---
const PROTECTED_EXACT = new Set([
  // Git
  '.gitignore',
  // ASP.NET / .NET config
  'appsettings.json',
  // Editor config
  '.editorconfig',
  // ESLint legacy
  '.eslintrc',
  '.eslintrc.js',
  '.eslintrc.cjs',
  '.eslintrc.json',
  '.eslintrc.yml',
  '.eslintrc.yaml',
  // ESLint flat config (v9+)
  'eslint.config.js',
  'eslint.config.mjs',
  'eslint.config.cjs',
  'eslint.config.ts',
  'eslint.config.mts',
  'eslint.config.cts',
]);

// --- Pattern: appsettings.*.json (ví dụ: appsettings.Development.json) ---
function isProtectedPattern(basename) {
  // Khớp appsettings.<bất kỳ>.json
  return /^appsettings\..+\.json$/.test(basename);
}

function isProtected(basename) {
  return PROTECTED_EXACT.has(basename) || isProtectedPattern(basename);
}

/**
 * Kiểm tra xem file có tồn tại trên filesystem không.
 * Dùng lstatSync để phát hiện cả symlink trỏ tới target không tồn tại.
 * Chỉ trả về false khi ENOENT — các lỗi khác (EACCES, EPERM) → coi là tồn tại
 * để tránh vô tình bỏ qua file bảo vệ do lỗi permission.
 */
function fileExists(filePath) {
  try {
    fs.lstatSync(filePath);
    return true;
  } catch (err) {
    if (err && err.code === 'ENOENT') return false;
    return true; // fail-closed: lỗi khác → coi là tồn tại
  }
}

function run(raw, options = {}) {
  // Chặn nếu input bị truncate (không thể tin tưởng payload)
  if (options.truncated) {
    return {
      exitCode: 2,
      stderr:
        'BLOCKED [config-protection]: Input vượt quá giới hạn kích thước cho phép. ' +
        'Từ chối xử lý payload bị cắt ngắn để tránh bỏ qua bảo vệ config. ' +
        'Thử lại với edit nhỏ hơn hoặc tạm thời tắt hook config-protection.',
    };
  }

  // Parse JSON
  let input = {};
  if (typeof raw === 'string') {
    try { input = raw.trim() ? JSON.parse(raw) : {}; } catch { input = {}; }
  } else if (raw && typeof raw === 'object') {
    input = raw;
  }

  // Chỉ xử lý tool Edit và Write
  const toolName = (input.tool_name || '').trim();
  if (toolName !== 'Edit' && toolName !== 'Write') {
    return { exitCode: 0 };
  }

  // Lấy đường dẫn file
  const filePath = (input.tool_input && (input.tool_input.file_path || input.tool_input.file)) || '';
  if (!filePath) return { exitCode: 0 };

  const basename = path.basename(filePath);

  if (!isProtected(basename)) {
    return { exitCode: 0 };
  }

  // File nằm trong danh sách bảo vệ — chỉ chặn khi file ĐÃ TỒN TẠI
  // (tạo mới file config lần đầu là hợp lệ — scaffolding)
  if (!fileExists(filePath)) {
    return { exitCode: 0 };
  }

  return {
    exitCode: 2,
    stderr:
      `BLOCKED [config-protection]: Không được phép sửa "${basename}". ` +
      'File này nằm trong danh sách config bảo vệ của KZTEK workspace. ' +
      'Hãy sửa source code để tuân thủ rule thay vì làm yếu config. ' +
      'Nếu đây là thay đổi config hợp lệ (không phải để lách lint), ' +
      'hãy giải thích rõ lý do cho user và được xác nhận trước khi tiếp tục.',
  };
}

// --- Stdin handler (chạy standalone qua spawnSync / pipe) ---
let raw       = '';
let truncated = /^(1|true|yes)$/i.test(String(process.env.KZTEK_HOOK_INPUT_TRUNCATED || ''));

process.stdin.setEncoding('utf8');

process.stdin.on('data', chunk => {
  if (raw.length < MAX_STDIN) {
    const remaining = MAX_STDIN - raw.length;
    raw += chunk.substring(0, remaining);
    if (chunk.length > remaining) truncated = true;
  } else {
    truncated = true;
  }
});

process.stdin.on('end', () => {
  const result = run(raw, { truncated, maxStdin: MAX_STDIN });

  if (result.stderr) {
    process.stderr.write(result.stderr + '\n');
  }

  if (result.exitCode === 2) {
    process.exit(2);
  }

  // Exit 0: forward stdin ra stdout (một số harness dùng stdout để tiếp tục)
  process.stdout.write(raw);
});
