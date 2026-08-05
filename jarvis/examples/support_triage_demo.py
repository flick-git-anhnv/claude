"""Demo: triage a customer bug report — same task, two different chains.

Run: python examples/support_triage_demo.py

Compare this file's `run_with_jarvis()` against `run_with_if_else()` below —
they do the same job. The point isn't that Jarvis can do something if/else
can't; it's what stays easy to change as the number of branches grows.
"""

from jarvis import Agent, AgentContext, AgentRegistry, Orchestrator, Route, Router, Task
from jarvis.core.task import TaskResult

# ── Keyword tables (shared by both versions, so the comparison is fair) ──

CRITICAL_KEYWORDS = ["sập", "không hoạt động", "crash", "mất dữ liệu"]
TEAM_KEYWORDS = {
    "iParking": ["camera", "biển số", "lpr", "bãi đỗ", "barrier"],
    "iLocker": ["tủ", "locker", "rfid"],
    "R&D": ["firmware", "mạch", "bo mạch", "esp32", "stm32"],
}


def classify(text: str) -> dict:
    lower = text.lower()
    severity = "P0" if any(k in lower for k in CRITICAL_KEYWORDS) else "P2"
    team = next((t for t, kws in TEAM_KEYWORDS.items() if any(k in lower for k in kws)), "Unknown")
    return {"raw": text, "severity": severity, "team": team}


# ══════════════════════════════════════════════════════════════════════
# Version A — Jarvis: agents + routes
# ══════════════════════════════════════════════════════════════════════


class ClassifyAgent(Agent):
    name = "classify"
    description = "Xác định severity + team phụ trách từ nội dung phản ánh"

    def run(self, context: AgentContext) -> TaskResult:
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=classify(context.task.input))


class EscalateAgent(Agent):
    """Chỉ nằm trong chain P0 — route thường không đi qua bước này."""

    name = "escalate"
    description = "Báo khẩn Engineering Manager + CTO cho bug P0 (mô phỏng)"

    def run(self, context: AgentContext) -> TaskResult:
        data = dict(context.last_output())
        data["escalated"] = True
        print(f"  🚨 ESCALATE: đã báo EM + CTO ngay (team={data['team']})")
        return TaskResult(task_id=context.task.id, agent_name=self.name, output=data)


class FormatTicketAgent(Agent):
    name = "format_ticket"
    description = "Định dạng ticket cuối cùng theo template chuẩn"

    def run(self, context: AgentContext) -> TaskResult:
        data = context.last_output()
        lines = [
            f"[BUG-{context.task.id}] Priority: {data['severity']} | Team: {data['team']}",
            f"Mô tả: {data['raw']}",
        ]
        if data.get("escalated"):
            lines.append("⚠️  Đã escalate lên EM + CTO")
        return TaskResult(task_id=context.task.id, agent_name=self.name, output="\n".join(lines))


def build_jarvis_orchestrator() -> Orchestrator:
    registry = AgentRegistry()
    registry.register(ClassifyAgent())
    registry.register(EscalateAgent())
    registry.register(FormatTicketAgent())

    router = Router(default_agents=["classify", "format_ticket"])
    router.add(
        Route.keyword(
            name="critical-bug",
            agents=["classify", "escalate", "format_ticket"],
            keywords=CRITICAL_KEYWORDS,
            priority=10,
        )
    )
    return Orchestrator(registry, router)


def run_with_jarvis(text: str) -> str:
    orchestrator = build_jarvis_orchestrator()
    report = orchestrator.dispatch(Task(input=text))
    return report.final_output


# ══════════════════════════════════════════════════════════════════════
# Version B — if/else thuần, không dùng Jarvis, cùng logic
# ══════════════════════════════════════════════════════════════════════


def run_with_if_else(text: str) -> str:
    data = classify(text)
    escalated = False

    if data["severity"] == "P0":
        print(f"  🚨 ESCALATE: đã báo EM + CTO ngay (team={data['team']})")
        escalated = True

    lines = [
        f"[BUG] Priority: {data['severity']} | Team: {data['team']}",
        f"Mô tả: {data['raw']}",
    ]
    if escalated:
        lines.append("⚠️  Đã escalate lên EM + CTO")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    samples = [
        "Camera LPR nhận diện sai biển số liên tục ở làn vào",
        "Toàn bộ hệ thống bãi đỗ sập, không hoạt động, khách không vào được",
    ]

    for text in samples:
        print(f"\n--- input: {text!r} ---")
        print("[Jarvis]")
        print(run_with_jarvis(text))
        print("[if/else]")
        print(run_with_if_else(text))
