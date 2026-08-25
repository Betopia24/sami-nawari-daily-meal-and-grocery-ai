# Architecture

## Runtime boundary

```text
Flutter
  |
  v
Main Backend  -- authenticated user + private service token -->  AI FastAPI
  |                                                        /      |      \
  +-- users/sellers/orders/payments/etc.                  /   PostgreSQL  Redis
                                                         /     + pgvector
                                                        v
                                                   OpenAI Responses API
```

## Data ownership

**Main backend owns** users, profiles, allergies, preferences, foods, ingredients, sellers, recipes, meal plans, grocery lists, orders, payments and publication state.

**AI backend owns** generation metadata/drafts, recommendation events, embeddings, prompt/model metadata, caches and idempotency state.

## Intelligence policy

| Feature | Engine |
|---|---|
| Food recommendation | hard compatibility filter + weighted ranking |
| Recipe recommendation | hard compatibility filter + weighted ranking; pgvector-ready |
| Meal plan | candidate filtering + OpenAI structured generation + validation |
| Replacement | compatibility + nutrition similarity + OpenAI intent parsing |
| Nutrition insight | deterministic nutrition aggregation + OpenAI narration |
| Grocery | deterministic unit normalization + aggregation |
| Seller recipe | OpenAI structured generation + ingredient faithfulness validation |
| Allergy/diet compatibility | deterministic rule engine |

## Safety invariants

1. An allergy conflict is never down-ranked; it is filtered/flagged.
2. Unknown ingredient verification is never labeled safe.
3. OpenAI does not calculate nutrition totals.
4. OpenAI does not mutate main application state.
5. Seller AI recipe cannot silently add a required ingredient not supplied by the seller.
6. Generated meal plan can only select recipes from the compatible candidate catalog.
7. Main backend remains authoritative for user identity and resource ownership.
