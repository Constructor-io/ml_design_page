---
id: query_flow
title: "Query Execution Flow"
position: 1
---

## Query Execution Flow

### Request flow

```
/v1/autocomplete/<prefix>
    │
    ├── prefix = prefix.replace('|', '/').lower()
    ├── Redis cache check (if SABR_CACHING enabled)
    ├── UserSegmentsFetcher (async) → tags
    ├── UserBoostedTermsFetcher (async, per section) → boosted_terms
    ├── RefinedQueryRules → whitelist/blacklist/boost/slot
    │
    └── Per section (parallel ThreadPool):
          TermsProcessor.get_results()
            │
            ├── QS.get_spelling_corrections(prefix) → corrections
            ├── QS.get_keysets_and_boosts(corrections) → (keysets, boosts)
            ├── DataPipelineService.get_query_boosted_terms(best_correction) → query_items
            ├── CESGateway (optional) → semantic neighbors
            ├── InvertedIndex.get_results_for_iterator(keysets, boosts, boosted_terms)
            │     → first-pass results
            ├── If first-pass insufficient → second-pass with second_run_corrections
            ├── RerankerGateway (optional) → ML re-ranking
            └── SponsoredListingsGateway → slotted ads
```

### Score contributions at query time

1. **Base score:** from inverted index (precomputed at index build)
2. **Fuzzy boost weights:** from QS keyset boosts (fuzzy corrections → lower weight than exact)
3. **Query-items boost:** `query→{item: weight}` from DataPipelineService (click/purchase CTR attribution)
4. **Personalization boost:** `PersonalizationItemsBooster` weights from user history
5. **Similar items boost:** co-occurrence items via `PERSONALIZATION_BOOST_SIMILARS`
6. **Searchandizing rules:** manual boost/blacklist/slot: `IDEAL_STD × BOOST_RULE_MULTIPLIER(4) × boost_value`
7. **CES boost:** embedding distance → score: `IDEAL_AVERAGE + 3 × IDEAL_STD × (1 - distance)`
8. **Reranker (optional):** full ML re-scoring

### Multi-section result merging

Over-fetch: `ceil(num_results / 2)` per section when multiple sections exist.

Limiting/round-robin:
1. If total results ≤ max_results → no trimming
2. Base allocation: `floor(max_results / num_sections)` per section
3. Remaining slots distributed one-at-a-time cycling through sections (alphabetical order)
4. Section with no remaining items skipped on cycle turn

### Batch Autocomplete

```
GET /v1/batch_autocomplete?q=foo&q=bar&num_results=5
```

Iterates each `q` sequentially, calls `autocomplete_prefix_impl()` per prefix. Shares all other params. Per-prefix timeout: returns `status_code=504` for timed-out prefixes, others continue.

Permission: `internal.batch_autocomplete` (internal-only). Used for cache pre-warming and batch pre-fetch.
