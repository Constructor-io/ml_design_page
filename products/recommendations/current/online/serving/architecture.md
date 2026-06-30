---
id: architecture
title: "Pod Resolution & Configuration"
position: 2
---

## Pod Resolution & Configuration

### Pod Resolution

Resolution order (priority descending):
1. Feature flag `RECOMMENDATIONS_OVERRIDE_PODS_STRATEGIES` (variant keyed by `pod_id`)
2. `pod_info.strategy_name` from MySQL `recommendation_pods` table
3. Fallback: `bestsellers`

Pod A/B testing: `RECOMMENDATIONS_OVERRIDE_POD_ID` + per-page-type flags (`HOME`, `CART`, `PDP`, `PLP`).

### REXConfig (Per-Pod Configuration)

Merge order (ascending priority):
1. `default` (hardcoded per strategy)
2. `pod_config` (from MySQL `recommendation_pods.metadata_json['pod_config']`)
3. Feature flag `RECOMMENDATIONS_POD_CONFIG` (variant by pod_id)
4. `CUSTOMER_DASHBOARD_RECOMMENDATION_PODS_EXPERIMENT_STRATEGY`

**Key fields:**

| Field | Default | Description |
|-------|---------|------------|
| `backfill_with_filtered_items` | True | FilteredItems instead of bestsellers for backfill |
| `strategies_override` | None | Multi-strategy blending (ordered list) |
| `max_num_results` | None | Cap on num_results |
| `bestsellers_metric_name` | None | Override KV metric |
| `diversify_with_facet` | None | Facet-based round-robin diversification |
| `override_similar_items_mapping` | None | Override mapping_type |
| `personalisation_config` | None | Per-pod personalization (boost, config) |
| `use_backfill` | None | Toggle backfilling |
| `exclude_items_config` | None | Exclude clicked/purchased/converted items |
| `use_personalisation` | True | Toggle personalization entirely |
| `refined_backfilling_config` | None | Facet-refined bestsellers backfill |
| `use_user_segmented_bestsellers` | None | Segment-specific bestsellers |

### Multi-Strategy Blending (StrategiesOverride)

When `strategies_override` is configured:
1. Iterate strategies in config order
2. Each strategy contributes at most `strategy_override.num_results` items
3. Cross-strategy deduplication by `item_id` (if enabled)
4. If `use_backfill=True` — auto-appends bestsellers at the end
5. Combined result → shared formatting
