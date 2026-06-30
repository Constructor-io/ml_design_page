---
id: ces_ac
title: "CES Integration"
position: 4
---

## CES Integration for Autocomplete

### Semantic neighbors

`CESGateway.get_cognitive_embeddings_neighbours()`:
- Tokenizes query: `ces_tokenize(query)`
- gRPC `GetNearestNeighbours` to CES service
- Requests `max_num_neighbours` (default 20) items
- Filters by `max_distance` (default `COGNITIVE_EMBEDDINGS_DISTANCE_THRESHOLD`)
- Adaptive threshold: `keep if (distance - best_distance) < adaptive_threshold_delta`

Score conversion:
```
score = IDEAL_AVERAGE + 3 × IDEAL_STD × (1 - min(distance, 1.0))
```
= 900,000 + 600,000 × similarity. Range: [900K, 1.5M].

### CES inverted index mixing

When CES results present: inverted index results capped to `num_inverted_index_result_when_used` (default 10). CES items injected alongside. If `bury_results=True`, CES items placed at end.

### Online filtering model

Secondary CES call: `get_online_filtering_model_similarities()`. Items below `online_filtering_threshold` removed (if CES-sourced) or buried.

### Related searches

`CESGateway.get_related_entities()` for search/browse:
- `related_searches`: semantically similar query strings
- `related_browse_pages`: related faceted browse pages

Only for `ACRequestType.SEARCH` and `ACRequestType.BROWSE` — not autocomplete.
