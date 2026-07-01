---
id: qu_tokenize
title: "Tokenize + Classify"
type: block
position: 2
---

## Tokenize + Classify

Whitespace split (max 15 tokens), then per-token classification:

| Token | Classification | Action |
|---|---|---|
| "macbok" | Not in vocabulary | → fuzzy correct |
| "pro" | Exact match (known catalog term) | → passthrough |
| "13in" | Entity (physical unit) | → passthrough |

Token types that bypass fuzzy correction:

| Type | How detected | Example |
|---|---|---|
| Exact matches | Found in `exact_searchable_identifiers` | SKU "AB-1234", model "xps15" |
| Acronyms | `A:` prefix in vocabulary | "LED", "USB" |
| Entities | `cnstrc_qnlp` unit detection | "10mm", "2x4", "5kg" |
| Numeric | All digits | "123", "2024" |
| CJK | Unicode range check | (optional, per feature flag) |
