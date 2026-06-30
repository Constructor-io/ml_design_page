---
id: ss_personalization
title: "Personalization"
position: 5
---

## Personalization

### PersonalizationItemsBooster

Same as search/recommendations (shared `PersonalizationItemsBooster` from `common/`):
```
weight(item, action) = 2 × boost_std(action) × (1 - 0.5^count)
```
Per-item final weight = max across actions. Applied as additive score boost at query time.

### Similar items expansion

Feature `PERSONALIZATION_BOOST_SIMILARS`: for each history item, fetch co-occurrence/neighbor items via `item_to_items_connector`. Apply `weight_multiplier` to their boost weights.

### User segments

Feature `APPLY_USER_SEGMENT`: ML-generated segments from `UserSegmentsProvider` → packed as tags → influence searchandizing rules.

### Safe personalization

Feature `SAFE_PERSONALIZATION`: caps max boost to prevent irrelevant items surfacing due to over-personalization.
