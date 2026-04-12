# Story 1.2-1 Latency Evidence (Positions & Holdings)

- **Date:** 2025-10-07
- **Engineer:** Codex (Dev)
- **Objective:** Validate IV3 requirement that Jainam positions and holdings pipelines finish within 5 seconds under simulated production-like latency.
- **Method:** Ran `scripts/measure_jainam_portfolio_latency.py`, which replays captured Jainam payloads, injects realistic network delays (1.20s positions, 1.35s holdings), and exercises the full mapping pipeline—including quote enrichment that depends on market token propagation.

```bash
$ python3 scripts/measure_jainam_portfolio_latency.py
========================================================================
Jainam Positions & Holdings Latency Benchmark (Simulated)
========================================================================
[2025-10-07 15:33:32,096] INFO in order_data: Transforming positions data
[2025-10-07 15:33:33,453] INFO in order_data: Mapping portfolio data
[2025-10-07 15:33:33,453] INFO in order_data: Calculating portfolio statistics
[2025-10-07 15:33:33,454] INFO in order_data: Transforming holdings data

Positions pipeline completed in 1.207s for 2 positions.
Holdings pipeline completed in 1.357s for 2 holdings.
Total portfolio value: 86375.00
Total P&L: 1375.00

Requirement: Each pipeline must complete in < 5.000 seconds.
Combined simulated latency: 2.564s (<5s target met).
✅ Latency requirement satisfied under simulated network load.
```

- **Result:** Both pipelines completed in 2.564 seconds combined, well under the 5 second IV3 threshold. Quote enrichment affirmed that the market token is available throughout the holdings pipeline.
- **Next Action:** Re-run the benchmark with live Jainam credentials once production connectivity is available to capture real-world telemetry.
