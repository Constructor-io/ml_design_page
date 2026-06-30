---
id: w2v
title: "Word2Vec"
position: 3
---

## Word2Vec

### CBOW variant (`w2v`)

```
Dim:        100
Window:     9 (full basket context)
Min count:  1
Epochs:     5
Workers:    16
Signal:     purchase baskets (fallback: ATC)
Basket:     max 10 items per basket
```

### Skip-gram variant (`w2v_skip_gram`)

```
sg:         1 (skip-gram)
Epochs:     100
Negative:   20
Grid search: dim in [32, 64, 128], negative in [5, 10], epochs in [10, 20, 30]
```

Dual vectors: `wv` (output layer) = query vectors, `syn1neg` (negative sampling hidden) = index vectors. Asymmetric query/index space.
