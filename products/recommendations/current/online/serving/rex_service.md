---
id: rex_service
title: "rex_service (New Microservice)"
position: 5
---

## rex_service (Standalone Microservice)

```
Framework:      FastAPI
Port:           8097
Deploy:         AWS ECS Fargate
Strategies:     bestsellers, filtered_items (only)
Backend:        direct gRPC to InvertedIndexConnector (no monolith TermsProcessor)
Max results:    500 (internal)
Pod cache:      PodInfoProvider (MySQL, background refresh)
Features:       FeaturesProvider (DB + EFT v1/v2 from S3, background refresh)
```

### apply_merchandising_and_filtering()

1. Build browse/collection iterators
2. Build facet iterators (blacklist/whitelist/boost/filter)
3. Execute Index Service query (gRPC)
4. Convert to `RecommendationItem` with strategy_id, is_backfilled, labels

### Serving comparison

| Aspect | fuzzy_autocomplete_server (legacy) | rex_service (new) |
|--------|------|------|
| Framework | Flask | FastAPI |
| Strategies | All 12+ | bestsellers, filtered_items only |
| Index access | via KV Service + TermsProcessor | direct gRPC to InvertedIndexConnector |
| Personalization | Full (PersonalizeREX, LinearPersonalREX) | None |
| Status | Production, all customers | Production, limited strategies |
