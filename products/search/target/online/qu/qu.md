---
id: qu
title: "Query → Structure (Engineering)"
type: block
position: 2
---

## Query → Structure (Engineering)

Online decision layer. Determines HOW to search, before any products are known.

### Responsibilities

- **Intent classification** — quota routing (which retrieval streams get more candidates)
- **Main noun extraction** — relevance constraint (product must BE this thing)
- **Attribute extraction** — structured filters (price, brand, size, color)
- **Category classification** — hard/soft category constraint
- **Ambiguity detection** — diversity strategy, multi-category routing

### Category constraint modes

```
"table lamp"    → category: Lighting/Table Lamps → excludes tables
"running shoes" → category: Footwear/Running     → excludes running accessories
"macbook pro"   → category: Electronics/Laptops  → excludes cases and accessories
```

- **Hard filter** (high confidence) — out-of-category items excluded from pool
- **Soft boost** (ambiguous) — out-of-category demoted but not excluded
- **Multi-category** (ambiguity) — "apple" → Electronics + Grocery

### Main noun matching

```
Query: "table lamp"        → main noun: lamp
Item:  "table for lamp"    → main noun: table     → mismatch ✗
Item:  "brass table lamp"  → main noun: lamp      → match ✓

Query: "running shoes"     → main noun: shoes
Item:  "shoe rack"         → main noun: rack      → mismatch ✗
Item:  "Nike running shoes"→ main noun: shoes     → match ✓
```

If query main noun ≠ item main noun — item is irrelevant, even if all tokens are present.

### Attribute extraction → filters

```
"red dress under $50"       → color: red, price: < $50
"samsung tv 55 inch"        → brand: Samsung, size: 55"
"wireless headphones under 100" → feature: wireless, price: < $100
```

Principle: everything that can become a structured filter — becomes one. Narrows search space, removes irrelevant before retrieval, guarantees constraint.
