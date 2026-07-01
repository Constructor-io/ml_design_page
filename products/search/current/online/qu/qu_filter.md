---
id: qu_filter
title: "CatBoost Filter"
type: block
position: 6
---

## CatBoost Filter

Optional ML gate. For each correction candidate, predicts P(correction is good):

| Aspect | Value |
|---|---|
| Model | CatBoost binary classifier |
| Threshold | 0.3 — candidates below are dropped |
| Fallback | If all filtered out, keep closest-to-original |
| Feature flag | `qt_137_use_filtering` |

### Features

- Edit distance statistics (per token and aggregated)
- LM score and DAWG score
- Token-level signals (exact match count, acronym count)
- Token length ratios

### Training

Trained on labeled correction pairs (good/bad) derived from search logs: if a correction leads to more clicks than the original, it's labeled good.

Per-customer model. Rebuilt by Index Builder.
