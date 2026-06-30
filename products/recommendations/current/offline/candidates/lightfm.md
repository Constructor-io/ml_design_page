---
id: lightfm
title: "LightFM Models"
position: 2
---

## LightFM Models

### LightFM (Personalization — Alternative Items)

User-item collaborative filtering. Items and users in one embedding space.

```
Embedding dim:      16
Loss:               WARP (Weighted Approximate-Rank Pairwise)
Max negatives:      1000 per step
Epochs:             60
Train/val split:    80/20
Interaction signal: click_through (weight=1.0), optional: conversion, purchase
Min interactions:   3 per user
Max interactions:   99th percentile cap
Item features:      FastText text embeddings + group IDs (categories)
User features:      identity only
```

Embedding extraction: `model.get_item_representations(features)` → `vec` per item.

### LightFM (Complementary — Item-to-Item)

Item-to-item MF: items act as both "users" and "items". Model predicts co-purchase pairs.

```
Embedding dim:      64
Loss:               WARP
Max negatives:      1000
Epochs:             100
Train period:       120 days
Interaction data:   item co-occurrence pairs from purchases/ATC
Item features:      Catalog metadata (brand, category, etc.) via RexSearchableFeatures
                    Vocabulary pruned to coverage_threshold=0.9
Identity features:  disabled (item_identity_features=False, user_identity_features=False)
```

Sample weights: `log1p(count)` (base variant).

### PMI variant

```
PMI temperature:    2.5
PMI clip:           [0.1, 10.0]
Z-score threshold:  1.96 (95% CI significance filter)
Weight method:      'hybrid' = log1p(count) * clip(exp(pmi/T), 0.1, 10.0)
Taxonomy fields:    hierarchical category (deepest significant level via coalesce)
```

Dual embeddings: `query_vec` = `get_user_representations()`, `index_vec` = `get_item_representations()`.
