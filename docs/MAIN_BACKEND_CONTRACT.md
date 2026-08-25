# Main Backend → AI Service Contract

The AI service is private. The main backend must authenticate users and pass only the verified user UUID in `X-User-ID`.

## AI profile
`GET /internal/ai/users/{user_id}/profile`

Required data: `user_id`, `profile_version`, dietary preferences, allergies, preferred cuisines, nutrition goal, household size, cooking frequency and language. Favorites/behavior signals are optional.

## Food candidates
`GET /internal/ai/foods/candidates?user_id=&limit=&meal_type=`

Return structured food records including seller ID, cuisine, availability, rating/popularity and canonical ingredient records. Ingredient allergen metadata must be verified by the main backend dataset.

## Recipe candidates
`GET /internal/ai/recipes/candidates?user_id=&limit=&meal_type=`

Return recipe ID, cuisine, meal/diet/goal tags, servings, ingredient quantities/units and nutrition per serving.

## Resource reads
- `GET /internal/ai/foods/{food_id}`
- `GET /internal/ai/recipes/{recipe_id}`
- `GET /internal/ai/meal-plans/{plan_id}?user_id={uuid}`
- `GET /internal/ai/seller-foods/{food_id}/draft?seller_user_id={uuid}`

The main backend must enforce ownership for meal-plan and seller-food reads. The AI service never trusts a resource ID as proof of access.
