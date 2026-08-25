import pytest
from app.services.rate_limit import RateLimiterService
from app.infrastructure.cache.memory import MemoryCache
from app.core.errors import RateLimited

@pytest.mark.asyncio
async def test_rate_limiter_blocks_after_limit():
    limiter=RateLimiterService(MemoryCache(),2)
    await limiter.check(user_id='u',feature='x')
    await limiter.check(user_id='u',feature='x')
    with pytest.raises(RateLimited):
        await limiter.check(user_id='u',feature='x')
