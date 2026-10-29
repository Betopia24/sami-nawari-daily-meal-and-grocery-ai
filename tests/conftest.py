import pytest
from app.core.config import Settings
from app.container import AppContainer
from app.infrastructure.cache.memory import MemoryCache
from app.infrastructure.llm.fake import FakeLLMProvider
from app.infrastructure.main_backend.in_memory import InMemoryMainBackendClient
from app.infrastructure.db.repositories import InMemoryGenerationRepository,InMemoryRecommendationEventRepository,InMemoryHealthRepository
from app.main import create_app
from tests.support.fixtures import USER_ID,SELLER_USER_ID,profile,food,recipe,meal_plan,seller_food

@pytest.fixture
def main_backend():
    c=InMemoryMainBackendClient(); c.profiles[USER_ID]=profile(); c.profiles[SELLER_USER_ID]=profile().model_copy(update={'user_id':SELLER_USER_ID})
    c.foods['f1']=food('f1'); c.foods['f2']=food('f2',rating=3.5); c.foods['bad']=food('bad',ingredients=__import__('tests.support.fixtures',fromlist=['ingredients_peanut']).ingredients_peanut())
    c.recipes['r1']=recipe('r1'); c.recipes['r2']=recipe('r2','Fish Rice',calories=350); c.recipes['bad']=recipe('bad','Peanut Dish',ingredients=__import__('tests.support.fixtures',fromlist=['ingredients_peanut']).ingredients_peanut())
    c.meal_plans['mp1']=meal_plan(); c.seller_foods['sf1']=seller_food(); return c

@pytest.fixture
def container(main_backend):
    settings=Settings(llm_provider='fake')
    return AppContainer(settings,MemoryCache(),main_backend,FakeLLMProvider(),InMemoryGenerationRepository(),InMemoryRecommendationEventRepository(),InMemoryHealthRepository())

@pytest.fixture
def app(container): return create_app(container=container,settings=container.settings)

@pytest.fixture
def headers(): return {'X-User-ID':str(USER_ID),'X-Request-ID':'req-test'}
