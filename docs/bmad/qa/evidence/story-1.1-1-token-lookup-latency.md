# Story 1.1-1 Cached Token Lookup Latency Evidence

**Date:** 2025-10-07 10:00:45 IST
**Engineer:** James (Dev)

## Benchmark Context

- **Purpose:** Demonstrate that cached calls to `get_token_from_symbol` complete in under 100 ms as required by Story 1.1-1 AC6.
- **Script:** `python3 scripts/benchmark_jainam_token_lookup.py`
- **Dataset:** Synthetic master contract with 120,000 instruments across all Jainam exchange segments (NSECM, NSEFO, NSECD, BSECM, BSEFO, MCXFO).
- **Iterations:** 500 cached lookups per exchange per repeat.
- **Repeats:** 5 measurement repeats per exchange.
- **Database:** Ephemeral SQLite database seeded via `save_master_contract_to_db` (identical persistence path used in production).

## Reproduction Command

```bash
python3 scripts/benchmark_jainam_token_lookup.py \
  --instrument-count 120000 \
  --iterations 500 \
  --repeat 5
```

## Results Summary

| Exchange | Warm Lookup (ms) | Cached Avg (ms) | Cached Min (ms) | Cached Max (ms) | Cached p95 (ms) |
|----------|------------------|-----------------|-----------------|-----------------|-----------------|
| BFO | 0.52 | 0.0004 | 0.0004 | 0.0004 | 0.0004 |
| BSE | 0.19 | 0.0004 | 0.0004 | 0.0004 | 0.0004 |
| CDS | 0.14 | 0.0004 | 0.0004 | 0.0004 | 0.0004 |
| MCX | 0.15 | 0.0004 | 0.0004 | 0.0004 | 0.0004 |
| NFO | 0.12 | 0.0004 | 0.0004 | 0.0004 | 0.0004 |
| NSE | 0.13 | 0.0004 | 0.0004 | 0.0004 | 0.0004 |

- **Master Contract Load Time:** 16,667.80 ms (one-off refresh across 120k instruments).
- **Observation:** Cached lookups remain four orders of magnitude below the 100 ms SLA, even with a production-sized contract.

## Conclusion

The cached token lookup path satisfies Story 1.1-1 AC6 with substantial headroom. Evidence stored for QA reference.
