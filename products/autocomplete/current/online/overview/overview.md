---
id: overview
title: "Autocomplete Overview"
type: block
position: 1
---

## Autocomplete

Real-time suggestions as the user types — combining prefix matching, popularity signals, personalization, and result preview. Must respond in <50ms per keystroke.

### Key Components

| Component | Description | Status |
|-----------|-------------|--------|
| Prefix matching | Trie/DAWG-based prefix lookup | TODO |
| Candidate ranking | ML model scoring suggestion candidates | TODO |
| Personalization | User-specific suggestion boosting | TODO |
| Result types | Items, queries, categories, brands in suggestions | TODO |
| Latency budget | <50ms total including network | TODO |

### Differences from Search Suggestions

- Triggered on every keystroke (not on submit)
- Much stricter latency requirements
- Shows mixed result types (items + suggestions + categories)
- Prefix-based matching (not full query understanding)
