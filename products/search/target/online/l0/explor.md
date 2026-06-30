---
id: explor
title: "Exploration Stream"
type: block
position: 9
---

## Exploration Stream

**Problem:** Vicious cycle: no impressions → no clicks → no interaction signal → models don't rank it → no impressions.

### Affected items

- New items in catalog
- Long-tail items with few impressions
- Items after attribute changes (new photo, price, description)

### Mechanics

A percentage of the retrieval quota is reserved for exploration:

```yaml
exploration:
  min_fraction: 0.03        # lower bound (customer config)
  max_fraction: 0.15        # upper bound (customer config)
  eligible:
    - impressions < threshold
    - created_at > now - N days
    - updated_at > now - N days
  ranking_within: content-based relevance to query
```

Exact percentage within limits is determined by QU per-query (navigational query → closer to min, exploratory → closer to max).

### Graduation

An item exits the exploration pool once it accumulates enough impressions — after that, models can rank it normally based on accumulated interaction signal.
