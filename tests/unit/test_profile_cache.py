import pytest
from tests.support.fixtures import USER_ID

@pytest.mark.asyncio
async def test_profile_is_cached_and_invalidated(container,main_backend):
    first=await container.profile_service.get(USER_ID)
    main_backend.profiles[USER_ID]=first.model_copy(update={'profile_version':99})
    cached=await container.profile_service.get(USER_ID)
    assert cached.profile_version==3
    await container.profile_service.invalidate(USER_ID)
    refreshed=await container.profile_service.get(USER_ID)
    assert refreshed.profile_version==99
