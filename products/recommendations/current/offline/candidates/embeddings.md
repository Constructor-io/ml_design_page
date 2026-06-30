---
id: embeddings
title: "Embedding Candidates (Granne ANN)"
position: 1
---

## EmbeddingSimilarityCandidates (Granne ANN)

General framework for all embedding-based sources. Per-item ANN search (Granne, HNSW), parallel across all catalog items (joblib, all CPUs).

### Embedding types

| Embedding type | Model | Dim | Training signal | Dual vectors |
|---|---|---|---|---|
| `lightfm` | LightFM (personalization) | 16 | clicks (WARP) | No |
| `ces` | FastText (catalog text) | 64 | unsupervised skip-gram | No |
| `ces_dssm` | DSSM (behavioral fine-tune) | 64 | triplet loss on clicks | No |
| `ces_best` | Best available CES model | varies | varies | No |
| `w2v` | Word2Vec CBOW | 100 | purchase baskets | No |
| `w2v_skip_gram` | Word2Vec Skip-gram | 32–128 | purchase baskets | Yes (`wv` + `syn1neg`) |
| `vit` | EfficientNet-B0 / ViT-DINO / SigLIP | varies | pretrained (no fine-tune) | No |
| `complementary_llm` | Dual-encoder NN (256d hidden) | varies | GPT-labeled complementary pairs | Yes |
| `complementary_lfm` | LightFM item-to-item | 64 | co-purchases (WARP) | Yes (`user_repr` + `item_repr`) |
| `complementary_lfm_pmi` | LightFM + PMI weighting | 64 | co-purchases + hierarchical PMI | Yes |
| `static_complementary` | Pre-computed (hardcoded S3) | — | LLM-generated | Yes |

### Granne index params

```
Index type: ANGULAR (float32, for recs) or ANGULAR_INT (quantized, for CES service)
max_search: 500 (build + query time beam width)
Process isolation: subprocess (avoid Python GIL deadlocks)
```

### Cluster auto-scaling by catalog size

200K items → 2x driver, 1M → 4x, 10M → 8x.
