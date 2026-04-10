import httpx

from agent.tools import register_tool

DDGS_URL = "https://api.duckduckgo.com/"


async def _web_search(query: str) -> str:
    params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(DDGS_URL, params=params)
        response.raise_for_status()
        data = response.json()

    results = []
    if data.get("AbstractText"):
        results.append(data["AbstractText"])
    for topic in data.get("RelatedTopics", [])[:5]:
        if isinstance(topic, dict) and topic.get("Text"):
            results.append(topic["Text"])

    return "\n\n".join(results) if results else "No results found."


register_tool(
    name="web_search",
    description="Search the web for current information using DuckDuckGo.",
    input_schema={
        "type": "object",
        "properties": {"query": {"type": "string", "description": "Search query"}},
        "required": ["query"],
    },
    handler=_web_search,
)
