---
id: ii_cosine
title: "cosine_similarity"
type: block
position: 6
---

## cosine_similarity

Text similarity between query token and item tokens, computed via FastText embeddings. Improves recall — helps items that are semantically related but don't share exact tokens.

### Properties

| Property | Value |
|----------|-------|
| Scope | token-item pair |
| Delivery | S3 (FastText model artifact) |
| Applied at | Index build time |
| Range | [0 - 1] * 200,000 |
| Model | FastText (per-customer, trained on customer catalog text) |
| Pipeline | `pipelines.feature_store.embeddings.fasttext` (TrainWordVectorsForIndexBuilder) |

### How it works

FastText model trained per-customer in data-pipeline. At index build time, Index Builder computes distance between each token and each item's text tokens. The cosine similarity becomes part of the item's score in the inverted index.

### Status

There is discussion about removing this factor — its original purpose was to improve recall, but now CES (Cognitive Embedding Search) handles semantic recall better and more explicitly. Keeping both is redundant computation at index build time.
