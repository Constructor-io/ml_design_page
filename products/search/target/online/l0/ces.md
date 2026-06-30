---
id: ces
title: "CES (Cognitive Embedding Search)"
type: block
position: 6
---

## CES (Cognitive Embedding Search)

Semantic retrieval: query and items in a shared embedding space, kNN search for nearest neighbors. Captures meaning-based matches that [[ii|Inverted Index]] misses. Results feed into [[union]] and CES distance used as feature in [[stageA|Stage A]].

### Serving

```
Query → encode → query embedding
Items → encode → item embeddings (offline, stored in ANN index)

Serving:
  query embedding → kNN search → 200-400 nearest items
  ces_distance per item → feature for reranker
```

### Training

- **Cross-customer pretrain** on behavioral data (clicks, purchases) across all customers
- **Per-customer fine-tune** on customer-specific catalog and interactions
- **Shared item embeddings:** frozen after training, reused in reranker and personalization stream (single source of truth)

### Embedding quality requirements

#### 1. Facet predictability

It must be possible to train a simple model `CES_embedding → facet_value` with high accuracy for any business-critical facet of the customer's vertical.

| Vertical | Critical facets | Requirement |
|----------|----------------|-------------|
| All customers | price range, category, brand | Embedding encodes these reliably |
| Pet stores | animal type (cat/dog/bird) | "cat food" close to "cat toys", far from "dog food" |
| Fashion | gender, season, style | "women's summer dress" far from "men's winter coat" |
| Electronics | device type, compatibility | "iPhone 15 case" close to "iPhone 15 charger" |

This ensures embeddings encode structured product semantics, not just click co-occurrence patterns. Validated by probing classifiers per facet.

#### 2. Variant-level embeddings

Currently CES operates at item level only. Target: embeddings at **variant level** — each variant (color, size, configuration) gets its own embedding. Enables personalization model to learn facet preferences from purchase history (user bought red variant → model can learn "prefers red").
