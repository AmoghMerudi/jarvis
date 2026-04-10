from typing import Any, Callable, Awaitable

# Registry: tool_name → (schema, handler)
_registry: dict[str, tuple[dict[str, Any], Callable[..., Awaitable[str]]]] = {}


def register_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    handler: Callable[..., Awaitable[str]],
) -> None:
    _registry[name] = (
        {
            "name": name,
            "description": description,
            "input_schema": input_schema,
        },
        handler,
    )


def get_tool_schemas() -> list[dict[str, Any]]:
    return [schema for schema, _ in _registry.values()]


async def execute_tool(name: str, tool_input: dict[str, Any]) -> str:
    if name not in _registry:
        return f"Error: unknown tool '{name}'"
    _, handler = _registry[name]
    return await handler(**tool_input)


def load_all_tools() -> None:
    """Import tool modules so they self-register."""
    import tools.system  # noqa: F401
    import tools.files  # noqa: F401
    import tools.web_search  # noqa: F401
