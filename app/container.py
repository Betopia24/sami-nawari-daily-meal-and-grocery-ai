from dataclasses import dataclass
from app.core.config import Settings
from app.infrastructure.cache.memory import MemoryCache
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.llm.fake import FakeLLMProvider
from app.infrastructure.llm.openai import OpenAILLMProvider
from app.infrastructure.main_backend.http import HttpMainBackendClient
from app.infrastructure.db.session import Database
from app.infrastructure.db.repositories import (
    SQLGenerationRepository, SQLRecommendationEventRepository, DBHealthRepository,
    InMemoryGenerationRepository, InMemoryRecommendationEventRepository, InMemoryHealthRepository,
)
from app.services.profile import AIProfileService
from app.services.compatibility import CompatibilityEngine
from app.services.compatibility_service import CompatibilityService
from app.services.recommendation import RecommendationService, RecommendationScorer
from app.services.meal_planning import MealPlanningService, MealPlanValidator
from app.services.nutrition import NutritionInsightService, NutritionCalculator
from app.services.grocery import GroceryGeneratorService, UnitNormalizer
from app.services.seller_recipe import SellerRecipeService, SellerRecipeValidator
from app.services.events import RecommendationEventService
from app.services.idempotency import IdempotencyService
from app.services.rate_limit import RateLimiterService


@dataclass
class AppContainer:
    settings: Settings
    cache: object
    main_backend: object
    llm: object
    generation_repo: object
    event_repo: object
    health_repo: object
    database: object | None = None

    def __post_init__(self) -> None:
        self.profile_service=AIProfileService(self.main_backend,self.cache,self.settings.redis_profile_ttl_seconds)
        self.compatibility_engine=CompatibilityEngine()
        self.compatibility_service=CompatibilityService(self.profile_service,self.main_backend,self.compatibility_engine)
        self.recommendation_service=RecommendationService(self.profile_service,self.main_backend,self.compatibility_engine,RecommendationScorer(),self.settings.recommendation_candidate_limit)
        self.meal_planning_service=MealPlanningService(self.profile_service,self.main_backend,self.compatibility_engine,self.llm,self.generation_repo,MealPlanValidator(),self.settings.recommendation_candidate_limit)
        self.nutrition_service=NutritionInsightService(self.profile_service,self.main_backend,self.llm,self.generation_repo,NutritionCalculator())
        self.grocery_service=GroceryGeneratorService(self.profile_service,self.main_backend,UnitNormalizer())
        self.seller_recipe_service=SellerRecipeService(self.main_backend,self.llm,self.generation_repo,SellerRecipeValidator())
        self.event_service=RecommendationEventService(self.event_repo)
        self.idempotency=IdempotencyService(self.cache,self.settings.idempotency_ttl_seconds)
        self.rate_limiter=RateLimiterService(self.cache,self.settings.generative_rate_limit_per_minute)

    async def close(self) -> None:
        for obj in (self.main_backend,self.cache,self.database):
            if obj is not None and hasattr(obj,'close'):
                await obj.close()


def build_production_container(settings: Settings) -> AppContainer:
    cache=RedisCache(settings.redis_url)
    main_backend=HttpMainBackendClient(settings.main_backend_base_url,settings.main_backend_service_token,settings.main_backend_timeout_seconds)
    if settings.llm_provider=='fake':
        llm=FakeLLMProvider()
    else:
        if not settings.openai_api_key:
            raise RuntimeError('OPENAI_API_KEY is required when LLM_PROVIDER=openai')
        llm=OpenAILLMProvider(api_key=settings.openai_api_key,model=settings.openai_model,timeout_seconds=settings.openai_timeout_seconds,max_retries=settings.openai_max_retries)
    database=Database(settings.database_url)
    return AppContainer(settings,cache,main_backend,llm,SQLGenerationRepository(database.session_factory),SQLRecommendationEventRepository(database.session_factory),DBHealthRepository(database),database)
