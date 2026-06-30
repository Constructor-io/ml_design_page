---
id: ss_index
title: "Inverted Index Build"
position: 2
---

## Inverted Index Build

Per-item token→score entries:

```
token                    → [(internal_id, score), ...]
A:{acronym}              → [(internal_id, score), ...]
R:{token}                → duplicate token entries
EXACT:{token}            → exact searchable identifiers
ENRICHED:{tokens}        → enriched attribute tokens
ALL:                     → all items (empty query / browse)
COLLECTION:{id}          → collection membership
FACET:{key}:{value}      → facet filter index
FACET_RANGE:{key}:{val}  → range facet filter
```

### Score computation pipeline

```
raw_score (computed_score from DSI, typically query frequency for search suggestions)
    │
    ├── get_suggested_or_computed_score():
    │     -1 sentinel → default_score
    │     below DEFAULT_RAW_MIN_SCORE → REJECTION_SCORE (item pruned)
    │     all_scores_discarded → fallback_to_suggested_score
    │
    ├── normalize_score(score, scoring_features):
    │     zscore = (score - mean) / std_dev
    │     cap at MAX_ZSCORE=3 (linear stretch in [3σ, 4σ] for outliers)
    │     new_score = zscore × IDEAL_STD + IDEAL_AVERAGE
    │     floor at IDEAL_MIN_SCORE (zscore=-2)
    │
    └── get_token_scores():
          Base = normalized item score for all tokens
          + weighted_keywords_dict adjustments: weight × IDEAL_STD per token
          + category_keywords_dict adjustments: weight × IDEAL_STD per token (max across groups)
          + cosine_similarities_weights: similarity × IDEAL_STD per token
          Token scores: max-merged across all items sharing that token
```

### Key constants

| Constant | Value | Description |
|----------|-------|-------------|
| `IDEAL_STD` | 200,000 | Standard deviation unit |
| `IDEAL_AVERAGE` | 900,000 | Mean score |
| `IDEAL_MIN_SCORE` | ~500,000 | Floor (zscore=-2) |
| `MAX_ZSCORE` | 3 | Cap before linear stretch |
| `MAX_SCORE` | 1,700,000 | Hard cap = IDEAL_AVERAGE + 4×IDEAL_STD |
| `SOFT_MAX_SCORE` | 2^31 - 1 | Soft cap (no upper bound) |
| `EXACT_MATCH_SCORE_BOOST` | 600,000 | = 3×IDEAL_STD |
| `REJECTION_SCORE` | -2 | Below this → item pruned |

**Cap types:**
- `HARD` (DAWG): `[IDEAL_MIN_SCORE, MAX_SCORE]` = [500K, 1.7M]
- `SOFT` (Vocabulary/Keyvi): `[IDEAL_MIN_SCORE, 2^31-1]` (uncapped above)
- `None` (Inverted Index): no capping

**Category keywords:** per product-category behavioral weights (token→float from click/conversion data). Applied as `max(weight across item's groups) × catkws_multiplier × IDEAL_STD`. Feature flag `catkws_enable` controls.
