from agent.tools import register_tool
from memory.facts import set_fact, get_fact
from memory.semantic import store_memory, retrieve_memories


async def _remember_fact(key: str, value: str) -> str:
    await set_fact(key, value)
    return f"Remembered: {key} = {value}"


async def _recall_fact(key: str) -> str:
    value = await get_fact(key)
    return value if value is not None else f"No fact stored for '{key}'"


async def _store_memory(content: str) -> str:
    await store_memory(content)
    return "Memory stored."


async def _search_memories(query: str) -> str:
    return await retrieve_memories(query)


register_tool(
    name="remember_fact",
    description=(
        "Permanently store a personal fact about the user. "
        "Call this whenever the user states something about themselves: "
        "their name, preferences, routines, work, relationships, etc. "
        "Examples: key='name' value='Amogh', key='wake_time' value='7am', "
        "key='job' value='software engineer'."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Short snake_case label, e.g. 'name', 'city', 'preferred_language'"},
            "value": {"type": "string", "description": "The fact value"},
        },
        "required": ["key", "value"],
    },
    handler=_remember_fact,
)

register_tool(
    name="recall_fact",
    description="Look up a specific stored fact by key.",
    input_schema={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "The fact key to look up"},
        },
        "required": ["key"],
    },
    handler=_recall_fact,
)

register_tool(
    name="store_memory",
    description=(
        "Store an important piece of information for later retrieval. "
        "Use this for events, decisions, conversations, or anything the user "
        "might want Jarvis to remember in future sessions."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "The information to remember"},
        },
        "required": ["content"],
    },
    handler=_store_memory,
)

register_tool(
    name="search_memories",
    description="Search past memories for context relevant to the current conversation.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for"},
        },
        "required": ["query"],
    },
    handler=_search_memories,
)
