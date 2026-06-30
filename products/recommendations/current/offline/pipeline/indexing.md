---
id: indexing
title: "Index Building & Storage"
position: 10
---

## Index Building & Storage

### RecommendationsToIndexBase

Per-strategy index builder. Output format (JSONL, one line per seed item):
```json
{"customer_id": "product-abc", "similar_customer_ids": {"product-xyz": 0.50000000, "product-def": 0.33333333}}
```

**Score scaling** (default, `use_scores=False`):
```
score = 1 / (1 + rank)     // rank 0-based
rank 0 → 1.0, rank 1 → 0.5, rank 2 → 0.333, rank 9 → 0.1
```

With `use_scores=True` — raw model score, rounded to 8 decimal places.

S3 path: `s3://.../similar-items/output/{TASK_DIRECTORY}/tag={tag}/version={version}/{date}/ac_id_{ac_id}.jsonl`

### MergeSimilarItemsGraphsV2

Combines all strategy indices into one graph per customer.

**Default mappings:**
```python
{'neighbor_items', 'neighbor_items_reranked', 'complementary_items',
 'complementary_items_backfilled', 'frequent_itemsets_items'}
```

Per-customer: `mappings_to_add` / `mappings_to_remove` (remove has priority).

**Merge logic (Spark combineByKey):** no cross-source normalization. Scores from each source stored as-is, keyed under mapping type name. Output per item:
```json
{
  "customer_id": "product-abc",
  "similar_customer_ids": {
    "neighbor_items": {"product-xyz": 0.5, "product-def": 0.12},
    "complementary_items": {"product-ghi": 0.8},
    "neighbor_items_reranked": {"product-xyz": 0.9}
  }
}
```

### DynamoDB Upload

```
Table (prod):       dp-global-item-to-items-graph-prod
Partition key (pk): "data/part:ac_id={ac_id}/ver:{YYYY-MM-DD-NN}/bpk:{customer_id}"
Sort key (sk):      "bsk:" (empty business SK)
Metadata key:       pk="meta/versions", sk="part:ac_id={ac_id}"
Score type:         DecimalType(precision=28, scale=16)
Batch write:        25 items per boto3 batch (DynamoDB limit)
Parallelism:        16 threads per Spark partition, 5000 rows per partition
TTL:                none (explicit version cleanup via delete_partition_versions)
```

### Top Items Stats (Bestsellers)

Source: `StgProductStatsDailyTask` (item-action-counts).

**Metrics per period [31d, 14d, 7d, 2d, 1d]:**
- `click_through_cnt_{N}d`
- `conversion_cnt_{N}d`
- `purchase_cnt_{N}d`

**Derived metrics:**
```
purchase_cnt_{N}d_w_fallbacks =
    computed_score / 1e6 + click_cnt / 1e4 + conversion_cnt / 1e2 + purchase_cnt

conversion_cnt_{N}d_w_fallbacks =
    computed_score / 1e4 + click_cnt / 1e2 + conversion_cnt
```

**Segment-based:** `{metric}<SEP>us={segment_name}` (e.g., `purchase_cnt_7d<SEP>us=brand | dior`)

**Facet-refined:** `{metric}<SEP>{facet_name}={value}` (e.g., `complementary_items<SEP>Color=Red`)

**Top N items:** 200 per metric (max 500). Scores normalized to [0,1] by dividing by max.

### Query Recommendations (Zero-Result Fallback)

```
Step 1: FindQueryReformulations — what users reformulate zero-result queries into
Step 2: ExplodeQueryResultsSnapshot — what items appear for reformulated queries
Step 3: GenerateZeroResultRecommendations:
          score = sum(reformulations) / (1 + sum(position * reformulations))
          Top 30 items per zero-result query
Step 4: ZeroResultRecommendationsS3Index → JSONL (top_size=500)
Step 5: MergeQueryRecommendationsGraphsV2 → KV Service
```

Serving: `QueryItemsRecommender` — query normalized (lowercase, whitespace-collapsed) → KV lookup → sorted by descending score.
