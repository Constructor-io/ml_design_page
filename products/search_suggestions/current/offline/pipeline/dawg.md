---
id: dawg
title: "DAWG, Trigram DB & Vocabulary"
position: 3
---

## DAWG, Trigram DB & Vocabulary

### DAWG (Directed Acyclic Word Graph)

`RecordDAWG` with format `'>II'` (two uint32 values per entry).

**Structure:** prefix_string → `(highest_dsi_score, unwrap_score)`.

- `highest_dsi_score (HTS)`: max normalized score among items whose token exactly equals this prefix (full-token match only; 0 for non-terminal prefixes)
- `unwrap_score (UWS)`: max score among items whose token **starts with** this prefix (used to decide whether to recurse)

**Stored entries (necessary prefixes only):**
- Full tokens (terminal nodes)
- Single characters (length=1)
- Branch nodes (≥2 distinct successor characters)

All other prefixes are implicit — the DAWG is compressed.

**Prefix → results traversal (`get_spelling_suggestions_prefix`):**
1. Strip spaces. If len ≤ 2: return direct prefix completions (no fuzzy)
2. `get_branches_to_check_from_trigrams(prefix[:5], trigram_db)` → seed DAWG branches
3. `cull_branches_prefix(branches, prefix, min_score, max_score)` → compute fuzzy match score per branch, remove low-scoring
4. Sort branches by fuzzy score ascending (best = last for `pop()`)
5. Loop: `unwrap_branches()` — pick best branch, expand children, collect results
6. Add direct prefix completions (exact matches)
7. Sort by score descending, return top `num_results`

**UWS usage:** `unwrap_score > 0` means "there exist descendants worth exploring". After expansion, set to 0 to prevent re-traversal.

### Trigram DB

Pre-computed acceleration cache for DAWG fuzzy matching. Keyvi JSON dictionary.

**Key:** query prefix (3-5 characters). **Value:** list of DAWG branch node prefixes to seed traversal.

**Build algorithm:**
1. Collect popular prefixes from query logs (95th percentile frequency, 7 days, top-N unique)
2. Min guarantee: 10,000 prefixes (supplement from DAWG tokens sorted by score if fewer)
3. For each prefix `p`:
   - Run `dawg.get_trigram_prefixes(p)` — DAWG fuzzy-match traversal
   - Extract first `len(p)-2` characters of each matched branch → "trigram" prefix
   - Add exact-match prefix `p[:len(p)-2]` if reachable in DAWG
   - Store `(p, [trigram_1, trigram_2, ...])` in Keyvi

**Query-time usage:**
```python
if prefix[:5] in trigram_db:
    branch_nodes = trigram_db[prefix[:5]]   # pre-computed starting points
    branches = [dawg.branch_data(node) for node in branch_nodes]
else:
    branches = dawg.get_branches_to_check('')   # fallback: start from root
```

Eliminates O(vocabulary) scan at query time — only relevant branches are checked.

### Vocabulary (Keyvi — Alternative Correction Engine)

FSA-based compressed dictionary: `token → max_score`. Built from all catalog tokens (max score across items per token) + synonyms at IDEAL_AVERAGE score.

**Used by QT-124 (feature `USE_KEYVI_CORRECTIONS`)** as replacement for DAWG+TrigramDB:
- `get_fuzzy_corrections(token, max_edit_distance, num)` — Keyvi native fuzzy lookup
- `get_fuzzy_completions(token, max_edit_distance, min_exact_prefix=1)` — prefix completion

**Edit distance thresholds (length-based):**

| Token length | Max edit distance | Max results |
|---|---|---|
| < 3 | 0 (no fuzzy) | 5 |
| 3-5 | 1 | 5 |
| 6-7 | 2 | 7 |
| 8+ | 3 | 20 |

**Completion thresholds:**

| Token length | Max edit distance | Max results |
|---|---|---|
| < 3 | 0 | 150 |
| 3-5 | 1 | 100 |
| 6-7 | 2 | 50 |
| 8+ | 3 | 30 |

Score adjustment: `compute_correction_score()` / `compute_completion_score()` using Damerau-Levenshtein + phonetic distance + typo distance.

### Language Model

KenLM n-gram model trained on normalized token sequences from catalog items. Training data: item tokens → stemmed, sorted → space-joined sentences.

Used in QS correction candidate scoring:
```
candidate_score(phrase) = log(max(1, LM_score × DAWG_score))
```
where `LM_score = 10^(kenlm.score(phrase, bos=True, eos=True))`.
