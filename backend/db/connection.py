import os
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base

engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker | None = None


async def init_db() -> None:
    global engine, AsyncSessionLocal

    database_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(database_url, echo=False)

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with AsyncSessionLocal() as session:
        yield session
