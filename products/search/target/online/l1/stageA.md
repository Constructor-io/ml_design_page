---
id: stageA
title: "Stage A — GBDT Pointwise"
type: block
position: 13
---

## Stage A — GBDT Pointwise

800-1200 → top-N (N ~ 100-200). Pointwise GBDT.

### Inputs

- Query-item relevance (lexical, semantic, learned)
- Behavioral stats (CTR, conversion, popularity by time windows)
- Personalization (lightweight): user_emb · item_emb distance, facet preferences, session similarity
- Item metadata (price, brand, category, freshness)
- Context (device, geo, time, session)
- LLM relevance label (offline, from feature store)

### Quota pass-through to top-N

If Stage A selects top-N purely by score, it kills diversity from retrieval. Solution:

```
top-N composition:
  - top by score (global):           ~60-70% of N
  - guaranteed from exploration:      min E items
  - guaranteed from personalization:  min P items
  - guaranteed from complementary:    min C items
```

Minimums (E, P, C) are inherited from customer retrieval config. Stage B determines their final position.

### Training

- **Labels:** ordinal 0/1/2/3 (none/click/atc/purchase) + optional LLM relevance merge
- **Loss 1:** LambdaRank optimizing purchase probability (grouped by request)
- **Loss 2:** revenue optimization — calibrated P(purchase) x item_value
- **Negatives:** confirmed only — item was in user's viewport but no action. Requires viewport impression tracking (SDK). Unobserved (below viewport) — not negative, excluded from training.
- **Cadence:** daily retrain (validate necessity — may simplify to weekly)
- **Constraints:** limited number of trees and features for fast inference over ~1000 items
