from sqlalchemy import select, text

from db.connection import get_session
from db.models import SemanticMemory
from providers import get_provider

TOP_K = 5


async def store_memory(content: str) -> None:
    provider = get_provider()
    embedding = await provider.embed(content)

    async for session in get_session():
        session.add(SemanticMemory(content=content, embedding=embedding))
        await session.commit()


async def retrieve_memories(query: str, top_k: int = TOP_K) -> str:
    provider = get_provider()
    embedding = await provider.embed(query)

    async for session in get_session():
        result = await session.execute(
            select(SemanticMemory.content)
            .order_by(SemanticMemory.embedding.cosine_distance(embedding))
            .limit(top_k)
        )
        rows = result.scalars().all()

    if not rows:
        return "No relevant memories found."
    return "\n".join(f"- {row}" for row in rows)
