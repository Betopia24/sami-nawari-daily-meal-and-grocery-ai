from uuid import UUID, uuid4
from app.domain.enums import ResourceType
from app.domain.schemas import RecommendationResult, RecommendationItem


class RecommendationScorer:
    def score_food(self, profile, item) -> tuple[float,list[str]]:
        score=0.15; reasons=[]
        if item.cuisine and item.cuisine.lower() in {x.lower() for x in profile.preferred_cuisines}:
            score+=0.25; reasons.append('matches_cuisine')
        if profile.nutrition_goal and profile.nutrition_goal.lower() in {x.lower() for x in item.goal_tags}:
            score+=0.20; reasons.append('matches_goal')
        if item.seller_id in profile.favorite_seller_ids:
            score+=0.10; reasons.append('favorite_seller')
        score+=min(item.rating/5,1)*0.15
        score+=min(max(item.popularity_score,0),1)*0.10
        if item.distance_km is not None:
            score+=max(0, 0.05*(1-min(item.distance_km/20,1)))
        return min(score,1.0), reasons

    def score_recipe(self, profile, item) -> tuple[float,list[str]]:
        score=0.15; reasons=[]
        if item.cuisine and item.cuisine.lower() in {x.lower() for x in profile.preferred_cuisines}:
            score+=0.30; reasons.append('preferred_cuisine')
        if profile.nutrition_goal and profile.nutrition_goal.lower() in {x.lower() for x in item.goal_tags}:
            score+=0.25; reasons.append('goal_match')
        score+=min(item.rating/5,1)*0.15
        score+=min(max(item.popularity_score,0),1)*0.15
        return min(score,1.0), reasons


class RecommendationService:
    def __init__(self, profile_service, main_backend, compatibility, scorer, candidate_limit: int = 200) -> None:
        self._profiles=profile_service; self._main=main_backend; self._compat=compatibility; self._scorer=scorer; self._candidate_limit=candidate_limit

    async def foods(self, user_id: UUID, request) -> RecommendationResult:
        profile=await self._profiles.get(user_id)
        candidates=await self._main.list_food_candidates(user_id,self._candidate_limit,request.meal_type)
        ranked=[]
        for item in candidates:
            if item.food_id in request.exclude_food_ids or not item.available: continue
            comp=self._compat.check(profile,ResourceType.FOOD,item.food_id,item.ingredients,item.dietary_tags)
            if comp.status.value != 'safe': continue
            score,reasons=self._scorer.score_food(profile,item)
            ranked.append(RecommendationItem(item_id=item.food_id,score=round(score,4),compatibility=comp.status,reasons=reasons))
        ranked.sort(key=lambda x:x.score,reverse=True)
        return RecommendationResult(recommendation_id=f'rec_{uuid4().hex}',items=ranked[:request.limit])

    async def recipes(self, user_id: UUID, request) -> RecommendationResult:
        profile=await self._profiles.get(user_id)
        candidates=await self._main.list_recipe_candidates(user_id,self._candidate_limit,request.meal_type)
        ranked=[]
        for item in candidates:
            if item.recipe_id in request.exclude_recipe_ids: continue
            if request.max_cooking_time_minutes and item.prep_time_minutes+item.cook_time_minutes>request.max_cooking_time_minutes: continue
            comp=self._compat.check(profile,ResourceType.RECIPE,item.recipe_id,item.ingredients,item.dietary_tags)
            if comp.status.value != 'safe': continue
            score,reasons=self._scorer.score_recipe(profile,item)
            ranked.append(RecommendationItem(item_id=item.recipe_id,score=round(score,4),compatibility=comp.status,reasons=reasons))
        ranked.sort(key=lambda x:x.score,reverse=True)
        return RecommendationResult(recommendation_id=f'rec_{uuid4().hex}',items=ranked[:request.limit])
