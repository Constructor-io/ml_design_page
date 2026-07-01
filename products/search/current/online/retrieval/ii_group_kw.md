---
id: ii_group_kw
title: "group_keywords"
type: block
position: 5
---

## group_keywords

Same algorithm as `behavior_keywords`, but aggregated by `group_id` instead of `item_id`. If many actions happen with items in a group by a specific token, all items in that group get a boost.

### Properties

| Property | Value |
|----------|-------|
| Scope | token-group pair |
| Delivery | S3 |
| Applied at | Index build time |
| Range | [1.7 - 5.7] * 200,000 |
| Pipeline | `pipelines.ingest_behavioral_keywords.groups.GroupBehavioralKeywordsToS3Index` |

### Difference from behavior_keywords

- **behavior_keywords**: token "shoes" → item123 gets boost because people who searched "shoes" clicked item123
- **group_keywords**: token "shoes" → all items in group "Nike Running" get boost because people who searched "shoes" clicked items in that group

This helps items with few individual clicks benefit from group-level popularity.
