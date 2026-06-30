---
id: suggestions
title: "Suggestion Generation"
position: 1
---

## Suggestion Generation

### CreateSearchSuggestions

Source: `DedupBehavioralLogs` (action=`search`), per `ac_key`.

**Algorithm:**
1. Filter to search events, count per term, drop terms with `count < min_searches_count`
2. Construct `UserSearch` objects (with NLTK `WordNetLemmatizer` lemmatization)
3. Four-pass deduplication (`reduceByKey` on Spark RDD):
   - **Plural dedup:** key = `WordNetLemmatizer.lemmatize(name)` (singular form)
   - **Spacing dedup:** key = `''.join(name.split())` (strip all spaces)
   - **Inverted word-order dedup:** key = `' '.join(sorted(name.split()))`
   - **Stem dedup:** key = `extended_tokenize(name, stem=True)` (stemmed form)
4. Merge whitelisted terms (always included regardless of count)
5. Subtract existing DSI items (5 passes: exact, singular, spaceless, sorted-words, stemmed)
6. Sort by `(count DESC, name ASC)`

**Parameters:**
```
min_searches_count:  4 (1d period), 3 (multi-day period)
MAX_SS_LINE_LENGTH:  80 characters
MIN_TERM_LENGTH:     3 characters
MAX_SEARCH_WORD_LENGTH: 5 words
BAD_CHARACTERS:      ['-', ',', ':', ';', '"', '@', '|']
nostem_terms:        ['ski', 'skis'] (excluded from stem dedup)
```

**Output:** S3 CSV `{ac_key}/{period}_period.csv` — columns: `name, count`.

### PrepNewSearchSuggestionsForDB

Validates candidates against live search API.

**Algorithm:**
1. Batch search (16 per batch, 64 partitions, ThreadPool) via autocomplete API
2. Validation per suggestion (`is_valid_ss`):
   - Reject HTML in name
   - Check against blacklist (tokenized stem matching)
   - Verify: ≥1 result item's `matched_terms` is a subset of suggestion tokens
   - Two matching modes: `_match_basic()` (single-stem), `_match_extended()` (synonym resolution, double-stemming)
3. Enrichment:
   - `get_top_groups()`: top 3 product category groups from API results
   - `get_top_facets_sets()`: inherits facet values from top products
   - Image URL from first result item
4. Raise `SSValidationError` if invalid ratio exceeds `max_invalid_ss_ratio=0.5`

### UpdateSearchSuggestionsInDB

**Algorithm:**
1. Re-validate existing suggestions (`UpdateExistingSearchSuggestions`) — deactivate orphaned
2. Validate new candidates (`PrepNewSearchSuggestionsForDB`)
3. Merge 1d + period outputs; dedup by name; assign A/B test cells:
   - `cell_a` = from 1d window only
   - `cell_b` = from period window only
   - `cell_c` = in both (intersection)
4. Upload to catalog API in chunks of 1000 (250 for slow customers)
5. `reset_last_update()` → triggers index rebuild

**Parameters:**
```
max_deactivated_ratio: 0.35
num_top_groups:        3
num_results:           10 (API call limit per suggestion)
```

**Blacklisting:** per-ac_key YAML (`ss_blacklisted_terms_path`) + inline list (`ss_blacklisted_terms`).

**Scheduling:** `30 12 * * *` (12:30 UTC daily), `DailyUpdateAllSearchSuggestionsInDB`.
