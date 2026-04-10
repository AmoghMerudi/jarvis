from sqlalchemy import select

from db.connection import get_session
from db.models import ExplicitFact


async def set_fact(key: str, value: str) -> None:
    async for session in get_session():
        result = await session.execute(
            select(ExplicitFact).where(ExplicitFact.key == key)
        )
        fact = result.scalar_one_or_none()
        if fact:
            fact.value = value
        else:
            session.add(ExplicitFact(key=key, value=value))
        await session.commit()


async def get_fact(key: str) -> str | None:
    async for session in get_session():
        result = await session.execute(
            select(ExplicitFact.value).where(ExplicitFact.key == key)
        )
        return result.scalar_one_or_none()


async def get_all_facts() -> str:
    async for session in get_session():
        result = await session.execute(select(ExplicitFact))
        facts = result.scalars().all()

    if not facts:
        return "No explicit facts stored yet."
    return "\n".join(f"- {f.key}: {f.value}" for f in facts)
