---
id: graph_methods
title: "Graph-Based Methods (ALS, FP-Growth, Co-clicks)"
position: 6
---

## Graph-Based Candidate Methods

### ComplementaryItemsGraphTable (ALS)

Co-occurrence → ALS matrix factorization.

```
Source:          ComputeCoOccurredItems (co-conversion or co-purchase pairs)
Filter:          binomial CI lower bound on conditional probability >= min_conditional_prob
ALS:             implicit.als.AlternatingLeastSquares
  factors:       40
  iterations:    100
Period:          30d (default), 50d, 120d variants
Max candidates:  20
Min pair counts: 2
Score formula:   relevance_weight * co_occurrence_relevance + (1 - relevance_weight) * ALS_score
  relevance_weight: 0.9 (default — heavily favors co-occurrence count)
Final:           log-normalized × weight_multiplier
```

### GenerateFrequentItemsetsBundles (FP-Growth)

```
Source:          purchase events (fallback: ATC)
Baskets:         sessions of unique items
Min basket size: 2
Max basket size: 8
Support:         SupportThresholdStrategy.MEDIAN
Period:          60d
Algorithm:       FP-Growth (FreqItemsetsBundles)
Output:          item→item pairs from frequent co-purchase patterns
```

### ComputeCoClickedItems

```
Source:          CLICK_THROUGH + BROWSE_RESULT_CLICK within same session
Score:           normalized co-click count / total clicks for item_1
Experience:      ALTERNATIVE
```
