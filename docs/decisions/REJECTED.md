---
title: Rejected Patterns — Hệ thống Agent KZTEK
created: 2026-08-05
updated: 2026-08-05
maintainer: GitHub Repo Researcher
---

# Danh sách Pattern Đã Từ Chối

> **Mục đích:** Ghi lại các pattern/feature đã được đánh giá và từ chối trong các nghiên cứu GitHub repo — giúp researcher tương lai tra cứu TRƯỚC khi đề xuất lại, tránh tốn thời gian đánh giá lại cùng một pattern.
>
> **Học từ:** `.out-of-scope/` folder trong `mattpocock/skills` — mỗi file ghi rõ: pattern đã xem xét, lý do từ chối, prior requests. Pattern rõ ràng này tránh được "groundhog day" — AI tái đề xuất cái đã từ chối.
>
> **Khi cập nhật:** Sau mỗi WF-GITHUB-RESEARCH khi loại bỏ pattern khỏi đề xuất, thêm 1 dòng vào bảng dưới.
>
> **Format cột:**
> - `Pattern`: tên pattern/feature/skill, viết ngắn gọn
> - `Lý do từ chối`: nguyên nhân cụ thể — không được viết chung chung "không phù hợp"
> - `Điều kiện mở lại`: khi nào pattern này có thể được xem xét lại
> - `Nguồn tham khảo`: repo/file nguồn tham khảo, kèm RESEARCH doc trong KZTEK
> - `Ngày`: ngày research đánh giá và từ chối

---

## Bảng từ chối

| # | Pattern | Lý do từ chối | Điều kiện mở lại | Nguồn tham khảo | Ngày |
|---|---------|--------------|-----------------|-----------------|------|
| 1 | **Router skill (ask-matt analog)** — skill nhận yêu cầu user và map sang skill nào nên dùng | KZTEK đã có Dispatcher (CLAUDE.md §2 routing table) + `scope-check.md` xử lý mapping yêu cầu → workflow. User KZTEK không invoke skills trực tiếp — Dispatcher handle routing. Thêm router skill = indirection thêm, không giải quyết vấn đề mới nào | Khi KZTEK chuyển sang mô hình user tự invoke skills trực tiếp (không có Dispatcher), hoặc khi số lượng skills > 30 và Dispatcher bắt đầu routing sai > 10% | `mattpocock/skills` `ask-matt/SKILL.md`; `RESEARCH-skills-mattpocock-2026-08-05.md §8 "Đánh giá 6"` | 2026-08-05 |
| 2 | **Skill lifecycle management / plugin distribution** — `plugin.json`, `marketplace.json`, versioning, semver cho từng skill | Hệ thống KZTEK là private config repo — không có distribution channel, không cần versioning per-skill, không có "user install plugin". Các skills luôn ở phiên bản HEAD của repo cấu hình. Effort tạo hạ tầng lifecycle > lợi ích | Khi KZTEK cần phân phối skills ra nhiều team/repo khác nhau, hoặc khi bắt đầu có concept "phiên bản stable vs dev" cho agent system | `mattpocock/skills` `plugin.json`, `marketplace.json`; `RESEARCH-skills-mattpocock-2026-08-05.md §3` | 2026-08-05 |
| 3 | **question-limits cho grilling** — giới hạn số câu hỏi trong phiên grilling interview | Grilling nên dừng khi frontier (danh sách prerequisites chưa rõ) trống — không phải dừng khi đủ N câu. Giới hạn cố định gây hai vấn đề: (a) dừng sớm khi vẫn còn prerequisite chưa rõ, (b) hỏi thêm vô ích khi frontier đã trống nhưng chưa đủ N câu. Dùng frontier-empty-check thay vì question count | Chưa xác định — logic frontier-based vẫn đúng về mặt nguyên lý | `mattpocock/skills` `.out-of-scope/question-limits.md`; `RESEARCH-skills-mattpocock-2026-08-05.md §4.2` | 2026-08-05 |
| 4 | **Skill marketplace / plugin grouping** — file `.claude-plugin/marketplace.json` nhóm skills thành bundles để cài đặt theo batch | KZTEK repo config là single-machine private setup — không có khái niệm "cài plugin theo batch" hay "share skills với người dùng khác qua marketplace". Tất cả skills tự động có sẵn vì nằm trong `~/.claude/commands/`. Overhead tạo và maintain marketplace.json > lợi ích | Khi KZTEK mở rộng thành multi-machine hoặc team-shared config repository, cần mechanism phân nhóm skills theo role/function | `anthropics/agent-skills` `.claude-plugin/marketplace.json`; `RESEARCH-anthropics-skills-2026-07-12.md §1.3.8` | 2026-07-12 |
| 5 | **Automated trigger testing** — `run_loop.py` chạy nhiều test prompts tự động để kiểm tra trigger accuracy của skills | KZTEK đã có `skill-trigger-test.md` làm manual simulation hiệu quả. Automated testing qua `run_loop.py` đòi hỏi Python environment riêng, API key ổn định, và infrastructure test runner — effort setup cao cho project config nhỏ. Kết quả manual simulation đủ chính xác cho quy mô hiện tại | Khi KZTEK có > 50 skills và tần suất sai routing tăng đến mức không thể phát hiện bằng manual testing | `anthropics/agent-skills` `run_loop.py`; `RESEARCH-anthropics-skills-2026-07-12.md §1.4 (comparison table)` | 2026-07-12 |
| 6 | **Prototype skill** — skill tạo throwaway HTML prototype để trả lời design question nhanh | KZTEK không có workflow prototype HTML standalone — design flow của KZTEK là wireframe → mockup trong Markdown → Figma-equivalent (DESIGN-*.md). HTML prototype giả định web-first workflow, không applicable cho WinForms/Avalonia-heavy stack | Khi KZTEK có web product cần rapid prototyping UI, hoặc khi có designer thực sự trong team cần validate concept nhanh | `mattpocock/skills` `prototype/SKILL.md`; `RESEARCH-skills-mattpocock-2026-08-05.md §5 (comparison table)` | 2026-08-05 |
| 7 | **Triage skill** — state machine xử lý GitHub issues (classify, label, assign) | KZTEK chưa dùng GitHub Issues làm primary tracker (dùng private backlog). Triage skill giả định integration với GitHub API để đọc/write labels, assign user — overhead setup API integration không xứng với quy mô team | Khi KZTEK migrate sang GitHub Issues làm primary tracker và có volume > 20 issues/tuần cần triage tự động | `mattpocock/skills` `triage/SKILL.md`; `RESEARCH-skills-mattpocock-2026-08-05.md §3.1` | 2026-08-05 |
| 8 | **Grill-with-docs** — variant của grilling kết hợp documentation lookup (tích hợp GitHub doc queries vào grilling loop) | KZTEK grilling skill (`/grilling`) phục vụ interview requirements chưa rõ — không cần lookup external docs trong quá trình grilling. Grilling nên "find facts by itself" mà không cần agent hỏi user về docs. Grill-with-docs là niche use-case cho team có large private doc bases | Khi KZTEK có private documentation base đủ lớn mà agent cần query trong lúc grilling | `mattpocock/skills` `grill-with-docs/SKILL.md`; `RESEARCH-skills-mattpocock-2026-08-05.md §4.4` | 2026-08-05 |
| 9 | **ui-ux-pro-max: E4 — Thêm KZTEK brand palette vào design-system MASTER template** | User xác nhận áp dụng E1+E2+E3A (2026-08-04); E4 không được chọn trong lần đó. Lý do nghi ngờ: `kztek-brand-info.md` đã chứa đầy đủ brand palette — thêm vào design-system MASTER template sẽ gây duplicate không cần thiết | Khi có yêu cầu rõ từ design workflow thực tế rằng designer cần brand palette trong template form, không phải skill form | `nextlevelbuilder/ui-ux-pro-max-skill`; `RESEARCH-ui-ux-pro-max-skill-2026-08-04.md §7 E4` | 2026-08-04 |
| 10 | **ui-ux-pro-max: E5 — Thêm hướng dẫn query design database vào design-taste-frontend.md** | User xác nhận áp dụng E1+E2+E3A (2026-08-04); E5 không được chọn. Skill `design-taste-frontend.md` đã có ~508 dòng hardcoded rules — thêm layer query design database tăng complexity mà người dùng hiện tại của KZTEK (WinForms/Avalonia developer) không có nhu cầu query styles database cho web | Khi KZTEK phát triển web product thực sự và developer cần query design database cho styling decisions | `nextlevelbuilder/ui-ux-pro-max-skill`; `RESEARCH-ui-ux-pro-max-skill-2026-08-04.md §7 E5` | 2026-08-04 |

---

## Ghi chú tra cứu

Trước khi đề xuất bất kỳ pattern mới nào trong WF-GITHUB-RESEARCH, kiểm tra:

1. Pattern có trong bảng trên không? → Nếu có, lý do từ chối còn valid không?
2. Điều kiện mở lại đã được thỏa mãn chưa? → Nếu có → có thể đề xuất lại kèm note "đã từng từ chối, điều kiện mở lại đã thỏa mãn vì X".
3. Pattern mới có giống về bản chất với pattern đã từ chối không? → Cẩn thận với "same pattern, different name".

---

*File này được tạo bởi GitHub Repo Researcher (L4) trong WF-GITHUB-RESEARCH.*
*Nguồn cảm hứng: `.out-of-scope/` folder trong `mattpocock/skills` (research session 2026-08-05).*
