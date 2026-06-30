---
id: caching
title: "Caching & Delta Index"
position: 6
---

## Caching & Delta Index

### Redis cache (SABR Caching)

- Feature: `SABR_CACHING`
- **Write:** after serving, if `processing_time > threshold_ms` (default 500ms) → write to Redis with TTL (default 300s)
- **Read:** check Redis before processing; return immediately on hit (`Results-Cache-Used: true`)
- **Key:** path + sorted args + request_type (strips personalization params: `ui`, `i`, `s`, `c`)
- **Value:** JSON → zlib compressed (level 3)
- **Bypass:** when searchandizing rules, blacklist, explain, or `DISABLE_CACHE` active
- Redis: separate read-replica and write connections

### Batch pre-warming

`ResultsCacheDB.set_batch()` via Redis pipeline. Called with pre-computed responses for popular queries (e.g., from `/v1/batch_autocomplete` for top-N queries).

### Delta Index

Incremental index for fast item updates without full rebuild.

**Build:**
- Opt-in per customer: `build_delta_index=True`
- Fetches only DSIs updated since primary index build (`min_updated_at`)
- Aborts if changed items exceed `item_count × incremental_index_items_changed_ratio` → falls back to full rebuild
- Includes deactivated items (tombstones)

**Serve:**
Delta stores specific key-value datasets:
```
DELTA_DATA_SETS = ["dsi_id_to_customer_id", "customer_id_to_dsi_id",
                   "customer_id_to_internal_id_range", "deactivated_dsis"]
```

Merge logic: delta wins for keys it has; primary covers the rest. Items present in delta's "ALL:" token skip list are excluded from primary index results.

Feature: `USE_DELTA_INDEX` passed via gRPC to index service.
