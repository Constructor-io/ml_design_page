---
id: strategies
title: "Strategies & Recommenders"
position: 1
---

## Strategies & Recommenders

| Strategy | Recommender | Data Source | Mapping Type |
|----------|-------------|-------------|--------------|
| `alternative_items` | SimilarItemsRecommender | Item-to-items graph | `neighbor_items` (overridable) |
| `complementary_items` | SimilarItemsRecommender | Item-to-items graph | `complementary_items` (overridable) |
| `bundles` | SimilarItemsRecommender | Item-to-items graph | `frequent_itemsets_items` (overridable) |
| `visually_similar_items` | SimilarItemsRecommender | Item-to-items graph | `neighbor_items_images` |
| `custom_item_item` | SimilarItemsRecommender | Item-to-items graph | customer-defined mapping |
| `custom_user_item` | UserToItemsRecommender | User-to-items KV | customer-defined mapping |
| `bestsellers` | TopItemsStatsRecommender | Top items stats KV | metric: `conversion_cnt_31d` |
| `filtered_items` | FilteredItemsRecommender | Inverted Index (browse) | — |
| `recently_viewed_items` | RecentlyViewedRecommender | User history service | — |
| `abandoned_in_cart` | AbandonedInCartRecommender | User history service | — |
| `buy_it_again` | BuyItAgainRecommender | User history service | — |
| `user_featured_items` | UserFeaturedItemsRecommender | History + neighbor graph | `neighbor_items` |
| `query_recommendations` | QueryItemsRecommender | Query-to-items KV | `recommendations` |

### Strategy execution flow

```
Pod endpoint: /recommendations/v1/pods/<pod_id>
    Pod → strategy resolution (MySQL + feature flags + A/B)

Strategy execution:
    ├── SimilarItemsRecommender (alternative, complementary, bundles, visual, custom_item_item)
    ├── TopItemsStatsRecommender (bestsellers)
    ├── FilteredItemsRecommender (filtered_items, browse-like)
    ├── RecentlyViewedRecommender (user history)
    ├── AbandonedInCartRecommender (cart - purchases)
    ├── BuyItAgainRecommender (purchase history)
    ├── UserFeaturedItemsRecommender (history → expand via neighbor graph)
    ├── QueryItemsRecommender (zero-result search fallback)
    └── UserToItemsRecommender (custom_user_item, BYOM)
```

### Serving Data Path

```
Data Pipeline → S3 (JSONL) → DynamoDB upload
                                    ↓
                          Data Pipeline Service (gRPC/HTTP)
                                    ↓
                          KV Service connector (fuzzy_autocomplete_server)
                                    ↓
                          SimilarItemsBatchDict.batch_get(customer_ids)
                                    ↓
                          {customer_id: {mapping_type: {candidate_id: score}}}
```

`multi_get(customer_ids)` returns full merged graph. Specific `mapping_type` extracted at strategy level.

Variation key fallback: tries `{item_id}<SEP>{variation_id}` first, falls back to bare `item_id`.
