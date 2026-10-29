# AI Server Integration Guide for Main Backend

এই ডকুমেন্টটি Main Backend developer-এর জন্য। AI Server চালাতে Main Backend-এ কোন internal endpoint লাগবে, কী data পাঠাতে হবে এবং Main Backend থেকে AI Server কীভাবে call করতে হবে—এখানে দেওয়া আছে।

## 1. Architecture

- User login, user identity, food, recipe, meal plan এবং seller data-এর source of truth হবে Main Backend।
- AI Server recommendation, compatibility check, meal-plan generation, nutrition insight, grocery draft এবং seller recipe generation করবে।
- Main Backend authenticated user-এর behalf-এ AI Server call করবে।
- AI Server Main Backend থেকে data নেওয়ার জন্য নিচের internal `GET` endpointগুলো call করবে।
- বর্তমান simplified setup-এ service token ব্যবহার করা হচ্ছে না। তাই AI Server এবং Main Backend private network/localhost/internal Docker network-এ রাখতে হবে।

## 2. Required headers when calling AI Server

Personalized AI endpoint-এ Main Backend-কে পাঠাতে হবে:

```http
X-User-ID: <authenticated-user-uuid>
X-Request-ID: <optional-request-id>
```

Generation endpoint-এ duplicate request ঠেকানোর জন্য পাঠানো উচিত:

```http
Idempotency-Key: <unique-operation-key>
```

`X-User-ID` অবশ্যই Main Backend-এর authenticated user থেকে set করতে হবে। Client-এর পাঠানো arbitrary `X-User-ID` সরাসরি trust করবেন না।

## 3. Main Backend-এ যেসব endpoint অবশ্যই লাগবে

AI Server বর্তমানে Main Backend-এ এই endpointগুলো call করে:

| Method | Endpoint | ব্যবহার |
|---|---|---|
| GET | `/internal/ai/users/{user_id}/profile` | User-এর AI profile নেওয়া |
| GET | `/internal/ai/foods/candidates` | Food recommendation-এর candidate নেওয়া |
| GET | `/internal/ai/recipes/candidates` | Recipe recommendation/meal plan-এর candidate নেওয়া |
| GET | `/internal/ai/foods/{food_id}` | একটি food-এর বিস্তারিত data |
| GET | `/internal/ai/recipes/{recipe_id}` | একটি recipe-এর বিস্তারিত data |
| GET | `/internal/ai/meal-plans/{plan_id}` | User-এর meal plan নেওয়া |
| GET | `/internal/ai/seller-foods/{food_id}/draft` | Seller food থেকে recipe draft-এর input নেওয়া |

### Response format

AI Server `data` wrapper থাকলে এবং না থাকলেও response parse করতে পারে। Consistency-এর জন্য এই format ব্যবহার করা ভালো:

```json
{
  "data": {}
}
```

404 হলে resource না পাওয়া, আর 403 হলে resource ownership না মেলার response দিতে হবে।

### 3.1 User AI profile

```http
GET /internal/ai/users/{user_id}/profile
```

Example response:

```json
{
  "data": {
    "user_id": "11111111-1111-1111-1111-111111111111",
    "profile_version": 3,
    "dietary_preferences": ["halal"],
    "allergies": ["peanut"],
    "preferred_cuisines": ["bangladeshi"],
    "nutrition_goal": "healthy",
    "household_size": 4,
    "cooking_frequency": "daily",
    "language": "en",
    "favorite_seller_ids": ["seller-1"],
    "behavior_affinity": {
      "rice": 0.8,
      "chicken": 0.7
    }
  }
}
```

Required/important fields:

- `user_id`: UUID string
- `profile_version`: integer
- `dietary_preferences`: string array
- `allergies`: string array
- `preferred_cuisines`: string array
- `nutrition_goal`: string or `null`
- `household_size`: integer, 1–20
- `cooking_frequency`: string or `null`
- `language`: string
- `favorite_seller_ids`: string array
- `behavior_affinity`: string-to-number object

### 3.2 Food candidates

```http
GET /internal/ai/foods/candidates?user_id=<uuid>&limit=200&meal_type=lunch
```

Query parameters:

- `user_id`: required UUID
- `limit`: required; AI Server normally sends up to 200
- `meal_type`: optional, for example `breakfast`, `lunch`, `dinner`

Response is a food array:

```json
{
  "data": [
    {
      "food_id": "food-123",
      "seller_id": "seller-1",
      "name": "Chicken Rice",
      "cuisine": "bangladeshi",
      "meal_types": ["lunch", "dinner"],
      "dietary_tags": ["halal"],
      "goal_tags": ["healthy"],
      "ingredients": [
        {
          "ingredient_id": "rice",
          "name": "Rice",
          "quantity": 200,
          "unit": "g",
          "category": "grain",
          "allergens": [],
          "flags": [],
          "verified": true
        }
      ],
      "rating": 4.6,
      "popularity_score": 0.8,
      "distance_km": 2.5,
      "available": true
    }
  ]
}
```

`rating` 0–5 এবং `popularity_score` 0–1-এর মধ্যে দিতে হবে। `available: false` হলে AI recommendation-এ item বাদ যাবে।

### 3.3 Recipe candidates

```http
GET /internal/ai/recipes/candidates?user_id=<uuid>&limit=200&meal_type=dinner
```

Query parameters:

- `user_id`: required UUID
- `limit`: required
- `meal_type`: optional

প্রতিটি recipe object-এ অন্তত এই fieldগুলো লাগবে:

```json
{
  "recipe_id": "recipe-123",
  "title": "Chicken Khichuri",
  "cuisine": "bangladeshi",
  "meal_types": ["lunch", "dinner"],
  "dietary_tags": ["halal"],
  "goal_tags": ["healthy"],
  "ingredients": [],
  "servings": 4,
  "prep_time_minutes": 15,
  "cook_time_minutes": 35,
  "rating": 4.7,
  "popularity_score": 0.85,
  "nutrition_per_serving": {
    "calories": 420,
    "protein_g": 25,
    "carbs_g": 55,
    "fat_g": 12,
    "fiber_g": 6,
    "sugar_g": 3,
    "sodium_mg": 480
  },
  "seller_id": "seller-1"
}
```

`ingredients`-এর প্রতিটি item-এর format Food candidate-এর মতো হবে।

### 3.4 Single food

```http
GET /internal/ai/foods/{food_id}
```

Response-এ 3.2-এর একটি পূর্ণ `FoodItem` object দিতে হবে। Compatibility check-এর জন্য `ingredients` এবং `dietary_tags` সঠিক হওয়া জরুরি।

### 3.5 Single recipe

```http
GET /internal/ai/recipes/{recipe_id}
```

Response-এ 3.3-এর একটি পূর্ণ `Recipe` object দিতে হবে। Grocery এবং nutrition calculation-এর জন্য `servings`, `ingredients` এবং `nutrition_per_serving` সঠিক হওয়া জরুরি।

### 3.6 Meal plan

```http
GET /internal/ai/meal-plans/{plan_id}?user_id=<uuid>
```

Main Backend-কে ownership verify করতে হবে—plan-টি অবশ্যই query-এর `user_id`-এর হতে হবে। Ownership না মিললে `403` দিতে হবে।

Example response:

```json
{
  "data": {
    "plan_id": "plan-123",
    "user_id": "11111111-1111-1111-1111-111111111111",
    "version": 2,
    "days": [
      {
        "date": "2026-10-28",
        "meals": [
          {
            "meal_type": "lunch",
            "recipe_id": "recipe-123",
            "servings": 2
          }
        ]
      }
    ]
  }
}
```

### 3.7 Seller food draft

```http
GET /internal/ai/seller-foods/{food_id}/draft?seller_user_id=<uuid>
```

Main Backend-কে seller ownership verify করতে হবে। Example response:

```json
{
  "data": {
    "food_id": "food-123",
    "seller_user_id": "22222222-2222-2222-2222-222222222222",
    "seller_id": "seller-1",
    "name": "Chicken Khichuri",
    "cuisine": "bangladeshi",
    "servings": 4,
    "prep_time_minutes": 15,
    "cook_time_minutes": 35,
    "preparation_notes": "Wash rice before cooking",
    "cooking_method": "stovetop",
    "ingredients": [],
    "details": "Seller-provided food details"
  }
}
```

## 4. Main Backend থেকে যেসব AI endpoint call করতে হবে

Main Backend authenticated user-এর request receive করে নিচের AI endpointগুলো call/proxy করতে পারবে। প্রতিটি personalized request-এ `X-User-ID` পাঠাতে হবে।

| Method | AI endpoint | ব্যবহার |
|---|---|---|
| POST | `/internal/v1/recommendations/foods` | Personalized food recommendation |
| POST | `/internal/v1/recommendations/recipes` | Personalized recipe recommendation |
| POST | `/internal/v1/meal-plans/generate` | AI meal plan generate |
| POST | `/internal/v1/meal-plans/{plan_id}/items/{item_id}/replacement-options` | Meal replacement options |
| POST | `/internal/v1/meal-plans/{plan_id}/insights` | Nutrition insight generate |
| GET | `/internal/v1/meal-plans/{plan_id}/insights/latest` | সর্বশেষ nutrition insight |
| POST | `/internal/v1/grocery-drafts/from-meal-plan` | Meal plan থেকে grocery draft |
| POST | `/internal/v1/grocery-drafts/from-recipe` | Recipe থেকে grocery draft |
| POST | `/internal/v1/seller-foods/{food_id}/recipe-drafts/generate` | Seller food থেকে recipe draft |
| POST | `/internal/v1/seller-foods/{food_id}/recipe-drafts/regenerate` | Recipe draft regenerate |
| POST | `/internal/v1/compatibility/check` | একটি food/recipe compatibility check |
| POST | `/internal/v1/compatibility/check-batch` | একাধিক compatibility check |
| POST | `/internal/v1/recommendation-events` | impression/click/save/order event record |
| POST | `/internal/v1/users/{user_id}/profile-cache/invalidate` | Profile update হলে AI cache invalidate |

### Request body examples

Food recommendation:

```json
{
  "limit": 20,
  "meal_type": "lunch",
  "delivery_zone_id": "zone-1",
  "exclude_food_ids": []
}
```

Recipe recommendation:

```json
{
  "limit": 20,
  "meal_type": "dinner",
  "max_cooking_time_minutes": 60,
  "exclude_recipe_ids": []
}
```

Meal plan generation:

```json
{
  "start_date": "2026-10-28",
  "days": 7,
  "meals_per_day": ["breakfast", "lunch", "dinner"],
  "goal_override": null,
  "excluded_recipe_ids": []
}
```

Grocery from meal plan:

```json
{
  "meal_plan_id": "plan-123"
}
```

Grocery from recipe:

```json
{
  "recipe_id": "recipe-123",
  "servings": 4
}
```

Compatibility check:

```json
{
  "resource_type": "recipe",
  "resource_id": "recipe-123"
}
```

Compatibility batch:

```json
{
  "items": [
    {"resource_type": "food", "resource_id": "food-123"},
    {"resource_type": "recipe", "resource_id": "recipe-123"}
  ]
}
```

Seller recipe generation:

```json
{
  "language": "en"
}
```

Seller recipe regeneration:

```json
{
  "previous_generation_id": "gen_recipe_abc123",
  "instructions": "Make it less spicy and shorter."
}
```

Profile cache invalidation:

```json
{
  "profile_version": 4
}
```

Recommendation event:

```json
{
  "recommendation_id": "rec_abc123",
  "item_type": "food",
  "item_id": "food-123",
  "event": "clicked"
}
```

Allowed event values: `impression`, `clicked`, `saved`, `ordered`, `dismissed`.

## 5. AI response format

সাধারণ AI response:

```json
{
  "request_id": "req_abc123",
  "data": {},
  "meta": {
    "cached": false
  }
}
```

Error response:

```json
{
  "request_id": "req_abc123",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Meal plan not found",
    "retryable": false
  }
}
```

Important status codes:

- `400` — invalid business request
- `403` — user/seller/resource ownership mismatch
- `404` — profile, food, recipe বা meal plan পাওয়া যায়নি
- `422` — validation error বা insufficient data
- `429` — AI generation rate limit
- `502` — AI generation/output validation failure; retryable হতে পারে
- `204` — recommendation event successfully recorded

## 6. Important integration notes

- Main Backend-কে user authentication এবং authorization করতে হবে। AI Server-এ পাঠানো `X-User-ID` authenticated user-এর ID হতে হবে।
- AI Server-এ direct mobile/client access না দিয়ে Main Backend-এর মাধ্যমে access দিন।
- `/internal/ai/meal-plans/{plan_id}` এবং seller food draft endpoint-এ ownership validation Main Backend-এ করতে হবে।
- Recipe ingredient-এর `ingredient_id` stable/canonical রাখুন। Compatibility এবং grocery calculation এটির উপর নির্ভর করে।
- Ingredient-এর `quantity` অবশ্যই positive number এবং `unit` consistent রাখুন; যেমন `g`, `kg`, `ml`, `l`, `pc`।
- Recipe-এর `servings` positive হতে হবে। Grocery quantity scale করার সময় AI Server এটি ব্যবহার করে।
- Meal plan replacement endpoint-এর বর্তমান compact model-এ `{item_id}` হিসেবে recipe ID match করা হয়। Main Backend-এর meal item ID recipe ID থেকে আলাদা হলে AI Server model update করতে হবে।
- Profile বা dietary/allergy data update হলে profile cache invalidate endpoint call করুন।
- Generation endpoint-এ একই operation-এর জন্য stable `Idempotency-Key` ব্যবহার করুন।

## 7. Health checks

Main Backend integration check করার জন্য AI Server:

```http
GET /health/live
GET /health/ready
```

`/health/ready` response-এ database এবং Redis status দেখাবে।

## 8. Minimum implementation checklist

- [ ] User AI profile endpoint
- [ ] Food candidates endpoint
- [ ] Recipe candidates endpoint
- [ ] Single food endpoint
- [ ] Single recipe endpoint
- [ ] Meal plan endpoint with ownership check
- [ ] Seller food draft endpoint with seller ownership check
- [ ] Stable ingredient and recipe schema
- [ ] Main Backend থেকে AI endpoint call/proxy
- [ ] `X-User-ID` authenticated user ID হিসেবে set করা
- [ ] Private network/firewall configuration
- [ ] Profile update হলে cache invalidation call
- [ ] Generation request-এ idempotency key
