---
id: keysets
title: "KeySets & Synonyms"
position: 3
---

## KeySets & Synonyms

### GetKeysetsAndBoosts

Takes `CorrectionResult` list, expands with synonyms/stems → `KeySet` tree.

**KeySet structure:**
```
KeySet {
    repeated KeySetLeaf leaf_children;    // terminal terms
    repeated KeySet keyset_children;      // nested sub-sets
    string keyset_operator;               // "AND", "OR"
    bool is_truncated;
}
KeySetLeaf {
    string keyset_term;                   // token string for index lookup
    uint32 keyset_flag;                   // score adjustment flag
}
```

**Boosts:** `List[(token_list, weight, boost_type)]` — per-keyset fuzzy correction weights. Exact matches get higher weights than fuzzy corrections at inverted index query time.

KeySet size limit: 1000 leaves.

### Synonym Types

| Type | Source | Field flags |
|------|--------|-------------|
| Manual synonyms | Customer dashboard | `auto_generated=False` |
| Auto synonyms | ML-generated | `auto_generated=True` |
| Auto-reviewed synonyms | ML + online review | `autoreviewed_as=True/False/None` |
| One-way synonyms | Manual/auto | `base_ngram → related_ngram` (directional) |
| Weighted relations | Manual/auto | `base → related + weight` |
| Unit synonyms (QT-191) | Runtime | `"12mm" → "0.47 in"` (measurement conversion) |

### Data structure (SynonymData)

```python
synonym_words_to_groups: {first_word → {(phrase, group_id)}}     # two-way groups
synonym_groups: {group_id → {all phrases}}                        # bidirectional
one_way_synonyms: {first_word → {(relation_id, base, related, auto, date, state, autoreviewed)}}
weighted_relations: {first_word → {(base, related, weight, auto, date, state, autoreviewed)}}
```

### Expansion in QueryGraph

`QueryGraph` (DAG): nodes = tokens/token-groups, edges = "follows" relationship.
- Two-way synonyms: add parallel paths (symmetric)
- One-way synonyms: add `related_ngram` as alternative when query contains `base_ngram`
- Weighted relations: add term with boost weight

### Synonym feature flags

| Feature | Controls |
|---------|----------|
| `SUPPRESS_AC_QUERY_SYNONYMS` | Disable synonyms in autocomplete corrections |
| `SUPPRESS_SEARCH_QUERY_SYNONYMS` | Disable synonyms in search corrections |
| `SYNONYMS_FILTERED_BY_DATE` | `synonyms_not_newer_than` cutoff |
| `USE_AUTOREVIEWED_SYNONYMS` (QT-233) | Enable auto-reviewed filter logic |

Filtering: `auto_generated + use_autoreviewed_synonyms → autoreviewed_as is not False` (None = unseen = pass).
