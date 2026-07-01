---
id: qu_fuzzy
title: "DAWG Fuzzy Lookup"
type: block
position: 3
---

## DAWG Fuzzy Lookup

For each token needing correction, query the DAWG vocabulary. Example for "macbok":

| Suggestion | Edit distance | DAWG score | Why |
|---|---|---|---|
| macbook | 1 | 0.95 | High catalog frequency |
| macbok | 0 (original) | 0.12 | Low catalog frequency |

Max edit distance scales with token length:

| Token length | Max edit distance |
|---|---|
| < 3 chars | 0 (no fuzzy) |
| 3–5 chars | 1 |
| 6–7 chars | 2 |
| > 7 chars | 3 |

Also checks `missing_spaces` DB: "macbookpro" → "macbook pro".

### DAWG vocabulary

DAWG (Directed Acyclic Word Graph) is a compressed trie built from all text in the customer's product catalog. Each token has an associated score reflecting how "important" it is in the catalog (frequency-weighted).

Built per-customer by Index Builder. Updated continuously as catalog changes.
