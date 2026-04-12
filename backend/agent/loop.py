from datetime import date
from typing import Any

from agent.prompts import build_system_prompt
from agent.tools import execute_tool, get_tool_schemas
from memory.facts import get_all_facts
from memory.semantic import retrieve_memories
from providers import get_provider

MAX_ITERATIONS = 10


async def run_agent(
    user_message: str,
    history: list[dict[str, Any]],
) -> str:
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

    for _ in range(MAX_ITERATIONS):
        response = await provider.chat(messages=messages, system=system, tools=tools)

        # Normalise stop reason across providers
        stop_reason = response.get("stop_reason") or response.get("finish_reason")
        tool_calls = _extract_tool_calls(response)

        if not tool_calls:
            return _extract_text(response)

        # Execute all tool calls and feed results back
        messages.append({"role": "assistant", "content": response.get("content", "")})
        for tool_call in tool_calls:
            result = await execute_tool(tool_call["name"], tool_call["input"])
            messages.append(
                {
                    "role": "tool",
                    "tool_use_id": tool_call["id"],
                    "content": result,
                }
            )

    return "I reached the maximum number of steps without a final answer."


def _extract_tool_calls(response: dict[str, Any]) -> list[dict[str, Any]]:
    calls = []
    for block in response.get("content", []):
        if isinstance(block, dict) and block.get("type") == "tool_use":
            calls.append(
                {"id": block["id"], "name": block["name"], "input": block["input"]}
            )
    return calls


def _extract_text(response: dict[str, Any]) -> str:
    for block in response.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            return block["text"]
    # Fallback for providers that return a top-level text field
    return response.get("text", "")
