---
id: reranker
title: "Offline Reranker"
position: 8
---

## Offline Reranker

### Model

```
Backend:        LightGBM (LGBM) LambdaRank
n_estimators:   500
max_depth:      7
num_leaves:     22
subsample:      0.8
learning_rate:  0.15355
reg_alpha:      50
reg_lambda:     5
label_gain:     0,1,1023,4095  (strongly upweights purchases: gain[3]=4095 vs gain[1]=1)
```

Model types: `simple` (GBDT), `rpv` (+ revenue-per-visit calibration), `combined`.

**Quality guards (fallback to IdentityReranker):**
- Positives in train < 500
- Validation size < 100
- Unique labels < 2

### Dataset Construction

**Alternative items:**

| Parameter | Value |
|----------|-------|
| Query anchor | click_through, browse_result_click |
| Target | click_through, browse_result_click (same session, ≤15s) |
| Scope | session_id |
| Period | inherited from task params |

**Complementary items:**

| Parameter | Value |
|----------|-------|
| Query anchor | conversion with subsequent purchase (≤24h) |
| Target | conversion with subsequent purchase (≤24h, different item) |
| Target window | 48h (172800s) |
| Scope | user_id |

**Alternative RPV variant:** same as alternative, but target requires subsequent purchase (≤1d), scope = user_id.

**Organic alternative items (V2):** co-clicks from same search query or same browse category (group_id). Forward-looking `has_conversion` / `has_purchase` flags.

**Labels:**
```
0 = negative (no action)
1 = click (weak positive)
2 = conversion (ATC)
3 = purchase
```

Label assignment: `greatest(when(has_purchase, 3), when(has_conversion, 2), when(has_click, 1), 0)`.

**Candidate integration:** candidates from `CANDIDATES_SOURCES` joined to positives. Score transform: `emb_similarity_{source} = exp(-raw_score)`. Only groups with ≥2 distinct labels kept (`filter_trivial_groups`).

### Features

**Feature prefix convention:**
- V1: `q_` = seed item, `t_` = target/candidate item
- V2: `seed_` = seed item, no prefix = target item

**Pairwise co-occurrence stats:**
- `pairwise_stats_30d_lag_1d__click_cnt` — co-click count (30d window, 1d lag)
- `pairwise_stats_30d_lag_1d__conversion_cnt`
- `pairwise_stats_30d_lag_1d__purchase_cnt`
- Same for 120d window
- Marginals: `..._item_1_cnt`, `..._item_2_cnt`

**Derived conditional probabilities (via `two_features_divided` processor):**
- `pairwise_stats_30d_lag_1d__click_prob` = co_click_cnt / seed_click_cnt = P(target clicked | seed clicked)
- `pairwise_stats_30d_lag_1d__click_inv_prob` = co_click_cnt / target_click_cnt
- Same for conversion, purchase

**Item-level behavioral (target only, prefixed `t_`):**
- `dsi_action_counts_7d_lag_1d_maxnrm__click_through_cnt`
- `dsi_action_counts_7d_lag_1d_maxnrm__conversion_cnt`
- `dsi_action_counts_7d_lag_1d_maxnrm__purchase_cnt`
- Same for 30d

**Candidate source scores:**
- `emb_similarity_lightfm`
- `emb_similarity_ces_best`
- `emb_similarity_w2v_skip_gram`
- `emb_similarity_complementary_lfm`

**Catalog attributes (per-customer):**
- `dsi_base__#@_rating`, `dsi_base__#@_brand`, `dsi_base__#@_primary_category_id`
- `dsi_variations_base__#@_avg_price`, `dsi_variations_base__#@_on_sale_ration`
- Customer-specific: `dsi_base__#@_pet_type`, `dsi_base__#@_ae_body_part_lower`, `dsi_variations_base__#@_room_list`

**Pairwise processors:**

| Processor | Output | Formula |
|-----------|--------|---------|
| `two_features_divided` | conditional probs | `l_col / r_col` |
| `two_features_absolute_difference` | `_abs_diff` | `\|q_feat - t_feat\|` |
| `two_features_relative_difference` | `_rel_diff` | `(q - t) / q` |
| `two_features_concat_encoded` | `_pair_encoded` | concat q+t → JamesStein |
| `two_features_list_jaccard_distance` | `_iou` | Jaccard for list-valued features |
| `apply_features_match_processor` | binary | `q_feat == t_feat → {0,1}` |

### Offline Inference

```
Task:           ApplyOfflineREXRerankerModel
Batch size:     2,000,000 rows per batch
Execution:      Spark toLocalIterator (prefetchPartitions=True), driver-side scoring
Sorting:        (q_customer_id, pos) within each batch before inference
Post-scoring:   row_number() over (item_1_id ORDER BY score DESC) → rank
Output:         Delta table: reranker_rex_model_inference
                Columns: item_1_id, item_2_id, score, rank
                Partitions: day, ac_key, tag, version
Optional:       MetadataFilter (remove cross-category / out-of-stock candidates)
```

### Training Metrics

- Primary: `RerankerNDCG(k=25, reference_column='label')`
- Additional: NDCG, MAP, MRR, AUC at top_k=[5]
- Revenue: `RerankerRevenueDiscountedByRank` (when revenue features present)
- MLflow: `Constructor/Rex-offline-reranker`
