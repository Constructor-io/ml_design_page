---
id: stacking
title: "Stacking (StackMixer)"
position: 7
---

## Stacking (StackMixer)

Round-robin merge from multiple candidate sources with dedup.

```
Max candidates per source: 9 (default for REXBackfilled)
Total candidates:          50
Deduplication:             by (item_1_id, item_2_id) — first source wins
Optional:                  quantile_thresholds per source (score-based filtering)
```

### Stacking configurations

| Stack class | Default sources | Strategy |
|---|---|---|
| `REXBackfilled` | `['ces']` | alternative |
| `AlternativeBackfilled` | `['ces']` | alternative |
| `ComplementaryBackfilled` | `['comp', 'w2v', 'ces', 'lightfm']` | complementary |
| `BundlesBackfilled` | `['freq', 'comp', 'w2v', 'ces', 'lightfm']` | bundles |
| `AlternativeImages` | `['vit']` | alternative (visual) |
| `ComplementaryLLM` | `['complementary_llm']` | complementary (direct, no mix) |

### Category bundling (optional post-stack)

- `CandidatesCategoryBundler` — reranks candidates to maximize category diversity
- `CandidatesCategoryBundleFilter` — hard filter one item per category
