---
id: postprocessing
title: "Post-processing"
position: 4
---

## Post-processing

### Backfill

**FillGapBackfillCalculator:** `needed = max(0, target - current)`.

**ForceExtraRatioBackfillCalculator(ratio=1.0):** always fetches at least `target * ratio` items from bestsellers, regardless of gap. Default in production: `ratio=1.0` (always at least num_results bestseller items appended).

Backfill items are appended after primary (never interleaved), tagged `is_backfilled=True`.

**Refined backfilling:** facet-refined bestsellers — fetches top items for seed item's specific facet value instead of global bestsellers.

### Diversification

`DiversifyWithFacetTransformer` — round-robin interleaving by facet value:
1. Group items by `tuple(sorted(facet_values))` for specified facet
2. Split into consecutive strategy chunks (preserves strategy ordering)
3. Per chunk: round-robin pop one item from each facet-value group until exhausted
4. Optional `num_results_to_diversify` cap (rest appended in original order)

### Merchandising

`MerchandisingFilteringAndSortingREXTransformer`:

**V1 mode** (no index fetch): converts ranks to scores, applies boost/bury/slot/blacklist/whitelist via `terms_processor.get_results_for_iterator()`.

Score formula:
```
score = IDEAL_AVERAGE + 4 * IDEAL_STD + MAX_BOOST_COEFFICIENT * BOOST_RULE_MULTIPLIER * IDEAL_STD / (REX_ALPHA * rank + 1)
```

**V2 mode** (feature flag `RECOMMENDATIONS_COMBINED_FILTERED_MERCHANDISING`): combined fetch + merchandising in one Index Service call. For strategies with filters/collections/whitelists.

### Deduplication

**By item_id:** exact match. Excludes: `args.exclude_item_ids` (from user history exclusion config) + `args.item_ids` (seed items).

**By item name** (response-time): exact string equality on `item['value']`. Per `(name, slice_facet)` — different color slices of same product name can coexist if slice differs.

### Recall Boosting

Internal fetch size: `2 * num_results` (hardcoded `RECALL_BOOST_COEFFICIENT = 2`). Bumped to `MAX_NUM_RESULTS_RECOMMENDATIONS` (200) when whitelist filters present. Extra added for excluded + blacklisted items.

### Item Exclusion from User History

Per-pod via `ExcludeItemsConfig`:
- `exclude_clicked` / `exclude_clicked_period` (days)
- `exclude_purchased` / `exclude_purchased_period`
- `exclude_converted` / `exclude_converted_period`

Fetches user history via parallel `ThreadPoolExecutor`, all excluded IDs passed to `DeduplicateREXTransformer`.

### Sponsored Listings

Feature flag: `SPONSORED_LISTINGS_RECOMMENDATIONS`. External service call with `pod_id`, `strategy_id`, `num_results_per_page`, filters, etc. Sponsored items returned with `is_retail_media=True`, slotted by `terms_processor`.

### Circuit Breakers

- `user_segments_service` — `user_segments_breaker`
- `sponsored_listings_service` — `sponsored_listings_breaker`
- `facet_storage` (DynamoDB) — `facet_db_breaker`
- User history: `enable_circuit_breakers` flag from `ac_config`

### Caching

- Response-level: `Cache-Control: no-cache` (explicit, all rec responses)
- Request-scoped: facet storage created at most once per request per backend
- Index Service timeout: `ac_config.rex_index_service_recommendations_timeout` (separate from search)
