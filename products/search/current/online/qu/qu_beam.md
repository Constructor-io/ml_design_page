---
id: qu_beam
title: "Beam Search"
type: block
position: 4
---

## Beam Search (candidate generation)

Builds multi-token correction candidates via beam search (beam width = 10). At each token position, expands all current phrases × all corrections for that token, keeps top 10.

Result for "macbok pro 13in":

| Candidate | Score | How |
|---|---|---|
| "macbook pro 13in" | 0.95 | "macbok" corrected, rest passthrough |
| "macbok pro 13in" | 0.12 | Original kept as fallback |

### Scoring

Each candidate scored: **log(max(1, LM_score × DAWG_score))**

| Component | What it is | Trained on |
|---|---|---|
| LM_score | KenLM 3-gram probability | Customer search logs |
| DAWG_score | Harmonic mean of per-token scores | Edit distance + phonetics + keyboard proximity |

### Post-beam steps

- **Joins:** try merging adjacent tokens ("lip" + "stick" → "lipstick")
- **Decompounding:** try splitting compounds (German/Finnish, e.g. "handschuhe" → "hand schuhe")
