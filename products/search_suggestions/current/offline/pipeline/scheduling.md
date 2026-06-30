---
id: ss_scheduling
title: "Scheduling & Feature Flags"
position: 5
---

## Scheduling & Feature Flags

### Airflow Scheduling

| Pipeline | Schedule | Description |
|----------|----------|-------------|
| Search Suggestions update | `30 12 * * *` (12:30 UTC) | `DailyUpdateAllSearchSuggestionsInDB` |
| Query Reformulations | `00 3 * * *` (3:00 UTC) | `FrustratedSearchesReportForAll` |
| CES Pretrain FastText | `16 0 * * *` (0:16 UTC) | `PretrainFastTextForSemanticSearch` |
| Related Searches (CES) | — | Via CES inference DAGs (daily) |
| Query Items (QRL) | `0 3 * * *` (3:00 UTC) | `GetQueryItemPairsFromQRL` |
| Search Queries Statistics | — | Per-ac_key daily |
| Index rebuild | On trigger | `reset_last_update()` triggers async rebuild |

### Core correction features

| Feature | Description |
|---------|-------------|
| `SPELL_CORRECTION` | Master toggle for query correction |
| `SEARCH_ONLY_BEST_SUGGESTION` | Use only top-1 correction in search |
| `ALWAYS_USE_ALL_SPELLING_CORRECTIONS` | Force all corrections (both passes) |
| `DISABLE_SECOND_PASS` (QT-286) | Skip 2nd-pass corrections |
| `USE_KEYVI_CORRECTIONS` (QT-124) | Keyvi FSA alternative to DAWG+Trigram |
| `USE_CORRECTION_FILTERING` (QT-137) | ML CatBoost filter on correction candidates |
| `ENABLE_DECOMPOUNDING` (QT-88) | German compound word splitting |
| `ENABLE_UNIT_HANDLING` (QT-191) | Unit-aware corrections (mm→in) |
| `SKIP_CJK_CORRECTIONS` (QT-255) | Skip corrections for CJK tokens |
| `PREFIX_COMPLETED_EXACT_IDENTIFIERS` (QT-42) | Prefix-complete exact IDs |
| `PREFIX_COMPLETED_FUZZY_SEARCHABLES` (QT-29) | Prefix-complete fuzzy tokens |

### Ranking/scoring features

| Feature | Description |
|---------|-------------|
| `QUERY_ITEMS` | Query→item CTR boosts from DataPipeline |
| `FILTER_ITEMS` | Filter→item CTR boosts (browse) |
| `PERSONALIZATION` | Master personalization toggle |
| `PERSONALIZATION_BOOST_SIMILARS` | Expand personalization via neighbor graph |
| `SAFE_PERSONALIZATION` | Cap personalization impact |
| `SEARCHANDIZING` | Manual boost/blacklist/slot rules |
| `USE_RERANKER_SERVICE_FOR_AUTOCOMPLETE` | ML reranker for autocomplete |
| `USE_RERANKER_SERVICE_FOR_SEARCH` | ML reranker for search |
| `USE_COGNITIVE_EMBEDDINGS` | CES semantic embedding neighbors |
| `USE_CES_BLENDING` | CES+base geometric mean (no reranker) |
| `USE_LLM_LABEL_SORT` | Sort by LLM relevance label |
| `DIVERSIFY_RESULTS_SEARCH` | Result diversification |

### Known Limitations

- **Offline suggestion generation** — new suggestions appear only after daily pipeline run + index rebuild; no real-time trending
- **Deduplication heuristics** — plural/spacing/stem/order dedup can miss semantically duplicate queries or incorrectly merge distinct ones
- **Validation via live API** — suggestion validation requires live search API call per candidate; expensive, limits throughput
- **TrigramDB coverage** — only covers 95th percentile of query volume; rare/new queries fall back to root-level DAWG traversal (slower)
- **Fixed edit distance thresholds** — length-based, not adapted to language or domain
- **No learned correction ranking** — harmonic mean × LM score is heuristic
- **Query-items boost is static** — updated daily from QRL; no real-time CTR signal
- **Personalization limited to history boost** — no learned query-level personalization model
- **No cross-section ranking** — sections filled independently and merged by round-robin, not jointly ranked
- **Redis cache key ignores personalization** — cache bypasses when personalization params change
- **Delta index item limit** — large catalog changes force full rebuild
- **Synonym quality** — auto synonyms require review; unreviewed pass by default
- **Single language model** — one KenLM per index; no multi-language correction scoring
- **No query intent classification** — all prefixes treated uniformly regardless of intent
