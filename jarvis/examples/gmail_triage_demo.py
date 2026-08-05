"""Demo THẬT: phân loại 5 email gần nhất trong hộp thư Gmail thật, bằng AI
thật (qua ClaudeCliBackend, không phải keyword matching) — không phải dữ
liệu giả lập.

Dữ liệu email dưới đây được lấy thật từ Gmail của user qua MCP tool
(search_threads) ngay trước khi chạy demo này — xem lịch sử hội thoại.

Run: python examples/gmail_triage_demo.py

Điểm mấu chốt so với if/else: không có "từ khóa" cố định nào để phân biệt
"job alert tự động, không cần làm gì" với "email cần trả lời thật" — 5 email
dưới đây không chứa từ nào kiểu "gấp", "khẩn", "reply"... nhưng con người đọc
qua là biết ngay đây toàn thông báo tự động. Agent CLassifyAgent ở đây dùng
AI thật để suy luận điều đó, if/else keyword-based thì chịu.
"""

import json

from jarvis import Agent, AgentContext, AgentRegistry, Orchestrator, Router, Task
from jarvis.core.task import TaskResult
from jarvis.llm import ClaudeCliBackend

# Dữ liệu THẬT lấy từ Gmail qua mcp Gmail search_threads (in:inbox, 5 mới nhất)
REAL_EMAILS = [
    {
        "id": "19fd0e127d200396",
        "sender": "jobalerts-noreply@linkedin.com",
        "subject": "Viettel Software tuyển dụng Trưởng nhóm lập trình Fullstack tại Viettel Software",
        "snippet": "Viettel Software Viettel Software tuyển dụng Trưởng nhóm lập trình Fullstack: Mô tả công việc...",
    },
    {
        "id": "19fd07348be28e0a",
        "sender": "jobalerts-noreply@linkedin.com",
        "subject": "Lead Software Engineer, Customer Data Platform tại Grab",
        "snippet": "Grab Lead Software Engineer, Customer Data Platform: Company Description About Grab...",
    },
    {
        "id": "19fd00578adf727b",
        "sender": "jobalerts-noreply@linkedin.com",
        "subject": "Mobile Engineer (Flutter) tại Wanosoft Co.,Ltd",
        "snippet": "Wanosoft Co.,Ltd Mobile Engineer (Flutter): Home»Careers»Mobile Engineer (Flutter)...",
    },
    {
        "id": "19fcf97a1ef3798b",
        "sender": "jobalerts-noreply@linkedin.com",
        "subject": "Senior System Software Engineer, AI Data Platform tại NVIDIA",
        "snippet": "NVIDIA Senior System Software Engineer, AI Data Platform: Our team is building...",
    },
    {
        "id": "19fcdbadf2414d89",
        "sender": "noreply@lovable.dev",
        "subject": "What 10+ prompts can actually become",
        "snippet": "Sentry built a sales dashboard. AppDirect saved $80000...",
    },
]


class FetchInboxAgent(Agent):
    """Trong bản thật, agent này gọi Gmail API. Ở đây trả về dữ liệu ĐÃ lấy
    thật từ Gmail (xem REAL_EMAILS) — tách riêng để agent classify/decide
    phía sau test được độc lập, không cần gọi mạng mỗi lần chạy demo."""

    name = "fetch_inbox"
    description = "Lấy N email gần nhất từ Gmail"

    def run(self, context: AgentContext) -> TaskResult:
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=REAL_EMAILS)


class ClassifyEmailsAgent(Agent):
    """Dùng AI THẬT (Claude, qua ClaudeCliBackend) để đọc hiểu từng email và
    quyết định category + có cần trả lời không — không dựa vào từ khóa."""

    name = "classify_emails"
    description = "Phân loại email bằng AI thật: category + needs_reply + lý do"

    def __init__(self) -> None:
        super().__init__()
        self.backend = ClaudeCliBackend()

    def run(self, context: AgentContext) -> TaskResult:
        emails = context.last_output()
        listing = "\n".join(
            f"{i}. From: {e['sender']} | Subject: {e['subject']} | Snippet: {e['snippet']}"
            for i, e in enumerate(emails)
        )
        prompt = f"""Đây là {len(emails)} email trong hộp thư. Với MỖI email, xác định:
- category: một trong "job_alert" (thông báo tuyển dụng tự động), "newsletter" (bản tin/marketing), "needs_reply" (email thật cần người nhận trả lời), "spam"
- needs_reply: true/false
- reason: lý do ngắn gọn (1 câu, tiếng Việt)

Danh sách email:
{listing}

CHỈ trả về JSON array, không giải thích thêm, đúng {len(emails)} phần tử, theo thứ tự trên, mỗi phần tử có 3 field: category, needs_reply, reason."""

        raw = self.backend.complete(prompt)
        # AI đôi khi bọc JSON trong ```json ... ``` — bóc ra trước khi parse
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            cleaned = cleaned.removeprefix("json").strip()
        classifications = json.loads(cleaned)

        merged = [{**email, **cls} for email, cls in zip(emails, classifications)]
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=merged)


class DecideActionAgent(Agent):
    """Dựa trên phân loại của agent trước, quyết định hành động cho từng
    email — KHÔNG tự gửi gì, chỉ báo cáo hành động đề xuất."""

    name = "decide_action"
    description = "Đề xuất hành động: archive / draft reply / ignore"

    def run(self, context: AgentContext) -> TaskResult:
        classified = context.last_output()
        lines = []
        needs_reply_count = 0
        for e in classified:
            if e["needs_reply"]:
                action = "→ cần soạn draft trả lời"
                needs_reply_count += 1
            elif e["category"] in ("job_alert", "newsletter"):
                action = "→ đề xuất archive (thông báo tự động, không cần hành động)"
            else:
                action = "→ đề xuất bỏ qua/xóa"
            lines.append(
                f"[{e['category']:11s}] {e['subject'][:60]:60s} {action}\n"
                f"              lý do AI: {e['reason']}"
            )
        summary = (
            f"Tổng {len(classified)} email — {needs_reply_count} email cần trả lời thật.\n\n"
            + "\n".join(lines)
        )
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=summary)


def build_orchestrator() -> Orchestrator:
    registry = AgentRegistry()
    registry.register(FetchInboxAgent())
    registry.register(ClassifyEmailsAgent())
    registry.register(DecideActionAgent())

    router = Router(default_agents=["fetch_inbox", "classify_emails", "decide_action"])
    return Orchestrator(registry, router)


if __name__ == "__main__":
    orchestrator = build_orchestrator()
    report = orchestrator.dispatch(Task(input="triage hộp thư"))

    if not report.succeeded:
        for r in report.results:
            if not r.success:
                print(f"❌ Agent '{r.agent_name}' lỗi: {r.error}")
    else:
        print(report.final_output)
