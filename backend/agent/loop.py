from dataclasses import dataclass, field
from datetime import date
from typing import Any

from agent.prompts import build_system_prompt
from agent.tools import PermissionDenial, execute_tool, get_tool_schemas
from memory.facts import get_all_facts
from memory.semantic import retrieve_memories
from providers import get_provider


@dataclass(frozen=True)
class UsageSummary:
    input_tokens: int = 0
    output_tokens: int = 0

    def add(self, turn_usage: dict[str, int]) -> "UsageSummary":
        return UsageSummary(
            input_tokens=self.input_tokens + turn_usage.get("input_tokens", 0),
            output_tokens=self.output_tokens + turn_usage.get("output_tokens", 0),
        )


@dataclass(frozen=True)
class TurnResult:
    output: str
    stop_reason: str  # "completed" | "max_turns" | "max_budget"
    usage: UsageSummary
    permission_denials: tuple[PermissionDenial, ...]
    turns_taken: int


@dataclass(frozen=True)
class AgentConfig:
    max_turns: int = 10
    max_budget_tokens: int = 20_000


async def run_agent(
    user_message: str,
    history: list[dict[str, Any]],
    config: AgentConfig = AgentConfig(),
) -> TurnResult:
    try:
        facts_str = await get_all_facts()
    except Exception:
        facts_str = "No explicit facts stored yet."
    try:
        memories_str = await retrieve_memories(user_message)
    except Exception:
        memories_str = "No relevant memories found."
    system = build_system_prompt(
        date=date.today().isoformat(),
        facts=facts_str,
        memories=memories_str,
    )

    provider = get_provider()
    messages = history + [{"role": "user", "content": user_message}]
    tools = get_tool_schemas()
    usage = UsageSummary()
    denials: list[PermissionDenial] = []

    for turn in range(config.max_turns):
        response = await provider.chat(messages=messages, system=system, tools=tools)

        usage = usage.add(response.get("usage", {}))
        if usage.input_tokens + usage.output_tokens >= config.max_budget_tokens:
            return TurnResult(
                output=response.get("text", ""),
                stop_reason="max_budget",
                usage=usage,
                permission_denials=tuple(denials),
                turns_taken=turn + 1,
            )

        tool_calls = response.get("tool_calls", [])
        if not tool_calls:
            return TurnResult(
                output=response.get("text", ""),
                stop_reason="completed",
                usage=usage,
                permission_denials=tuple(denials),
                turns_taken=turn + 1,
            )

        messages.append(response["raw_assistant_message"])
        for tool_call in tool_calls:
            result = await execute_tool(tool_call["name"], tool_call["input"])
            if isinstance(result, PermissionDenial):
                denials.append(result)
                tool_content = f"[denied: {result.reason}]"
            else:
                tool_content = result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_content,
            })

    return TurnResult(
        output="I reached the maximum number of steps without a final answer.",
        stop_reason="max_turns",
        usage=usage,
        permission_denials=tuple(denials),
        turns_taken=config.max_turns,
    )
