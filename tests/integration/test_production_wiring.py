
import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.core.config import Settings
from app.container import build_production_container
from app.main import create_app
from tests.support.fixtures import USER_ID

pytestmark=pytest.mark.integration

@pytest.mark.asyncio
async def test_production_container_with_docker_services_and_http_main_backend():
    if os.getenv('RUN_INTEGRATION')!='1':
        pytest.skip('Run through docker-compose.test.yml')
    settings=Settings(
        app_env='test',
        database_url=os.environ['DATABASE_URL'],
        redis_url=os.environ['REDIS_URL'],
        main_backend_base_url=os.environ['MAIN_BACKEND_BASE_URL'],
        llm_provider='fake',
    )
    container=build_production_container(settings)
    app=create_app(container=container,settings=settings)
    headers={'X-User-ID':str(USER_ID),'Idempotency-Key':'docker-plan-1'}
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
            rec=await client.post('/internal/v1/recommendations/foods',headers=headers,json={'limit':5,'meal_type':'lunch'})
            assert rec.status_code==200
            plan=await client.post('/internal/v1/meal-plans/generate',headers=headers,json={'start_date':'2026-08-26','days':1,'meals_per_day':['lunch']})
            assert plan.status_code==200
            assert plan.json()['data']['plan']['days'][0]['meals'][0]['recipe_id'] in {'r1','r2'}
    finally:
        await container.close()
