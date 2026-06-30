---
id: personalization
title: "Personalization"
position: 3
---

## Personalization

### PersonalizeREXTransformer (primary)

1. Fetch user history (parallel, across all user IDs)
2. Compute per-item boost weights via `PersonalizationItemsBooster`:
   ```
   weight(item, action) = 2 * boost_std(action) * (1 - 0.5^count)
   ```
   `boost_std`: PURCHASE/CONVERSION/CUSTOM=2, others=1. Per-item: max across actions.
3. Expand weights via `SimilarItemsBatchDict.batch_get()`:
   - For each history item I with weight w, for each similar item J with similarity s:
   - J.accumulated_weight += s * w (additive across multiple history items)
4. Score update:
   ```
   personalization_score = accumulated_weight / MAX_USER_HISTORY_BOOST  // normalize ~[0,1]
   new_score = original_score + personalization_score * personalization_boost
   ```
   Default `personalization_boost = 4.0`.
5. Re-sort by descending score.

### LinearPersonalREXTransformer (linear model, rank blending)

Features:
- `one_hot_interaction_{action}_7d` — binary: item was {clicked/converted/purchased/...} in 7d
- `user_hist_avg_{action}_neighbor_sim` — sum of `similarity(history_item, candidate) * count`
- `item_log_score` — `log(1 + max(0, item.score))`

Model: `predictions = feature_matrix @ weight_vector` (no bias, weights from feature flag).

Blending:
```
rex_rank = rankdata(original_scores)
predicts_rank = rankdata(predictions)
blended_rank = blending_coefficient * predicts_rank + (1 - blending_coefficient) * rex_rank
```

### User History

| ActionType | boost_std | last_actions | expire_days |
|---|---|---|---|
| `PURCHASE` | 2 | 20 | 120 |
| `CONVERSION` | 2 | 20 | 31 |
| `CUSTOM_INTERACTION` | 2 | 20 | 31 |
| `CLICK_THROUGH` | 1 | 20 | 31 |
| `BROWSE_RESULT_CLICK` | 1 | 20 | 31 |
| `RESULT_CLICK` | 1 | 20 | 31 |
| `RECOMMENDATION_RESULT_CLICK` | 1 | 20 | 31 |
| `SEARCH_RESULT_CLICK` | 1 | 20 | 31 |
| `ITEM_DETAIL_LOAD` | 1 | 20 | 31 |
| `SELECT` | 1 | 20 | 31 |
| `ASSISTANT_SEARCH_RESULT_CLICK` | 1 | 20 | 31 |
| `QUIZ_RESULT_CLICK` | 1 | 20 | 31 |

**History fetching:** parallel ThreadPoolExecutor across all user IDs (`customer_user_id`, `constructor_user_id`, `additional_constructor_user_ids`). Merge: concatenate per-action, dedup preserving order, sort ascending by timestamp.

**Additional user ID mapping:** feature flag `RECOMMENDATIONS_UI_TO_I_HISTORY_MAPPING` — maps `customer_user_id` → up to 5 internal `constructor_user_ids` via user-segments service (channel: `email`).
