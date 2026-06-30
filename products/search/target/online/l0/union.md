---
id: union
title: "Union & Dedup"
type: block
position: 10
---

## Union & Dedup

Each stream delivers its top-K candidates. Scores across streams are incomparable — no summation, no normalization. Simple union by item_id with deduplication.

### Why not score summation?

- Scores have **different distributions** (inverted index: normal, personalization: exponential, CTR: log-scale)
- Normalization doesn't help — relative distances between scores are incomparable across sources
- One source with a wide distribution dominates the others
- Impossible to set correct "weights" when scales are incompatible

### Principle: each source delivers its quota of candidates

```
Inverted Index  → top X candidates  ─┐
Semantic (CES)  → top Y candidates  ─┼─→ Union (deduplicate) → Candidate pool → Reranker
Personalization → top Z candidates  ─┤
Complementary   → top W candidates  ─┤
Exploration     → top V candidates  ─┘
```

- Each stream is responsible for **recall of its aspect** — delivers its best by its own criteria
- Scores within a stream are never compared to scores from other streams
- Final order is determined by the **reranker**, which sees all features and scores uniformly
- Quotas (X, Y, Z, W, V) are determined by Query Understanding based on intent and query characteristics

### Quota ranges per query

```
QU determines quotas per-query:
  II:     200-600 (depends on query specificity)
  CES:    200-400
  Perso:  100-300 (depends on user history depth)
  Compl:   50-150
  Explor:  30-100

Union:
  all streams → merge by item_id → dedup
  → ~800-1200 unique candidates
  → LLM pre-filter (remove confident irrelevant)
  → ~600-1000 → Reranker
```

### Merge rules

- Quotas per-stream determined by QU per-query (not fixed)
- On duplicate: item enters pool once, all source scores preserved as features for reranker
- No quality threshold — stream delivers exactly K best, even if scores are low
- Principle: **streams maximize recall** (don't miss), **reranker maximizes precision** (correct order)

### Architectural principle

Separation of concerns:
- **Streams** → recall — don't miss good candidates of each type
- **Reranker** → precision — correct final order considering all signals

If an item doesn't make it into the candidate pool, the reranker cannot save it.

### Declarative configuration

DSI describes only **what** is enabled and limits. The system decides how to implement per-query.

```yaml
retrieval:
  streams:
    lexical:           {enabled: true}
    semantic:          {enabled: true, model: auto}
    personalization:   {enabled: true, min_history: 5, fallback: popular}
    complementary:     {enabled: true}
    exploration:       {min_fraction: 0.03, max_fraction: 0.15}

  constraints:
    category_match:    soft          # soft boost | strict filter | off
    main_noun_match:   required      # product must BE what user asked for

  llm_filter:          {enabled: true, confidence_threshold: 0.9}

ranker:
  stage_a:             {model: auto}
  stage_b:             {enabled: true}
  objectives:
    relevance: 0.60
    revenue: 0.25
    diversity: 0.10
    freshness: 0.05
```
