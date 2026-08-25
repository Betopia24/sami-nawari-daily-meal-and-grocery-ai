from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


class Database:
    def __init__(self, url: str) -> None:
        self.engine: AsyncEngine = create_async_engine(url, pool_pre_ping=True, pool_recycle=1800)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def ping(self) -> bool:
        from sqlalchemy import text
        async with self.engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        return True

    async def close(self) -> None:
        await self.engine.dispose()
