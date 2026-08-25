# Food AI Backend — Production MVP

A dedicated FastAPI AI service for the locked MVP intelligence layer of the food ecosystem. The main backend remains the source of truth for users, sellers, foods, recipes, meal plans, orders and grocery lists. This service provides personalized intelligence using a verified `X-User-ID` supplied only by the authenticated main backend.

## Locked MVP AI features

1. Personalized Food Recommendation
2. AI Meal Plan Generator
3. Smart Meal Replacement / Regeneration
4. AI Nutrition Insights
5. Personalized Recipe Recommendation
6. Smart Grocery List Generator
7. Seller Food Data → AI Recipe Generation
8. Dietary & Allergy Compatibility Engine

Natural-language smart search is intentionally **not** part of this MVP.

## Architecture principles

- **Private service**: Flutter should call the main backend, not this service directly.
- **User personalization**: main backend resolves identity; AI requests include `X-User-ID`.
- **OpenAI only where generation is useful**: meal-plan composition, free-form replacement intent, insight narration and seller recipe generation.
- **Deterministic safety/calculation**: compatibility, grocery quantities and nutrition numbers never depend on LLM arithmetic.
- **Modular monolith**: one deployable AI service with OOP service classes and clear ports/adapters.
- **Dockerized infrastructure**: FastAPI, PostgreSQL + pgvector, Redis.
- **Human in the loop**: seller-generated recipe is a draft and must be approved by the seller/main backend before publication.

## OpenAI

`OPENAI_MODEL` defaults to `gpt-5.6`, matching the current OpenAI Responses API quickstart at project generation time (2026-08-25). The model is environment-configurable so a future model upgrade requires no business-code changes.

The adapter uses the Responses API structured parsing interface and Pydantic output models.

## Start

```bash
cp .env.example .env
# Fill OPENAI_API_KEY and change service tokens.
docker compose up --build
```

API: `http://localhost:8000`  
Development docs: `http://localhost:8000/docs`

## Main backend contract expected by this AI service

The production HTTP adapter expects private main-backend routes:

- `GET /internal/ai/users/{user_id}/profile`
- `GET /internal/ai/foods/candidates`
- `GET /internal/ai/recipes/candidates`
- `GET /internal/ai/foods/{food_id}`
- `GET /internal/ai/recipes/{recipe_id}`
- `GET /internal/ai/meal-plans/{plan_id}`
- `GET /internal/ai/seller-foods/{food_id}/draft`

All should be protected with the main-backend service token.

## AI API endpoints

- `POST /internal/v1/recommendations/foods`
- `POST /internal/v1/recommendations/recipes`
- `POST /internal/v1/meal-plans/generate`
- `POST /internal/v1/meal-plans/{plan_id}/items/{item_id}/replacement-options`
- `POST /internal/v1/meal-plans/{plan_id}/insights`
- `GET /internal/v1/meal-plans/{plan_id}/insights/latest`
- `POST /internal/v1/grocery-drafts/from-meal-plan`
- `POST /internal/v1/grocery-drafts/from-recipe`
- `POST /internal/v1/seller-foods/{food_id}/recipe-drafts/generate`
- `POST /internal/v1/seller-foods/{food_id}/recipe-drafts/regenerate`
- `POST /internal/v1/compatibility/check`
- `POST /internal/v1/compatibility/check-batch`
- `POST /internal/v1/recommendation-events`
- `POST /internal/v1/users/{user_id}/profile-cache/invalidate`

Required internal headers for personalized routes:

```http
Authorization: Bearer <INTERNAL_SERVICE_TOKEN>
X-User-ID: <authenticated UUID from main backend>
X-Request-ID: <optional tracing ID>
```

For costly generation routes also send:

```http
Idempotency-Key: <unique operation key>
```

## Tests

Local unit/API tests use in-memory adapters and do **not** call OpenAI:

```bash
pytest -q -m "not integration"
```

Full Docker infrastructure tests:

```bash
make test-integration
```

The Docker test stack starts pgvector PostgreSQL and Redis, runs Alembic migrations, then runs the complete suite with coverage.

## Production checklist

- Replace all default service tokens.
- Keep AI service on a private network; expose only the main backend publicly.
- Use managed secrets rather than committing `.env`.
- Add TLS/mTLS or signed service JWTs if services cross trust boundaries.
- Enable database backups and Redis persistence as required.
- Set container CPU/memory limits at deployment platform level.
- Add metrics/tracing (OpenTelemetry/Prometheus) in your deployment environment.
- Seed and maintain a verified canonical ingredient/allergen dataset in the main backend.
- Treat `unknown` compatibility as not verified; never represent it as safe.
