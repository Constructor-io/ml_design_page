---
id: related
title: "Related Searches & Reformulations"
position: 4
---

## Related Searches & Reformulations

### BuildRelatedSearches

Three generation methods:

**a. Similar Sessions (`get_rs_similar_sessions`):**
- Queries co-occurring in same session
- Self-join by `(query, session_id)`
- Filters: same-token substrings removed, spaceless equivalents removed, inverted word-order removed
- Levenshtein typo detection: sorted-stopword-free tokens distance > 1
- Min co-occurrence: 5
- Excludes top-5 most popular candidates (avoid generic)

**b. Expanding/Refining (`get_rs_expanding_refining`):**
- Expanding: candidate has more tokens, all query tokens ⊆ candidate tokens
- Refining: query has more tokens, all candidate tokens ⊆ query tokens
- Optional category gate (dominant product category must match)

**c. Reformulations (V3 only):**
- From `FindQueryReformulations` (session-level query sequences, failed first query)
- Min reformulation count: 3

**Versions:** V1, V2, V2_GROUPS, V3, FOR_BROWSE_V1.

**Output:** Delta table `related_searches` — columns: `query, related_query, source, priority, clicks, add2carts, shows, co_occurrence`. Partitioned by `[day, ac_key, tag]`.

### Query Reformulations

```
Source:    behavioral logs, consecutive search pairs in same session (≤60s gap)
Condition: first query had no conversions (but can have clicks)
Aggregation: (query, reformulated_query) → counts: sessions, clicked, converted
Enrichment: top 10 converted items per reformulated query
Output:    Delta table query_reformulations, partitioned by [day, period, ac_key]
```

Used by: related searches (V3), zero-result recommendations, search analytics.

### Query Normalization

**At request time (FAS):**
```python
prefix = prefix.replace('|', '/').lower()   # URL decode + lowercase
```

**For query-items lookup:**
```python
normalized_query = ' '.join(tokenize(query.strip(), client_side_query=True))
```
Uses `cnstrc_normalizer.tokenizer.tokenize()` — language-aware tokenizer (20+ languages, Thai special handling).

**At index build time:**
- NFKC unicode normalization
- HTML tag stripping (regex)
- Non-word character removal (Unicode-aware)
- Underscore → space
- Stemming: `extended_tokenize(term, stem=True, drop_duplicates=True, sort=True, lang=lang)`
- Double-stemming: two-pass for non-idempotent stemmers ("mens" → "men" → "man")
- NLTK `WordNetLemmatizer` for English plural handling
