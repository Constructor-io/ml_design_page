---
id: ii
title: "Inverted Index (II)"
type: block
position: 5
---

## Inverted Index (II)

Token → posting list → intersection → weighted harmonic mean of token scores. Final score = computed_score + conversion boost + refinement boost.

### Computed Score (harmonic mean)

```
Query: "white bread" → tokenize → [white, bread]

  white → posting list: (item1:123, item2:80, item4:55, item9:490)
  bread → posting list: (item1:250, item3:90, item5:44, item9:167)

  Intersection: item1, item9
  item1 score = Hmean(123, 250) + boost
  item9 score = Hmean(490, 167) + boost

Fuzzy: "mac book shellf" → tries all spelling corrections
  → token scores reduced by SCOREFUNC(edit_distance)
```

### Token Weighting

Not all tokens are equal. Token weight in the harmonic mean depends on two axes:

| Axis | High weight | Low weight |
|------|------------|-----------|
| **Role in query** | Head noun ("shoes" in "running shoes") | Modifier ("running", "red", "cheap") |
| **Match field** | Title match | Description / tags match |

```
"red running shoes" → tokens: [red, running, shoes]

  weights:
    shoes   → head_noun × title_match    = HIGH  (main object)
    running → modifier  × title_match    = MED   (qualifier)
    red     → modifier  × description    = LOW   (attribute, may only appear in description)

  Hmean = weighted_harmonic_mean(token_scores, weights)

Effect: item "Nike Running Shoes" (title match on head noun) >>
        item "Red shoe rack" (title match, but wrong head noun)
```

Head noun is determined by QU. Match field comes from the inverted index (posting list stores field origin).

### Score Factors

| Factor | Scope | Source |
|--------|-------|--------|
| dsi_computed_score | item-level | Linear regression on daily action counts |
| behavior_keywords | token-item | (token-item actions / item actions) * 4 + 1.7 |
| group_keywords | token-group | Same algorithm, aggregated by group_id |
| cosine_similarity | token-item | FastText distance (query token vs item tokens) |
| conversion boost | query-item | CTR-based + L2R (XGBoost, top-50k queries) |
| refinement boost | query-facet | Auto affinity rules (t-test) + manual searchandising |

### Personalization boost: removed

The current system applies a per-user personalization boost directly inside II scoring. This is removed in the target architecture.

- **Problem:** mixing personalization into retrieval score conflates relevance with preference — makes debugging impossible, couples systems, and limits personalization expressiveness
- **Solution:** personalization is handled by a **dedicated retrieval stream** (Personalized kNN) that delivers its own candidates. The reranker then balances relevance vs personal preference with full visibility into both signals.
- II becomes a pure lexical relevance signal — how well do the words match?
