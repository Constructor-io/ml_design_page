---
id: dual_encoder
title: "Complementary Dual-Encoder"
position: 5
---

## Complementary Dual-Encoder (LLM-trained)

```
Hidden dim:     256
Input:          CES vectors (pretrained item embeddings as initialization)
Training signal: GPT-labeled complementary pairs (binary: complementary/non-complementary)
Optional weight: actual post-click purchases from the pod (revenue signal)
Epochs:         500
Batch size:     2048
LR:             0.0001 → 0.001 (cosine annealing)
```

Output: item embeddings in JSONL, consumed by `EmbeddingSimilarityCandidates(embedding_type='complementary_llm')`.
