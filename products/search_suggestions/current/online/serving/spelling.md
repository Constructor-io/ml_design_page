---
id: spelling
title: "Spelling Correction (Query Service)"
position: 2
---

## Spelling Correction (Query Service)

### Architecture

Query Service (QS) — Rust/C++ gRPC service. Two RPC methods:

1. `GetSpellingCorrections` → `GetSpellingCorrectionsResponse`
2. `GetKeysetsAndBoosts` → `GetKeysetsAndBoostsResponse`

### GetSpellingCorrections

**Input:** `(ac_id, query, is_autocomplete, is_search_suggestion_section, feature_params)`

**Output:**
```
GetSpellingCorrectionsResponse {
    PhraseCorrection original_phrase;
    string best_correction;
    bool are_all_tokens_exact_searchable;
    repeated CorrectionResult first_run_corrections;
    repeated CorrectionResult second_run_corrections;
    CorrectionExplanation explanation;
}
```

**TokenCorrection:**
```
TokenCorrection {
    string raw_token;              // what user typed
    string correction;             // corrected form
    string normalized_correction;  // stemmed form
    uint32 score;                  // DAWG/Keyvi score
    uint32 score_adjustment;       // EXACT_MATCH=3, BOOST=5, IDENTITY=1
    bool is_exact_match;           // exact searchable identifier
    bool is_completion;            // prefix-completed (autocomplete mode)
    bool is_fuzzy_match;
    bool is_join;                  // joined two tokens
    bool is_acronym;
    bool is_numeric;
    bool is_cjk;
}
```

**Phrase scoring:** harmonic mean of token scores:
```
score(phrase) = N / (1/s₁ + 1/s₂ + ... + 1/sₙ)
```

### First-Pass vs Second-Pass

- **First-pass corrections:** primary candidates from a single QS call
- **Second-pass corrections:** backup candidates, used only if first-pass retrieval returns insufficient results:
  - Autocomplete: `< 6` unfiltered results
  - Search: `< 3` unfiltered results
- Second-pass disabled if `always_only_best_suggestion=True` or `disable_second_pass=True` (QT-286)
- Feature `ALWAYS_USE_ALL_SPELLING_CORRECTIONS` forces both passes always
