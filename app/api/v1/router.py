from fastapi import APIRouter
from app.api.v1 import recommendations,meal_plans,grocery,seller_recipes,compatibility,recommendation_events,profiles

router=APIRouter(prefix='/internal/v1')
router.include_router(recommendations.router)
router.include_router(meal_plans.router)
router.include_router(grocery.router)
router.include_router(seller_recipes.router)
router.include_router(compatibility.router)
router.include_router(recommendation_events.router)
router.include_router(profiles.router)
