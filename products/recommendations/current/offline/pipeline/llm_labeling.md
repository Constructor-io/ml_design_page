---
id: llm_labeling
title: "LLM Labeling Pipeline"
position: 9
---

## LLM Labeling Pipeline

```
Task:           LLMOnlineLabels
Model:          OpenAI GPT (async)
Labels:         3-class (alternative / complementary / irrelevant)
                or binary (complementary / non-complementary)
Max batch:      50K pairs per run
Max total:      10M pairs
Sources:        reranker_positives_dataset, llm_just_added_candidates_dataset, others
Output:         Delta table rex_llm_labels, partitioned by (day, ac_key, model_tag)
Usage:          LLMFiltered variants (filter or boost) applied to any base index
```

Each `*_filtered` / `*_boosted` variant: base index + `LLMFiltered` post-processing.
