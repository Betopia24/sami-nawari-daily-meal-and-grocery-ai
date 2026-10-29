import pytest
from httpx import AsyncClient,ASGITransport
from tests.support.fixtures import SELLER_USER_ID

@pytest.mark.asyncio
async def test_health_live(app):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.get('/health/live'); assert r.status_code==200

@pytest.mark.asyncio
async def test_food_recommendation_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/recommendations/foods',headers=headers,json={'limit':5,'meal_type':'lunch'})
        assert r.status_code==200
        assert r.json()['data']['items'][0]['item_id']=='f1'

@pytest.mark.asyncio
async def test_meal_plan_idempotency_endpoint(app,headers):
    h={**headers,'Idempotency-Key':'same-key'}
    payload={'start_date':'2026-08-26','days':1,'meals_per_day':['lunch']}
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        a=await client.post('/internal/v1/meal-plans/generate',headers=h,json=payload)
        b=await client.post('/internal/v1/meal-plans/generate',headers=h,json=payload)
        assert a.status_code==b.status_code==200
        assert a.json()['data']['generation_id']==b.json()['data']['generation_id']
        assert b.json()['meta']['cached'] is True

@pytest.mark.asyncio
async def test_compatibility_batch_endpoint(app,headers):
    payload={'items':[{'resource_type':'food','resource_id':'f1'},{'resource_type':'food','resource_id':'bad'}]}
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/compatibility/check-batch',headers=headers,json=payload)
        statuses=[x['status'] for x in r.json()['data']['items']]
        assert statuses==['safe','conflict']

@pytest.mark.asyncio
async def test_seller_recipe_endpoint(app,headers):
    h={**headers,'X-User-ID':str(SELLER_USER_ID),'Idempotency-Key':'recipe-key'}
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/seller-foods/sf1/recipe-drafts/generate',headers=h,json={'language':'en'})
        assert r.status_code==200
        assert r.json()['data']['recipe']['title']=='Chicken Khichuri'


@pytest.mark.asyncio
async def test_recipe_recommendation_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/recommendations/recipes',headers=headers,json={'limit':5})
        assert r.status_code==200
        assert 'bad' not in [x['item_id'] for x in r.json()['data']['items']]

@pytest.mark.asyncio
async def test_replacement_options_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/meal-plans/mp1/items/r1/replacement-options',headers=headers,json={'preference':'fish','limit':3})
        assert r.status_code==200
        assert r.json()['data']['options'][0]['recipe_id']=='r2'

@pytest.mark.asyncio
async def test_nutrition_insight_endpoint(app,headers):
    h={**headers,'Idempotency-Key':'insight-key'}
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/meal-plans/mp1/insights',headers=h)
        assert r.status_code==200
        assert r.json()['data']['nutrition']['calories']==1600

@pytest.mark.asyncio
async def test_grocery_from_meal_plan_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/grocery-drafts/from-meal-plan',headers=headers,json={'meal_plan_id':'mp1'})
        assert r.status_code==200
        rice=next(x for x in r.json()['data']['items'] if x['ingredient_id']=='rice')
        assert rice['quantity']==400

@pytest.mark.asyncio
async def test_grocery_from_recipe_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/grocery-drafts/from-recipe',headers=headers,json={'recipe_id':'r1','servings':4})
        assert r.status_code==200
        rice=next(x for x in r.json()['data']['items'] if x['ingredient_id']=='rice')
        assert rice['quantity']==400

@pytest.mark.asyncio
async def test_seller_recipe_regenerate_endpoint(app,headers):
    h={**headers,'X-User-ID':str(SELLER_USER_ID),'Idempotency-Key':'recipe-first'}
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        first=await client.post('/internal/v1/seller-foods/sf1/recipe-drafts/generate',headers=h,json={'language':'en'})
        gid=first.json()['data']['generation_id']
        h2={**headers,'X-User-ID':str(SELLER_USER_ID),'Idempotency-Key':'recipe-regen'}
        r=await client.post('/internal/v1/seller-foods/sf1/recipe-drafts/regenerate',headers=h2,json={'previous_generation_id':gid,'instructions':'Make it shorter.'})
        assert r.status_code==200
        assert 'Updated request' in r.json()['data']['recipe']['summary']

@pytest.mark.asyncio
async def test_compatibility_single_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/compatibility/check',headers=headers,json={'resource_type':'food','resource_id':'bad'})
        assert r.status_code==200
        assert r.json()['data']['status']=='conflict'

@pytest.mark.asyncio
async def test_recommendation_event_endpoint(app,headers,container):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/recommendation-events',headers=headers,json={'recommendation_id':'rec1','item_type':'food','item_id':'f1','event':'clicked'})
        assert r.status_code==204
        assert container.event_repo.events[-1]['item_id']=='f1'

@pytest.mark.asyncio
async def test_profile_cache_invalidation_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        r=await client.post('/internal/v1/users/11111111-1111-1111-1111-111111111111/profile-cache/invalidate',headers=headers,json={'profile_version':4})
        assert r.status_code==200 and r.json()['data']['invalidated'] is True


@pytest.mark.asyncio
async def test_latest_nutrition_insight_endpoint(app,headers):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        generated=await client.post('/internal/v1/meal-plans/mp1/insights',headers={**headers,'Idempotency-Key':'latest-insight'},json=None)
        assert generated.status_code==200
        latest=await client.get('/internal/v1/meal-plans/mp1/insights/latest',headers=headers)
        assert latest.status_code==200
        assert latest.json()['data']['generation_id']==generated.json()['data']['generation_id']
        assert latest.json()['meta']['cached'] is True
