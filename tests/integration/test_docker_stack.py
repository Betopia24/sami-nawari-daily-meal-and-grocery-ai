import os
import pytest

pytestmark=pytest.mark.integration

@pytest.mark.asyncio
async def test_docker_dependencies_are_reachable():
    if os.getenv('RUN_INTEGRATION')!='1':
        pytest.skip('Set RUN_INTEGRATION=1 inside docker-compose.test.yml')
    from app.infrastructure.cache.redis import RedisCache
    from app.infrastructure.db.session import Database
    cache=RedisCache(os.environ['REDIS_URL']); db=Database(os.environ['DATABASE_URL'])
    try:
        assert await cache.ping() is True
        assert await db.ping() is True
    finally:
        await cache.close(); await db.close()
