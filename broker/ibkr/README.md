# IBKR Stability Protocol (Version 5.5)

This protocol documents the "Hardened" integration for Interactive Brokers within OpenAlgo. 

### Core Stability Features (Verified Ver 5.5)

1.  **Sovereign Order Lane**: All orders go through **Client ID 0**. This ensures priority and bypasses socket collisions.
2.  **Stable Data Lanes**: 
    *   Positions use `clientId + 400`.
    *   Orders Book uses `clientId + 15`.
    *   Streaming uses `clientId + 99`.
    *   All connections use a **Synchronized Retry** with incremental shifts (+10) to find open lanes.
3.  **Dynamic Contract Hijacking (Scan & Kill)**: 
    *   The system scans the live TWS portfolio to find open positions.
    *   It retrieves the exact `conId`, `multiplier`, and `exchange` from the portfolio.
    *   Exit orders are built using this live contract data, ensuring 100% acceptance.
4.  **MarketPrice Shield**: 
    *   Uses `ib.marketPrice()` for streaming, providing robust bid/ask midpoint fallbacks when trades are thin.
    *   Enforces strict float validation for `market_data_service` compatibility.
5.  **Forex/Option Mapping**: 
    *   Auto-detects `EUR.USD` as **CASH**.
    *   Auto-detects `WL2J6 C11500` and similar fragments as **OPT**.

---

### Key Utilities

*   **`broker/ibkr/api/utils.py`**: Contains `close_ibkr_position()` and `close_all_ibkr_positions()`. These are for use in Python strategies.
*   **`scripts/ibkr_emergency_exit.py`**: Terminal-ready panic button. Run `python scripts/ibkr_emergency_exit.py ALL`.
*   **`scripts/test_ibkr_streaming_v2.py`**: Validates data flow quality.

---

### Dashboard Troubleshooting

*   **Spinning Positions**: If the Positions tab spins, ensure TWS is not being bombarded by too many scripts and that the `bcid` in `.env` is correct. The sync wait is now locked at **3.0 seconds** for optimal stability.
*   **Missing LTP**: If the dashboard shows 0.0, check the `websocket_proxy` logs for `reqMktData` errors.
*   **Security Definition Not Found**: Check `transform_data.py` to ensure the symbol mapping correctly identifies the instrument type (STK vs OPT vs FUT).

### Master Configuration
| Feature | Client ID | Purpose |
| :--- | :--- | :--- |
| **Orders** | 0 | Sovereign Lane (Priority) |
| **Book** | +15 | Order tracking |
| **Positions** | +400 | Portfolio sync |
| **Streaming** | +99 | Live market data |
| **Strategies** | +10 | Background execution |

---
**Status: STABLE / PRODUCTION READY**
Last Updated: 2026-04-08
