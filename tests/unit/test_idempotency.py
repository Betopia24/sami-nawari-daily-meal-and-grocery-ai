import pytest

@pytest.mark.asyncio
async def test_idempotency_returns_cached_result(container):
    calls=0
    async def factory():
        nonlocal calls; calls+=1; return {'value':calls}
    first,cached1=await container.idempotency.execute(scope='x',user_id='u',key='k',factory=factory)
    second,cached2=await container.idempotency.execute(scope='x',user_id='u',key='k',factory=factory)
    assert first==second=={'value':1}
    assert cached1 is False and cached2 is True and calls==1
