---
id: qu_finalizer
title: "Finalizer"
type: block
position: 5
---

## Finalizer (overrides, skip tokens)

Applies per-customer DynamoDB overrides to correction candidates after scoring:

| Step | What it does | Example |
|---|---|---|
| Inclusions | Force-add specific corrections | "iphone" always corrects to "iPhone" |
| Exclusions | Remove specific corrections | Block "macbook" → "mac book" |
| Skip tokens | Remove stop words from candidates | "for", "the" stripped per-customer config |

### Data source

Managed by Customer Success team via internal tools. Stored in DynamoDB, delivered to QS by DB Data Downloader sidecar.

Used as an escape hatch when algorithmic correction produces wrong results for specific queries.
