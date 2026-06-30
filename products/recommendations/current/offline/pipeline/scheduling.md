---
id: scheduling
title: "Scheduling & Configuration"
position: 11
---

## Scheduling & Configuration

### Airflow DAGs

**Daily automated DAGs:**
- `DailyMergeSimilarItemsGraphsForSubscribedCustomers`
- `DailyMergeSimilarItemsGraphsForNonSubscribedCustomers`
- `DailyMergeSimilarItemsGraphsForExtraImportantCustomers`

**On-demand:** `RunAllLearningsInteractive` (ECS Luigi, retries=5, timeout=1 day).

**Training schedules:**
- LightFM (personalization): daily (within `RunAllLearnings`)
- Word2Vec: daily
- Complementary ALS: daily
- FP-Growth bundles: daily
- LightFM (complementary): daily
- Offline reranker: daily (separate DAGs per customer group)

**Embedding models** (via CES pipeline):
- FastText pretrain: daily 00:16 UTC
- DSSM: Tuesdays
- Transformer: Wednesdays

### Customer Configuration

**V1 (42 customers, per-customer YAML):**
```yaml
__conditional:
  - if:
      - model_name: rex_reranker_offline
    then:
      model_type: simple
      model_training_features:
        - emb_similarity_lightfm
        - pairwise_stats_30d_lag_1d__click_cnt
        - ...
      additional_features_processor:
        two_features_divided:
          - l_col: pairwise_stats_30d_lag_1d__click_cnt
            r_col: pairwise_stats_30d_lag_1d__click_item_1_cnt
            result_col: pairwise_stats_30d_lag_1d__click_prob
```

**V2 (centralized defaults + per-customer overrides):**
```yaml
# defaults/default.yaml
__conditional:
  - if:
      - model_name: rex_default_complementary_reranked
    then:
      strategy: complementary
  - if:
      - model_name: rex_default_alternative_reranked
    then:
      strategy: alternative
```

V2 relies on centralized parameter injection, dataset registry, and automatic index registration.

### REX Index Registry

Key registered indices:

| Index name | Strategy | Pipeline |
|---|---|---|
| `neighbor_items` | alternative | LightFM → Granne ANN (legacy) |
| `neighbor_items_reranked` | alternative | LightFM candidates → offline reranker |
| `co_clicked_items` | alternative | co-click counts normalized |
| `neighbor_items_backfilled` | alternative | StackMixer (ces) |
| `alternative_items_ces_best_reranked` | alternative | CES candidates → offline reranker |
| `alternative_items_pod_interactions_reranked` | alternative | Pod interaction data → reranker |
| `alternative_item_global_rpv` | alternative | RPV-optimized |
| `neighbor_items_images` | alternative (visual) | ViT image embeddings |
| `complementary_items` | complementary | ALS co-conversion (30d) |
| `complementary_items_50d` / `_120d` | complementary | ALS (longer windows) |
| `complementary_items_backfilled` | complementary | StackMixer (comp+w2v+ces+lightfm) |
| `complementary_items_llm` | complementary | LLM dual-encoder stack |
| `complementary_items_llm_backfilled` | complementary | comp+w2v+llm_labeled+ces+lightfm |
| `complementary_items_multi_source_reranked` | complementary | Multi-source → offline reranker |
| `frequent_itemsets_items` | bundles | FP-Growth stacked |
| `rex_default_alternative_reranked` | alternative (V2) | Config-driven, organic dataset |
| `rex_default_complementary_reranked` | complementary (V2) | Config-driven |
| `shop_the_look` / `complete_the_look` | complementary | Static mapping from S3 |

### Known Limitations

- **Offline-only reranking** — all item-to-item scores precomputed daily; no real-time model inference at serving time
- **No cross-customer model sharing** — each customer's graph trained independently (except CES pretrain)
- **Stacking is heuristic** — round-robin without learned combination weights
- **Personalization is additive boost** — not a learned re-ranking; PersonalizeREXTransformer is a score bump, not a model
- **LinearPersonalREXTransformer** — no training pipeline; weights are manually set via feature flags
- **Backfill always appends** — never interleaved with primary results; UX discontinuity
- **DynamoDB latency** — item-to-items graph read via Data Pipeline Service (extra hop)
- **No session context** — recommendations don't consider current session beyond seed items
- **24h cold start** — new items invisible until next daily pipeline run
- **Candidate diversity not learned** — category bundling is rule-based, not optimized
- **Label quality** — positives from co-clicks (15s window) may include noisy pairs
- **No position debiasing** — training data from recommendations pod may have presentation bias
- **Limited feedback loop** — pod interaction dataset exists but not widely used for model improvement
- **Single mapping type per strategy** — no runtime blending of multiple candidate sources at serving time
- **ForceExtraRatioBackfillCalculator(1.0)** — always fetches full num_results from bestsellers even if primary has enough results; wasteful
