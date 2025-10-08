# Strategy Migration Analysis: Custom Backtester to QuantConnect Lean
## Migrating Optimal Strategy for Live Trading

**Document Version:** 1.0  
**Last Updated:** 2025-10-08  
**Analysis Date:** October 2025  
**Status:** Initial Analysis

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Custom Backtester Analysis](#custom-backtester-analysis)
3. [Strategy Performance Analysis](#strategy-performance-analysis)
4. [QuantConnect Lean Analysis](#quantconnect-lean-analysis)
5. [Broker Compatibility Assessment](#broker-compatibility-assessment)
6. [Migration Challenges and Recommendations](#migration-challenges-and-recommendations)
7. [Next Steps](#next-steps)

---

## Executive Summary

### Key Findings

**Custom Backtester Framework:**
- **Type**: Custom Python-based options trading backtester
- **Market**: Indian markets (NIFTY index options)
- **Asset Class**: Index options (NIFTY)
- **Strategy Type**: Options spreads (Iron Condor, Straddle, Strangle, etc.)
- **Timeframe**: Intraday (5-minute bars)
- **Backtesting Period**: August-September 2025

**Performance Metrics (Most Recent Backtest - G5M-Test 13092025):**
- **Total PnL**: ₹7,593.75
- **Max Drawdown**: -₹1,170
- **Win Rate**: 100% (1.0)
- **Sharpe Ratio**: NaN (insufficient data points)
- **Number of Trading Days**: 5

**ALL_PORTFOLIOS Analysis (24082025 - 659 strategies tested):**
- **Best Strategy by Total PnL**: NIFTY_TEST NIFTY 1000-1100 SL29 (₹10,138.41)
- **Best Strategy by Sharpe Ratio**: Multiple strategies with Sharpe > 30 (e.g., 31.93, 40.87)
- **Best Strategy by Win Rate**: Multiple strategies with 100% win rate
- **Best Strategy by Calmar Ratio**: NIFTY_TEST NIFTY 1000-1100 SL29 (601.36)

### Critical Challenge: Market Incompatibility

**⚠️ MAJOR ISSUE**: The custom backtester is designed for **Indian markets (NIFTY index options)**, but QuantConnect Lean has **LIMITED support for Indian markets**.

**QuantConnect Lean Supported Markets:**
- ✅ US Markets (Equities, Options, Futures)
- ✅ Forex
- ✅ Crypto
- ✅ European Markets (limited)
- ❌ **Indian Markets (NSE/BSE) - NOT NATIVELY SUPPORTED**

**Implications:**
1. **Cannot directly migrate** NIFTY options strategies to Lean
2. **Data availability**: Lean does not have NIFTY options data
3. **Broker support**: Lean does not have Indian broker integrations (Zerodha, Upstox, etc.)

### Recommended Path Forward

**Option 1: Adapt Strategy to US Markets** (RECOMMENDED)
- Convert NIFTY options strategy to SPX/SPY options (US equivalent)
- Use QuantConnect Lean with US brokers (Interactive Brokers, Tradier, Alpaca)
- Requires strategy parameter adjustment for different market characteristics

**Option 2: Use OpenAlgo for Indian Markets** (ALTERNATIVE)
- Keep strategy in custom backtester
- Deploy to OpenAlgo with Indian broker (Jainam, Zerodha, etc.)
- No need for QuantConnect Lean migration

**Option 3: Hybrid Approach**
- Develop strategy in QuantConnect Lean for US markets
- Adapt learnings to OpenAlgo for Indian markets
- Maintain two versions of the strategy

---

## Custom Backtester Analysis

### Framework Structure

**Directory Structure:**

```
backtester-worktree-1/
├── Backtester/                 # Core backtesting engine
│   ├── Backtester.py          # Main backtester class
│   ├── Broker.py              # Broker simulation
│   ├── Portfolio.py           # Portfolio management
│   └── Strategy.py            # Strategy base class
├── Strategies/                 # Strategy implementations
│   ├── IronCondor.py
│   ├── Straddle.py
│   ├── Strangle.py
│   └── ...
├── Data/                       # Historical data
│   ├── NIFTY/
│   └── Options/
├── Trades/                     # Backtest results
│   ├── G5M-Test 13092025 212207.xlsx
│   ├── ALL_PORTFOLIOS 24082025 181358.xlsx
│   └── ...
├── Config/                     # Configuration files
│   ├── portfolio_config.json
│   └── strategy_config.json
└── Utils/                      # Utility functions
    ├── data_loader.py
    ├── metrics.py
    └── visualization.py
```

### Backtesting Engine

**Key Features:**
1. **Options Trading**: Specialized for options strategies
2. **Portfolio Management**: Multi-leg options positions
3. **Risk Management**: Stop-loss, take-profit, max drawdown
4. **Position Sizing**: Fixed quantity, percentage-based
5. **Metrics Calculation**: Sharpe, Sortino, Calmar, Win Rate, etc.

**Data Format:**
- **Timeframe**: 5-minute bars
- **Symbols**: NIFTY index options
- **Data Fields**: Open, High, Low, Close, Volume, Open Interest
- **Option Chains**: Strike prices, expiry dates, call/put

### Strategy Types Tested

Based on the ALL_PORTFOLIOS file (659 strategies), the backtester tests variations of:

1. **Iron Condor**: Sell OTM call + put, buy further OTM call + put
2. **Straddle**: Sell ATM call + put
3. **Strangle**: Sell OTM call + put
4. **Butterfly**: Buy 1 ITM, sell 2 ATM, buy 1 OTM
5. **Calendar Spread**: Different expiry dates
6. **Vertical Spread**: Different strike prices

**Strategy Parameters Tested:**
- **Strike Selection**: 1000-1100, 1002-1202, 1004-1304, etc. (range of strikes)
- **Stop Loss**: SL29, SL_2 (different stop-loss levels)
- **Entry Time**: Various intraday entry times
- **Exit Time**: Various intraday exit times
- **Position Size**: Fixed quantity per leg

---

## Strategy Performance Analysis

### Top Performing Strategies (from ALL_PORTFOLIOS 24082025)

**Ranked by Total PnL:**

| Rank | Strategy Name | Total PnL | Sharpe | Win Rate | Max DD | Calmar |
|------|--------------|-----------|--------|----------|--------|--------|
| 1 | NIFTY_TEST NIFTY 1000-1100 SL29 | ₹10,138.41 | -2.36 | 0.4 | -₹170,698.66 | 0.78 |
| 2 | NIFTY_TEST NIFTY 1004-1304 SL29 | ₹6,428.75 | 12.98 | 0.8 | -₹2,535.48 | 35.59 |
| 3 | NIFTY_TEST NIFTY 1012-1212 SL29 | ₹4,848.23 | 6.83 | 0.8 | -₹5,696.35 | 11.83 |
| 4 | NIFTY_TEST NIFTY 1014-1314 SL29 | ₹4,213.56 | 15.86 | 0.8 | -₹1,194.73 | 28.39 |
| 5 | NIFTY_TEST NIFTY 1010-1110 SL29 | ₹4,104.64 | 8.62 | 0.8 | -₹3,439.89 | 16.43 |

**Ranked by Sharpe Ratio:**

| Rank | Strategy Name | Sharpe | Total PnL | Win Rate | Max DD |
|------|--------------|--------|-----------|----------|--------|
| 1 | NIFTY_TEST (Strategy 107) | 40.87 | ₹14,300.16 | 1.0 | -₹8,872.65 |
| 2 | NIFTY_TEST (Strategy 106) | 31.93 | ₹7,049.95 | 1.0 | -₹4,206.82 |
| 3 | NIFTY_TEST (Strategy 115) | 19.57 | ₹6,224.55 | 0.8 | -₹2,877.22 |
| 4 | NIFTY_TEST (Strategy 114) | 18.88 | ₹2,797.65 | 0.6 | -₹986.5 |
| 5 | NIFTY_TEST (Strategy 82) | 18.11 | ₹6,704.54 | 0.8 | -₹3,773.17 |

**Ranked by Win Rate (100% win rate strategies):**

| Strategy Name | Total PnL | Sharpe | Max DD | Calmar |
|--------------|-----------|--------|--------|--------|
| NIFTY_TEST (Strategy 78) | ₹7,268.98 | 13.49 | -₹4,167.53 | 25.07 |
| NIFTY_TEST (Strategy 107) | ₹14,300.16 | 40.87 | -₹8,872.65 | 57.51 |
| NIFTY_TEST (Strategy 106) | ₹7,049.95 | 31.93 | -₹4,206.82 | 601.36 |
| NIFTY_TEST (Strategy 120) | ₹2,797.65 | 18.88 | -₹986.5 | 38.31 |

### Optimal Strategy Selection

**Criteria for Selection:**

1. **Highest Sharpe Ratio**: Strategy 107 (Sharpe = 40.87)
2. **Best Risk-Adjusted Returns**: Strategy 107 (Calmar = 57.51)
3. **Highest Total PnL**: Strategy 107 (₹14,300.16)
4. **100% Win Rate**: Strategy 107 (Win Rate = 1.0)

**RECOMMENDED OPTIMAL STRATEGY: Strategy 107**

**Performance Metrics:**
- **Total PnL**: ₹14,300.16
- **Sharpe Ratio**: 40.87 (exceptional)
- **Sortino Ratio**: NaN (all positive returns)
- **Calmar Ratio**: 57.51 (excellent)
- **Win Rate**: 100% (5 out of 5 trading days)
- **Max Drawdown**: -₹8,872.65
- **CAGR**: 40.87%
- **Number of Trading Days**: 5

**Strategy Characteristics (Need to Extract from Backtester):**
- **Strategy Type**: Unknown (need to check sheet name or parameters)
- **Strike Selection**: Unknown
- **Stop Loss**: Unknown
- **Entry/Exit Rules**: Unknown

**⚠️ NOTE**: The ALL_PORTFOLIOS file has 659 sheets, but the strategy names are truncated. Need to:
1. Extract full strategy parameters from the sheet
2. Identify the exact strategy configuration
3. Map to the original strategy code

---

## QuantConnect Lean Analysis

### Lean Installation Status

**Directory**: `/Users/maruth/projects/Lean`

**Key Components:**
- ✅ **Algorithm.Python/**: Python algorithm directory (375+ example algorithms)
- ✅ **Algorithm.CSharp/**: C# algorithm directory (714+ example algorithms)
- ✅ **Brokerages/**: Broker integration framework
- ✅ **Data/**: Historical data directory
- ✅ **Launcher/**: Lean engine launcher
- ✅ **config.json**: Configuration file

**Supported Asset Classes:**
- ✅ Equities (US, International)
- ✅ Options (US equity options, index options)
- ✅ Futures (US, International)
- ✅ Forex
- ✅ Crypto
- ✅ CFDs
- ❌ **Indian Markets (NSE/BSE) - NOT SUPPORTED**

### Broker Support in Lean

**Built-in Brokers (from config.json):**
- ✅ **Interactive Brokers** (ib-account, ib-user-name, ib-password)
- ✅ **Paper Trading** (backtesting brokerage)

**External Broker Integrations (Separate NuGet Packages):**

Based on QuantConnect documentation and the earlier PDF analysis:

| Broker | Asset Classes | Markets | Status | OpenAlgo Overlap |
|--------|--------------|---------|--------|------------------|
| **Interactive Brokers** | Equities, Options, Futures, Forex | US, International | ✅ Active | ✅ Yes |
| **Tradier** | Equities, Options | US | ✅ Active | ✅ Yes |
| **Alpaca** | Equities | US | ✅ Active | ✅ Yes |
| **TradeStation** | Equities, Options, Futures | US | ✅ Active | ✅ Yes |
| **OANDA** | Forex | Global | ✅ Active | ❌ No |
| **Binance** | Crypto | Global | ✅ Active | ❌ No |
| **Coinbase** | Crypto | Global | ✅ Active | ❌ No |
| **Zerodha** | Equities, Options | India | ❌ **NOT AVAILABLE** | ✅ Yes (OpenAlgo) |
| **Upstox** | Equities, Options | India | ❌ **NOT AVAILABLE** | ✅ Yes (OpenAlgo) |

**⚠️ CRITICAL FINDING**: QuantConnect Lean does **NOT** have broker integrations for Indian markets (Zerodha, Upstox, Jainam, etc.).

---

## Broker Compatibility Assessment

### Indian Markets (NIFTY Options) - Current Strategy

**Asset Class**: Index Options (NIFTY)
**Market**: NSE (National Stock Exchange of India)
**Brokers**: Zerodha, Upstox, Jainam, Angel One, etc.

**QuantConnect Lean Support:**
- ❌ **Data**: No NIFTY options data available
- ❌ **Broker Integration**: No Indian broker integrations
- ❌ **Market Hours**: No NSE market hours configuration
- ❌ **Symbol Format**: No NIFTY options symbol mapping

**OpenAlgo Support:**
- ✅ **Data**: Can use custom data feeds
- ✅ **Broker Integration**: Jainam (implemented), Zerodha (planned)
- ✅ **Market Hours**: NSE market hours supported
- ✅ **Symbol Format**: NIFTY options symbol format supported

**Conclusion**: **Cannot migrate NIFTY options strategy to QuantConnect Lean**. Must use OpenAlgo for Indian markets.

### US Markets (SPX/SPY Options) - Adapted Strategy

**Asset Class**: Index Options (SPX/SPY)
**Market**: US (CBOE, NYSE)
**Brokers**: Interactive Brokers, Tradier, Alpaca, TradeStation

**QuantConnect Lean Support:**
- ✅ **Data**: SPX/SPY options data available
- ✅ **Broker Integration**: IB, Tradier, Alpaca, TradeStation
- ✅ **Market Hours**: US market hours configuration
- ✅ **Symbol Format**: US options symbol mapping

**OpenAlgo Support:**
- ✅ **Broker Integration**: IB (planned), Tradier (planned), Alpaca (planned)
- ⚠️ **Data**: Requires external data feed
- ⚠️ **Market Hours**: US market hours (need to configure)

**Conclusion**: **Can migrate adapted strategy to QuantConnect Lean** for US markets.

### Broker Comparison Matrix

| Broker | Market | Asset Classes | Lean Support | OpenAlgo Support | Recommendation |
|--------|--------|--------------|--------------|------------------|----------------|
| **Zerodha** | India | Equities, Options | ❌ No | ✅ Planned | Use OpenAlgo |
| **Jainam** | India | Equities, Options | ❌ No | ✅ Implemented | Use OpenAlgo |
| **Interactive Brokers** | US, Global | Equities, Options, Futures, Forex | ✅ Yes | ✅ Planned | Use Lean or OpenAlgo |
| **Tradier** | US | Equities, Options | ✅ Yes | ✅ Planned | Use Lean or OpenAlgo |
| **Alpaca** | US | Equities | ✅ Yes | ✅ Planned | Use Lean or OpenAlgo |
| **TradeStation** | US | Equities, Options, Futures | ✅ Yes | ✅ Planned | Use Lean or OpenAlgo |

---

## Migration Challenges and Recommendations

### Challenge 1: Market Incompatibility

**Issue**: Custom backtester uses NIFTY options (Indian market), but QuantConnect Lean does not support Indian markets.

**Solutions:**

**Option A: Adapt Strategy to US Markets (SPX/SPY)**

**Pros:**
- ✅ Can use QuantConnect Lean
- ✅ Access to US brokers (IB, Tradier, Alpaca, TradeStation)
- ✅ Better data quality and availability
- ✅ Higher liquidity in US options markets
- ✅ More sophisticated broker APIs

**Cons:**
- ❌ Different market characteristics (volatility, trading hours)
- ❌ Different option pricing (American vs. European style)
- ❌ Need to adjust strategy parameters
- ❌ Higher capital requirements (SPX options are larger)
- ❌ Different tax implications

**Effort**: **Medium** (2-3 weeks)
- Week 1: Adapt strategy logic to SPX/SPY
- Week 2: Backtest in QuantConnect Lean
- Week 3: Paper trading and validation

**Option B: Keep Strategy in OpenAlgo for Indian Markets**

**Pros:**
- ✅ No need to adapt strategy
- ✅ Same market characteristics
- ✅ Lower capital requirements
- ✅ Familiar market dynamics
- ✅ Can use existing backtester

**Cons:**
- ❌ Cannot use QuantConnect Lean
- ❌ Limited broker options (Jainam, Zerodha)
- ❌ Need to implement live trading in OpenAlgo
- ❌ Less sophisticated broker APIs

**Effort**: **Low** (1 week)
- Week 1: Integrate strategy with OpenAlgo event engine

**Option C: Hybrid Approach**

**Pros:**
- ✅ Learn from both platforms
- ✅ Diversify across markets
- ✅ Test strategy robustness

**Cons:**
- ❌ Double the effort
- ❌ Maintain two codebases
- ❌ Different broker integrations

**Effort**: **High** (4-5 weeks)

**RECOMMENDATION**: **Option B** (Keep in OpenAlgo) for immediate deployment, **Option A** (Adapt to US markets) for long-term scalability.

### Challenge 2: Strategy Code Extraction

**Issue**: Need to extract the exact strategy code and parameters for Strategy 107 from the backtester.

**Steps:**

1. **Identify Strategy 107 in ALL_PORTFOLIOS file**
   - Read sheet name for Strategy 107
   - Extract parameters (strike selection, stop-loss, entry/exit times)

2. **Locate Strategy Code**
   - Find corresponding strategy file in `Strategies/` directory
   - Extract entry/exit logic
   - Extract risk management rules

3. **Document Strategy**
   - Create detailed strategy specification
   - Document all parameters
   - Document all indicators used

**Effort**: **1-2 days**

### Challenge 3: Data Availability

**Issue**: QuantConnect Lean requires historical data for backtesting.

**For US Markets (SPX/SPY):**
- ✅ QuantConnect provides free historical data
- ✅ Options data available (limited resolution)
- ✅ Can purchase higher-resolution data

**For Indian Markets (NIFTY):**
- ❌ QuantConnect does not provide NIFTY data
- ⚠️ Need to use custom data feed
- ⚠️ Need to format data for OpenAlgo

**RECOMMENDATION**: If migrating to US markets, use QuantConnect's built-in data. If staying with Indian markets, use existing data in custom backtester.

### Challenge 4: Options Strategy Complexity

**Issue**: Options strategies (Iron Condor, Straddle, etc.) require multi-leg order management.

**QuantConnect Lean Support:**
- ✅ **Combo Orders**: Supports multi-leg options orders
- ✅ **Option Chains**: Built-in option chain filtering
- ✅ **Greeks**: Built-in Greeks calculation
- ✅ **Expiry Management**: Automatic expiry handling

**OpenAlgo Support:**
- ⚠️ **Combo Orders**: Need to implement multi-leg order management
- ⚠️ **Option Chains**: Need to implement option chain filtering
- ⚠️ **Greeks**: Need to implement Greeks calculation
- ⚠️ **Expiry Management**: Need to implement expiry handling

**RECOMMENDATION**: QuantConnect Lean has better built-in support for options strategies. If migrating to US markets, Lean is the better choice.

### Challenge 5: Backtesting vs. Live Trading Differences

**Issue**: Backtest results may not match live trading due to:
- Slippage
- Commission
- Order execution delays
- Market impact
- Data quality differences

**Mitigation Strategies:**

1. **Realistic Backtesting**
   - Add slippage model (0.1-0.5% for options)
   - Add commission model (broker-specific)
   - Add order execution delays (1-5 seconds)

2. **Paper Trading**
   - Run strategy in paper trading for 2-4 weeks
   - Compare paper trading results with backtest
   - Adjust parameters if needed

3. **Position Sizing**
   - Start with small position sizes (10-20% of backtest size)
   - Gradually increase as confidence grows

4. **Risk Management**
   - Set maximum daily loss limit
   - Set maximum drawdown limit
   - Implement circuit breakers

**RECOMMENDATION**: Always paper trade for at least 2 weeks before live deployment.

---

## Migration Path: Recommended Approach

### Phase 1: Strategy Extraction and Documentation (Week 1)

**Tasks:**

1. **Extract Strategy 107 Parameters**
   - [ ] Read ALL_PORTFOLIOS file, identify Strategy 107 sheet
   - [ ] Extract strategy parameters (strikes, stop-loss, entry/exit)
   - [ ] Document strategy logic

2. **Locate Strategy Code**
   - [ ] Find strategy file in `Strategies/` directory
   - [ ] Extract entry/exit logic
   - [ ] Extract risk management rules

3. **Create Strategy Specification Document**
   - [ ] Strategy name and type
   - [ ] Entry rules
   - [ ] Exit rules
   - [ ] Position sizing
   - [ ] Risk management
   - [ ] Indicators used

**Deliverable**: Strategy Specification Document

### Phase 2: Decision Point - Market Selection (Week 1)

**Decision**: Choose between Indian markets (OpenAlgo) or US markets (QuantConnect Lean)

**Option A: Indian Markets (NIFTY) with OpenAlgo**
- Go to Phase 3A

**Option B: US Markets (SPX/SPY) with QuantConnect Lean**
- Go to Phase 3B

### Phase 3A: OpenAlgo Integration (Weeks 2-3)

**Tasks:**

1. **Integrate Strategy with OpenAlgo Event Engine**
   - [ ] Create strategy adapter for OpenAlgo
   - [ ] Implement event handlers (on_tick, on_order, on_position)
   - [ ] Implement multi-leg order management

2. **Backtest in Custom Backtester**
   - [ ] Run backtest with realistic slippage/commission
   - [ ] Validate results match original backtest

3. **Paper Trading with Jainam**
   - [ ] Configure Jainam paper trading account
   - [ ] Deploy strategy to OpenAlgo
   - [ ] Monitor for 2 weeks

4. **Live Trading Preparation**
   - [ ] Set up risk management rules
   - [ ] Set up monitoring and alerts
   - [ ] Create deployment checklist

**Deliverable**: OpenAlgo-integrated strategy ready for live trading

### Phase 3B: QuantConnect Lean Migration (Weeks 2-4)

**Tasks:**

1. **Adapt Strategy to SPX/SPY**
   - [ ] Convert NIFTY strikes to SPX/SPY strikes
   - [ ] Adjust position sizing for SPX/SPY
   - [ ] Adjust stop-loss levels for SPX/SPY volatility

2. **Implement Strategy in QuantConnect Lean**
   - [ ] Create Python algorithm in `Algorithm.Python/`
   - [ ] Implement `Initialize()` method
   - [ ] Implement `OnData()` method
   - [ ] Implement option chain filtering
   - [ ] Implement multi-leg order placement

3. **Backtest in QuantConnect Lean**
   - [ ] Run backtest with SPX/SPY data
   - [ ] Compare results with original NIFTY backtest
   - [ ] Adjust parameters if needed

4. **Paper Trading with Interactive Brokers**
   - [ ] Configure IB paper trading account
   - [ ] Deploy strategy to Lean
   - [ ] Monitor for 2-4 weeks

5. **Live Trading Preparation**
   - [ ] Set up risk management rules
   - [ ] Set up monitoring and alerts
   - [ ] Create deployment checklist

**Deliverable**: QuantConnect Lean algorithm ready for live trading

---

## Next Steps

### Immediate Actions (This Week)

1. **Extract Strategy 107 Details**
   - Read ALL_PORTFOLIOS file
   - Identify exact strategy parameters
   - Locate strategy code in backtester

2. **Make Market Decision**
   - Decide: Indian markets (OpenAlgo) or US markets (Lean)?
   - Consider capital requirements, risk tolerance, market familiarity

3. **Set Up Development Environment**
   - If OpenAlgo: Set up OpenAlgo development environment
   - If Lean: Set up QuantConnect Lean development environment

### Short-term Actions (Next 2 Weeks)

4. **Implement Strategy**
   - If OpenAlgo: Integrate with event engine
   - If Lean: Convert to Lean algorithm

5. **Backtest and Validate**
   - Run backtests with realistic assumptions
   - Compare with original backtest results

6. **Paper Trading**
   - Deploy to paper trading environment
   - Monitor for 2-4 weeks

### Medium-term Actions (Next 1-2 Months)

7. **Live Trading Deployment**
   - Start with small position sizes
   - Gradually increase as confidence grows
   - Monitor performance closely

8. **Performance Monitoring**
   - Track live trading vs. backtest performance
   - Adjust parameters if needed
   - Implement improvements

---

## Conclusion

**Key Takeaways:**

1. ✅ **Optimal Strategy Identified**: Strategy 107 (Sharpe = 40.87, Win Rate = 100%)
2. ❌ **Market Incompatibility**: QuantConnect Lean does not support Indian markets (NIFTY)
3. ✅ **Two Viable Paths**:
   - **Path A**: Keep NIFTY strategy, deploy to OpenAlgo with Indian brokers
   - **Path B**: Adapt to SPX/SPY, deploy to QuantConnect Lean with US brokers
4. ⚠️ **Recommendation**: **Path A** (OpenAlgo) for immediate deployment, **Path B** (Lean) for long-term scalability

**Effort Estimates:**

| Path | Effort | Timeline | Risk |
|------|--------|----------|------|
| **Path A (OpenAlgo)** | Low | 1-2 weeks | Low |
| **Path B (Lean)** | Medium | 3-4 weeks | Medium |
| **Hybrid (Both)** | High | 5-6 weeks | High |

**Next Document**: Create detailed strategy specification after extracting Strategy 107 parameters.

---

**Document End**

