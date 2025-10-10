# Research Prompt B: New Parameter Research

**Generated**: 2025-10-08  
**Target Platforms**: ChatGPT Deep Research / Gemini Deep Research / Grok DeepSearch  
**Research Type**: Gap Analysis and New Parameter Identification  
**Estimated Research Time**: 90-120 minutes

---

## 🎯 Research Objective

Identify and research new parameters that should be added to the backtester system through comprehensive gap analysis and industry benchmarking. The goal is to create a prioritized list of missing parameters with complete implementation specifications that will bring the system to professional trading platform standards.

---

## 📋 Context and Background

### Project Overview

We are integrating a Python-based algorithmic trading backtester with MarvelQuant (a Flask-based multi-broker trading platform) to enable live trading execution. While the current `Util.py` module contains 100+ parameters, there are significant gaps when compared to:

1. **Column Mappings**: Parameters defined in Excel column mappings but not fully implemented in code
2. **Input Sheet Definitions**: Parameters present in historical input sheets but lacking backend logic
3. **Industry Standards**: Parameters that professional platforms (QuantConnect, TradeStation, Interactive Brokers) provide but our system lacks
4. **Live Trading Requirements**: Parameters needed specifically for real-time execution that weren't necessary for backtesting

### Current System Gaps

**Known Gap Categories**:

1. **Advanced Order Types**: Current system supports basic market orders; missing limit, stop-limit, OCO, bracket, iceberg, TWAP, VWAP orders
2. **Portfolio-Level Risk**: Limited portfolio-level risk management; missing correlation-based limits, sector exposure limits, concentration limits
3. **Market Regime Detection**: No parameters for detecting and adapting to market regimes (trending, ranging, high volatility, low volatility)
4. **Execution Quality**: No parameters for slippage modeling, market impact estimation, fill probability, execution algorithms
5. **Performance Tracking**: Limited performance metrics; missing Sharpe ratio targets, Sortino ratio, Calmar ratio, drawdown limits, recovery time tracking
6. **Dynamic Adjustments**: No parameters for dynamic strategy adjustments based on performance, market conditions, or time of day
7. **Multi-Timeframe Analysis**: Limited support for multi-timeframe strategies; missing parameters for timeframe synchronization
8. **Greeks Management**: For options strategies, missing delta, gamma, theta, vega targets and limits
9. **Liquidity Management**: No parameters for liquidity checks, bid-ask spread limits, volume requirements
10. **Commission and Fees**: Basic expense calculation; missing detailed commission structures, exchange fees, regulatory fees

### Integration Goals

1. **Comprehensive Coverage**: Fill all gaps between current implementation and industry standards
2. **Live Trading Readiness**: Add parameters essential for real-time execution safety
3. **Excel/JSON Compatibility**: All new parameters must map cleanly to dual-format configuration
4. **Backward Compatibility**: New parameters should be optional with sensible defaults
5. **Validation Framework**: Each new parameter must have complete validation rules

---

## 🔍 Specific Research Questions

**YOU MUST ANSWER THESE QUESTIONS:**

### 1. Gap Analysis: Column Mapping vs Implementation

**Research Questions**:
- What parameters are defined in `/Users/maruth/projects/backtester-worktree-1/backtester_v2/ui-centralized/configurations/data/archive/column_mapping` but NOT implemented in `Util.py`?
- Which Excel columns in historical input sheets have no corresponding backend logic?
- What parameters are partially implemented (defined but not fully functional)?
- Which parameters have inconsistent naming between Excel, column mapping, and code?
- What parameters are deprecated in input sheets but still referenced in code?

**Expected Output**: Complete gap analysis table with columns: Parameter Name, Defined In (Excel/Mapping/Code), Implementation Status (Not Implemented/Partial/Inconsistent), Priority

### 2. Advanced Order Types

**Current State**: System primarily supports market orders

**Research Questions**:
- What order types are industry-standard in professional trading platforms?
  - Limit orders (buy/sell at specific price or better)
  - Stop-limit orders (trigger at stop price, execute as limit order)
  - OCO (One-Cancels-Other) orders
  - Bracket orders (entry + stop-loss + take-profit as single order)
  - Iceberg orders (display only portion of total quantity)
  - TWAP (Time-Weighted Average Price) orders
  - VWAP (Volume-Weighted Average Price) orders
  - Trailing stop orders (already partially implemented - research enhancements)
- How do platforms like Interactive Brokers and TradeStation implement these order types?
- What parameters are needed for each order type? (price, quantity, time-in-force, display quantity, etc.)
- How should order types be validated before submission to broker?
- What order types are most critical for options trading strategies?

**Expected Output**: Complete specification for top 5 priority order types with all required parameters

### 3. Portfolio-Level Risk Management

**Current State**: Basic portfolio target and stop-loss; missing advanced risk controls

**Research Questions**:
- What portfolio-level risk parameters are industry-standard?
  - Maximum portfolio drawdown (absolute and percentage)
  - Maximum daily loss limit
  - Maximum position concentration (% of portfolio in single position)
  - Sector exposure limits (% of portfolio in single sector)
  - Correlation-based position limits (avoid highly correlated positions)
  - Leverage limits (maximum leverage ratio)
  - Margin utilization limits (% of available margin)
  - VaR (Value at Risk) limits
- How do professional platforms calculate and enforce these limits in real-time?
- What actions should be taken when limits are breached? (stop new entries, close positions, send alerts)
- How should risk limits differ for different account sizes and risk profiles?
- What validation ensures risk limits are not too restrictive or too loose?

**Expected Output**: Complete specification for top 10 portfolio-level risk parameters with calculation methods and enforcement logic

### 4. Market Regime Detection

**Current State**: No market regime detection; strategies run regardless of market conditions

**Research Questions**:
- What market regime detection methods are used in professional trading systems?
  - Volatility regime (VIX-based, ATR-based, historical volatility)
  - Trend regime (ADX, moving average slopes, trend strength indicators)
  - Volume regime (volume profile, volume trends)
  - Correlation regime (market correlation levels)
  - Sentiment regime (put/call ratio, advance/decline ratio)
- How should strategies adapt to different market regimes?
  - Trending market: momentum strategies, trend-following
  - Ranging market: mean reversion, range-bound strategies
  - High volatility: reduce position sizes, widen stops
  - Low volatility: increase position sizes, tighten stops
- What parameters are needed for regime detection? (lookback periods, thresholds, smoothing factors)
- How frequently should regime be re-evaluated? (real-time, daily, weekly)
- What validation ensures regime detection parameters are robust?

**Expected Output**: Complete specification for market regime detection system with 5-7 key parameters

### 5. Execution Quality Parameters

**Current State**: No slippage modeling or execution quality tracking

**Research Questions**:
- What execution quality parameters are industry-standard?
  - Slippage modeling (fixed points, percentage-based, volatility-based)
  - Market impact estimation (based on order size vs average volume)
  - Fill probability (likelihood of order being filled at desired price)
  - Execution delay (time between signal and order placement)
  - Partial fill handling (what to do if order is only partially filled)
  - Liquidity checks (minimum volume, bid-ask spread requirements)
- How do platforms like QuantConnect model slippage and market impact?
- What parameters are needed for realistic execution simulation in backtesting?
- How should execution parameters differ between backtesting and live trading?
- What validation ensures execution parameters are realistic?

**Expected Output**: Complete specification for execution quality system with 8-10 parameters

### 6. Performance Tracking and Targets

**Current State**: Basic P&L tracking; missing advanced performance metrics

**Research Questions**:
- What performance tracking parameters are industry-standard?
  - Sharpe ratio (risk-adjusted return)
  - Sortino ratio (downside risk-adjusted return)
  - Calmar ratio (return vs maximum drawdown)
  - Maximum drawdown (peak-to-trough decline)
  - Recovery time (time to recover from drawdown)
  - Win rate (percentage of winning trades)
  - Profit factor (gross profit / gross loss)
  - Expectancy (average win × win rate - average loss × loss rate)
  - R-multiple (profit/loss in terms of initial risk)
- How should strategies be automatically disabled if performance degrades?
  - Sharpe ratio falls below threshold
  - Drawdown exceeds limit
  - Win rate drops below acceptable level
- What parameters are needed for performance-based strategy adjustment?
- How frequently should performance metrics be calculated? (daily, weekly, monthly)
- What validation ensures performance targets are achievable?

**Expected Output**: Complete specification for performance tracking system with 10-12 parameters

### 7. Dynamic Strategy Adjustments

**Current State**: Static parameters; no dynamic adjustments based on performance or market conditions

**Research Questions**:
- What dynamic adjustment mechanisms are used in professional trading systems?
  - Position sizing based on recent performance (increase after wins, decrease after losses)
  - Stop-loss adjustment based on volatility (wider stops in high volatility)
  - Entry threshold adjustment based on win rate (stricter entry criteria if win rate is low)
  - Time-of-day adjustments (different parameters for open, mid-day, close)
  - Day-of-week adjustments (different parameters for Monday vs Friday)
- How do platforms implement parameter adaptation algorithms?
- What parameters control the rate and magnitude of dynamic adjustments?
- How to prevent over-adjustment that leads to instability?
- What validation ensures dynamic adjustments are safe for live trading?

**Expected Output**: Complete specification for dynamic adjustment system with 6-8 parameters

### 8. Multi-Timeframe Analysis

**Current State**: Single timeframe per strategy; limited multi-timeframe support

**Research Questions**:
- What multi-timeframe parameters are industry-standard?
  - Primary timeframe (main trading timeframe)
  - Confirmation timeframes (higher timeframes for trend confirmation)
  - Filter timeframes (lower timeframes for entry timing)
  - Timeframe synchronization (how to align signals across timeframes)
- How do platforms implement multi-timeframe strategies?
- What parameters are needed for timeframe coordination?
- How should multi-timeframe strategies handle conflicting signals?
- What validation ensures timeframe parameters are compatible?

**Expected Output**: Complete specification for multi-timeframe system with 5-7 parameters

### 9. Options Greeks Management

**Current State**: Basic options support; no Greeks-based risk management

**Research Questions**:
- What Greeks-based parameters are industry-standard for options trading?
  - Delta targets and limits (directional exposure)
  - Gamma limits (rate of delta change)
  - Theta targets (time decay expectations)
  - Vega limits (volatility exposure)
  - Portfolio Greeks (aggregate Greeks across all positions)
- How do professional options platforms manage Greeks in real-time?
- What parameters are needed for delta-neutral strategies?
- How should Greeks limits trigger position adjustments?
- What validation ensures Greeks parameters are appropriate for strategy type?

**Expected Output**: Complete specification for Greeks management system with 8-10 parameters

### 10. Liquidity and Execution Constraints

**Current State**: No liquidity checks; assumes all orders can be filled

**Research Questions**:
- What liquidity parameters are industry-standard?
  - Minimum average daily volume (ADV) requirements
  - Maximum order size as % of ADV
  - Bid-ask spread limits (maximum acceptable spread)
  - Minimum open interest (for options)
  - Market depth requirements (volume at best bid/ask)
- How do platforms check liquidity before order placement?
- What parameters are needed for liquidity-based position sizing?
- How should strategies adapt when liquidity is insufficient?
- What validation ensures liquidity parameters prevent illiquid trades?

**Expected Output**: Complete specification for liquidity management system with 6-8 parameters

### 11. Commission and Fee Structures

**Current State**: Basic expense calculation; missing detailed fee modeling

**Research Questions**:
- What commission and fee parameters are industry-standard?
  - Per-trade commission (fixed or percentage-based)
  - Per-contract commission (for options/futures)
  - Exchange fees (NSE, BSE, MCX fees)
  - Regulatory fees (STT, GST, stamp duty)
  - Clearing fees
  - Broker-specific fees
  - Volume-based commission tiers
- How do platforms model different broker commission structures?
- What parameters are needed for accurate cost calculation?
- How should commission affect position sizing and strategy selection?
- What validation ensures commission parameters match broker fee schedules?

**Expected Output**: Complete specification for commission system with 10-12 parameters

### 12. Time-Based Strategy Controls

**Current State**: Basic start/end time; missing advanced time controls

**Research Questions**:
- What time-based parameters are industry-standard?
  - Trading windows (specific time ranges when strategy is active)
  - Blackout periods (times when trading is prohibited)
  - Time-of-day position sizing (different sizes for different times)
  - Intraday square-off times (automatic position closing times)
  - Weekend/holiday handling
  - Time zone management for global markets
- How do platforms implement complex time-based rules?
- What parameters are needed for time-based risk management?
- How should time-based parameters interact with market conditions?
- What validation ensures time-based parameters are logically consistent?

**Expected Output**: Complete specification for time-based control system with 8-10 parameters

### 13. News and Event Handling

**Current State**: No news/event awareness; strategies run regardless of scheduled events

**Research Questions**:
- What news and event parameters are used in professional trading systems?
  - Economic calendar integration (avoid trading during major announcements)
  - Earnings announcement handling (close positions before earnings)
  - Volatility event detection (unusual price movements)
  - News sentiment parameters (positive/negative news impact)
- How do platforms integrate news and event data into trading logic?
- What parameters control strategy behavior around scheduled events?
- How should strategies adapt to unexpected news events?
- What validation ensures event parameters are up-to-date?

**Expected Output**: Complete specification for news/event handling system with 5-7 parameters

### 14. Correlation and Diversification

**Current State**: No correlation tracking; can open highly correlated positions

**Research Questions**:
- What correlation parameters are industry-standard?
  - Maximum correlation between positions (avoid redundant exposure)
  - Sector diversification requirements (minimum number of sectors)
  - Strategy diversification (maximum allocation to single strategy)
  - Instrument diversification (spread across multiple instruments)
- How do platforms calculate and monitor correlation in real-time?
- What parameters are needed for correlation-based position limits?
- How should correlation limits affect new position entry?
- What validation ensures correlation parameters promote diversification?

**Expected Output**: Complete specification for correlation management system with 6-8 parameters

### 15. Rollover and Expiry Management

**Current State**: Basic expiry handling; missing advanced rollover logic

**Research Questions**:
- What rollover parameters are industry-standard?
  - Rollover timing (days before expiry, specific time of day)
  - Rollover method (close and reopen, spread order, calendar spread)
  - Rollover strike selection (same strike, ATM, maintain delta)
  - Rollover cost limits (maximum acceptable rollover cost)
  - Rollover volume requirements (minimum liquidity in new expiry)
- How do professional platforms automate expiry rollovers?
- What parameters are needed for different rollover strategies?
- How should rollover logic differ for different instruments?
- What validation ensures rollover parameters prevent costly mistakes?

**Expected Output**: Complete specification for rollover management system with 7-9 parameters

---

## 📊 Required Analysis Areas

### Area 1: Gap Analysis - Column Mapping vs Code

**Analyze**:
- All parameters in `/Users/maruth/projects/backtester-worktree-1/backtester_v2/ui-centralized/configurations/data/archive/column_mapping`
- All parameters in historical input sheets (`/Users/maruth/projects/backtester-worktree-1/backtester-golden/INPUT SHEETS/input_old/`)
- All parameters in `Util.py` BT_FIELDS
- Cross-reference to identify: defined but not implemented, partially implemented, inconsistently named

**Deliverable**: Gap analysis table with implementation status for every parameter

### Area 2: Industry Benchmark Analysis

**Analyze**:
- QuantConnect LEAN engine parameter system
- Interactive Brokers TWS API order types and parameters
- TradeStation strategy parameters
- Alpaca Trading API parameters
- TradingView Pine Script parameters
- Identify parameters present in 3+ platforms but missing from our system

**Deliverable**: Industry benchmark comparison table

### Area 3: Live Trading Requirements

**Analyze**:
- Parameters needed specifically for real-time execution (not needed in backtesting)
- Safety parameters to prevent costly errors in live trading
- Monitoring and alerting parameters
- Circuit breaker parameters (automatic strategy shutdown)
- Audit trail parameters (logging and compliance)

**Deliverable**: Live trading requirements specification

### Area 4: Options-Specific Parameters

**Analyze**:
- Greeks management parameters (delta, gamma, theta, vega)
- Implied volatility parameters
- Options-specific order types (vertical spreads, iron condors, butterflies)
- Expiry and rollover parameters
- Strike selection enhancements

**Deliverable**: Options parameter specification

### Area 5: Risk Management Enhancements

**Analyze**:
- Portfolio-level risk parameters
- Position-level risk parameters
- Correlation-based risk parameters
- Drawdown management parameters
- Leverage and margin parameters

**Deliverable**: Comprehensive risk management parameter specification

### Area 6: Performance and Optimization

**Analyze**:
- Performance metric parameters (Sharpe, Sortino, Calmar, etc.)
- Optimization parameters (parameter ranges, optimization methods)
- Walk-forward analysis parameters
- Out-of-sample testing parameters
- Overfitting prevention parameters

**Deliverable**: Performance tracking and optimization parameter specification

### Area 7: Execution and Slippage

**Analyze**:
- Slippage modeling parameters
- Market impact parameters
- Fill probability parameters
- Execution algorithm parameters (TWAP, VWAP, etc.)
- Liquidity check parameters

**Deliverable**: Execution quality parameter specification

### Area 8: Market Regime and Adaptation

**Analyze**:
- Market regime detection parameters
- Dynamic parameter adjustment parameters
- Adaptive position sizing parameters
- Regime-based strategy selection parameters

**Deliverable**: Market regime and adaptation parameter specification

### Area 9: Multi-Strategy and Portfolio

**Analyze**:
- Multi-strategy coordination parameters
- Portfolio rebalancing parameters
- Strategy allocation parameters
- Inter-strategy dependencies

**Deliverable**: Multi-strategy portfolio parameter specification

### Area 10: Compliance and Audit

**Analyze**:
- Audit trail parameters
- Compliance check parameters
- Regulatory reporting parameters
- Risk disclosure parameters

**Deliverable**: Compliance and audit parameter specification

---

## 📄 Expected Deliverables

### 1. Gap Analysis Report (3-5 pages)

**Content**:
- Complete list of parameters defined in column_mapping but NOT in Util.py
- Complete list of parameters in input sheets but NOT in Util.py
- Parameters partially implemented (defined but not functional)
- Parameters with inconsistent naming across Excel/mapping/code
- Deprecated parameters still referenced in code
- Summary statistics (total gaps, by category, by priority)

**Format**: Tables with columns: Parameter Name, Defined In, Implementation Status, Gap Type, Priority, Notes

### 2. Industry Standard Parameters (8-10 pages)

**Content**:
- Comprehensive list of parameters present in 3+ professional platforms but missing from our system
- For each parameter:
  - Parameter name and description
  - Which platforms implement it (QuantConnect, IB, TradeStation, etc.)
  - Use cases and benefits
  - Implementation complexity estimate
  - Priority ranking
- Organized by category: Order Types, Risk Management, Execution, Performance, etc.

**Format**: Detailed tables with examples from each platform

### 3. Prioritization Matrix (2-3 pages)

**Content**:
- All identified new parameters ranked by:
  - Impact (High/Medium/Low) - how much value it adds
  - Effort (High/Medium/Low) - implementation complexity
  - Live Trading Criticality (Critical/Important/Nice-to-Have)
  - User Demand (based on input sheet analysis)
- Priority quadrants:
  - P0 (Critical): High impact, low effort, critical for live trading
  - P1 (High): High impact, medium effort, or medium impact, low effort
  - P2 (Medium): Medium impact, medium effort
  - P3 (Low): Low impact or high effort

**Format**: Priority matrix diagram + ranked table

### 4. Implementation Specifications for Top 10 Parameters (10-15 pages)

**Content**:
For EACH of the top 10 priority parameters:
- **Parameter Name**: Internal code name
- **Display Name**: User-friendly name for UI
- **Category**: Order Type / Risk Management / Execution / etc.
- **Description**: What the parameter does and why it's needed
- **Data Type**: int, float, string, boolean, enum, list, dict
- **Default Value**: Sensible default for most use cases
- **Valid Range/Values**: Constraints and allowed values
- **Dependencies**: Which other parameters it depends on or conflicts with
- **Validation Rules**: How to validate the parameter value
- **Excel Mapping**: Which Excel column(s) map to this parameter
- **JSON Schema**: JSON schema definition
- **Implementation Notes**: Technical details for developers
- **Code Example**: Python code showing how to implement
- **Test Cases**: Unit test examples
- **Live Trading Considerations**: Special handling for real-time execution

**Format**: Detailed specification document with code examples

### 5. Quick Reference Guide (2-3 pages)

**Content**:
- Summary table of all new parameters (50-100 parameters)
- Columns: Parameter Name, Category, Priority, Data Type, Default, Live Trading Critical (Y/N)
- Organized by category for easy reference
- Color-coded by priority (P0/P1/P2/P3)

**Format**: Comprehensive table optimized for quick lookup

---

## ✅ Success Criteria

**The research is successful if it provides:**

1. ✅ **Complete Gap Analysis**: Every parameter in column_mapping and input sheets is cross-referenced with Util.py
2. ✅ **Industry Benchmarked**: At least 20 new parameters identified from professional platforms
3. ✅ **Prioritized**: Clear priority ranking (P0/P1/P2/P3) with justification for each parameter
4. ✅ **Implementation Ready**: Top 10 parameters have complete specifications with code examples
5. ✅ **Live Trading Focused**: Critical live trading parameters are identified and prioritized
6. ✅ **Categorized**: Parameters organized by logical categories (Order Types, Risk, Execution, etc.)
7. ✅ **Validated**: Each parameter has validation rules and constraints defined
8. ✅ **Excel/JSON Compatible**: All parameters have clear Excel column and JSON schema mappings
9. ✅ **Backward Compatible**: New parameters are optional with sensible defaults
10. ✅ **Actionable**: Development team can immediately start implementing from the specifications

---

## 🔗 Preferred Sources and References

### Trading Platform Documentation

1. **QuantConnect LEAN Engine**: https://github.com/QuantConnect/Lean
   - Order types: https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types
   - Risk management: https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/risk-management

2. **Interactive Brokers API**: https://interactivebrokers.github.io/tws-api/
   - Order types: https://interactivebrokers.github.io/tws-api/order_types.html
   - Risk management: https://www.interactivebrokers.com/en/trading/risk-management.php

3. **TradeStation**: https://www.tradestation.com/
   - Strategy parameters: https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/
   - Order types: https://help.tradestation.com/10_00/eng/tradestationhelp/orders/

4. **Alpaca Trading API**: https://alpaca.markets/docs/
   - Order types: https://alpaca.markets/docs/trading/orders/
   - Risk management: https://alpaca.markets/docs/trading/risk-management/

5. **TradingView Pine Script**: https://www.tradingview.com/pine-script-docs/
   - Strategy parameters: https://www.tradingview.com/pine-script-docs/en/v5/concepts/Strategies.html

### Risk Management Resources

6. **CBOE (Chicago Board Options Exchange)**: https://www.cboe.com/
   - Options Greeks: https://www.cboe.com/education/tools/greeks/
   - Risk management: https://www.cboe.com/education/risk-management/

7. **Options Industry Council**: https://www.optionseducation.org/
   - Options strategies and parameters
   - Risk management best practices

8. **CFA Institute**: https://www.cfainstitute.org/
   - Portfolio risk management
   - Performance measurement standards

### Academic and Industry Research

9. **"Algorithmic Trading and DMA" by Barry Johnson**
   - Execution algorithms (TWAP, VWAP, etc.)
   - Market impact modeling
   - Slippage estimation

10. **"Quantitative Risk Management" by McNeil, Frey, Embrechts**
    - VaR (Value at Risk) calculations
    - Portfolio risk metrics
    - Correlation and diversification

### Technical Standards

11. **FIX Protocol**: https://www.fixtrading.org/
    - Standard order types and parameters
    - Execution report fields

12. **JSON Schema**: https://json-schema.org/
    - Parameter validation schemas
    - Data type definitions

13. **Python Validation Libraries**:
    - pydantic: https://docs.pydantic.dev/
    - marshmallow: https://marshmallow.readthedocs.io/

### Regulatory and Compliance

14. **SEBI (India)**: https://www.sebi.gov.in/
    - Algorithmic trading regulations
    - Risk management requirements

15. **SEC (US)**: https://www.sec.gov/
    - Trading regulations (for reference)
    - Risk disclosure requirements

---

## 🎯 Technology Stack Constraints

**ALL RECOMMENDATIONS MUST WORK WITHIN THIS STACK:**

- **Backend**: Python 3.8+, Flask 2.x with Blueprints
- **Data Processing**: pandas, numpy
- **File Handling**: openpyxl (Excel), JSON (configuration)
- **Validation**: JSON Schema, pydantic, custom Python validation
- **Integration**: MarvelQuant API for live trading (multi-broker support)
- **Database**: SQLite 3.x
- **Real-time**: Server-Sent Events (SSE) for live updates

**DO NOT SUGGEST**: Technologies outside this stack (e.g., PostgreSQL, Redis, React, Vue, WebSockets if SSE is sufficient)

---

## 🤖 Platform-Specific Optimization Tips

### For ChatGPT Deep Research

**Optimization Tips**:
1. **Emphasize gap analysis**: "Analyze the column_mapping file and identify all parameters not implemented in Util.py"
2. **Request platform comparison**: "Compare parameter systems across QuantConnect, Interactive Brokers, and TradeStation"
3. **Specify output format**: "Provide implementation specifications in table format with all required fields"
4. **Request code examples**: "Include Python 3.8+ code examples for top 10 priority parameters"

**Query Optimization**:
- Use keywords: "gap analysis," "missing parameters," "industry benchmark," "implementation specification"
- Request citations: "Include URLs to platform documentation for each parameter"
- Ask for prioritization: "Rank parameters by impact and effort using a priority matrix"

**Expected Results**:
- 25-35 pages of comprehensive research
- Complete gap analysis with all missing parameters identified
- Detailed specifications for top 10 parameters
- Priority matrix with clear rankings

### For Gemini Deep Research

**Optimization Tips**:
1. **Review the research plan**: Gemini will generate a multi-point plan - ensure it covers gap analysis, industry benchmarking, and prioritization
2. **Refine before execution**: If the plan misses any categories (order types, risk management, etc.), add them
3. **Use follow-ups**: After initial research, ask "Provide detailed specifications for the top 10 priority parameters"
4. **Request comparisons**: "Create comparison tables showing which platforms implement each parameter"

**Best Practices**:
- Start with clear scope: "Identify new parameters missing from backtester system"
- Let Gemini generate the plan, then refine it
- Use follow-up questions to drill deeper into specific parameter categories
- Request structured output (tables, matrices, specifications)

**Expected Results**:
- Structured research with clear sections
- Good coverage of industry standards
- May need follow-ups for complete implementation specifications

### For Grok DeepSearch

**Optimization Tips**:
1. **Specify date range**: "Focus on 2024-2025 best practices for trading system parameters"
2. **Request specific output**: "Provide gap analysis table and priority matrix with rankings"
3. **Use Think Mode**: Pair with Think Mode for reasoning about parameter prioritization
4. **Follow-up strategy**: Use follow-ups to expand specifications for high-priority parameters

**Best Practices**:
- Emphasize industry benchmarking: "What parameters do QuantConnect, IB, and TradeStation have that we're missing?"
- Request specific examples: "Show examples of order type parameters from professional platforms"
- Ask for recent developments: "What new parameters have been added to trading platforms in 2024-2025?"
- Verify technical claims against official documentation

**Query Limits**: Free (5/24hrs), Premium (30/2hrs)

**Expected Results**:
- Fast, focused research on missing parameters
- Recent examples and industry trends
- May need verification of technical details against official docs

---

## 📋 Validation Checklist

After research completion, verify:

- [ ] Gap analysis covers ALL parameters in column_mapping and input sheets
- [ ] At least 20 new parameters identified from industry benchmarking
- [ ] All parameters categorized (Order Types, Risk, Execution, Performance, etc.)
- [ ] Priority ranking (P0/P1/P2/P3) is justified with impact and effort estimates
- [ ] Top 10 parameters have complete implementation specifications
- [ ] Each specification includes: name, type, default, range, dependencies, validation, Excel mapping, JSON schema
- [ ] Code examples are Python 3.8+ compatible
- [ ] All parameters have validation rules defined
- [ ] Live trading critical parameters are clearly identified
- [ ] Backward compatibility is addressed (new parameters are optional)
- [ ] Excel/JSON compatibility is maintained
- [ ] Industry sources are cited (QuantConnect, IB, TradeStation, etc.)
- [ ] Implementation complexity estimates are realistic
- [ ] Quick reference guide summarizes all new parameters

---

## 🎯 Detailed Parameter Categories to Research

### Category 1: Advanced Order Types (Priority: P0)

**Missing Order Types to Research**:

1. **Limit Orders**
   - Parameters: LimitPrice, TimeInForce (DAY, GTC, IOC, FOK), DisplayQuantity
   - Use case: Enter at specific price or better
   - Platforms: All major platforms support this

2. **Stop-Limit Orders**
   - Parameters: StopPrice, LimitPrice, TimeInForce
   - Use case: Trigger at stop price, execute as limit order
   - Platforms: IB, TradeStation, Alpaca

3. **OCO (One-Cancels-Other) Orders**
   - Parameters: PrimaryOrderID, SecondaryOrderID, OCOGroup
   - Use case: Submit two orders, if one fills, cancel the other
   - Platforms: IB, TradeStation

4. **Bracket Orders**
   - Parameters: EntryPrice, StopLossPrice, TakeProfitPrice, BracketType
   - Use case: Entry + SL + TP as single atomic order
   - Platforms: IB, TradeStation, Alpaca

5. **Iceberg Orders**
   - Parameters: TotalQuantity, DisplayQuantity, RefreshQuantity
   - Use case: Hide total order size, display only portion
   - Platforms: IB, professional platforms

6. **TWAP (Time-Weighted Average Price) Orders**
   - Parameters: StartTime, EndTime, TotalQuantity, TimeSlices
   - Use case: Execute large order over time to minimize market impact
   - Platforms: IB, institutional platforms

7. **VWAP (Volume-Weighted Average Price) Orders**
   - Parameters: StartTime, EndTime, TotalQuantity, VolumeParticipationRate
   - Use case: Execute in line with market volume
   - Platforms: IB, institutional platforms

**Research Focus**: For each order type, identify all required parameters, validation rules, and implementation complexity

### Category 2: Portfolio-Level Risk Management (Priority: P0)

**Missing Risk Parameters to Research**:

1. **Drawdown Management**
   - MaxDrawdownPercent: Maximum allowed drawdown from peak equity
   - MaxDailyLossPercent: Maximum loss allowed in single day
   - DrawdownRecoveryMode: How to behave during drawdown (reduce size, stop trading, etc.)
   - DrawdownCalculationMethod: Peak-to-trough, rolling window, etc.

2. **Position Concentration Limits**
   - MaxPositionConcentrationPercent: Max % of portfolio in single position
   - MaxSectorConcentrationPercent: Max % of portfolio in single sector
   - MaxStrategyConcentrationPercent: Max % of portfolio in single strategy
   - MaxInstrumentConcentrationPercent: Max % of portfolio in single instrument type

3. **Correlation-Based Limits**
   - MaxPositionCorrelation: Maximum correlation between any two positions
   - CorrelationLookbackPeriod: Period for calculating correlation
   - CorrelationThreshold: Threshold above which positions are considered correlated
   - CorrelationAction: What to do when correlation limit is breached

4. **Leverage and Margin**
   - MaxLeverageRatio: Maximum leverage allowed (e.g., 2:1, 3:1)
   - MaxMarginUtilizationPercent: Max % of available margin to use
   - MarginCallAction: What to do when margin call is imminent
   - LeverageCalculationMethod: How to calculate current leverage

5. **Value at Risk (VaR)**
   - VaRConfidenceLevel: Confidence level for VaR calculation (95%, 99%)
   - VaRTimeHorizon: Time horizon for VaR (1 day, 1 week)
   - VaRCalculationMethod: Historical, parametric, Monte Carlo
   - MaxVaRLimit: Maximum allowed VaR

**Research Focus**: For each risk parameter, identify calculation methods, enforcement mechanisms, and industry standards

### Category 3: Market Regime Detection (Priority: P1)

**Missing Regime Parameters to Research**:

1. **Volatility Regime**
   - VolatilityRegimeIndicator: VIX, ATR, Historical Volatility
   - VolatilityRegimeThresholds: Low (<15), Medium (15-25), High (>25)
   - VolatilityRegimeLookback: Period for calculating volatility
   - VolatilityRegimeAction: How to adjust strategy based on regime

2. **Trend Regime**
   - TrendRegimeIndicator: ADX, Moving Average Slope, Trend Strength
   - TrendRegimeThresholds: Ranging (<20), Weak Trend (20-30), Strong Trend (>30)
   - TrendRegimeLookback: Period for calculating trend
   - TrendRegimeAction: Which strategies to enable/disable based on trend

3. **Volume Regime**
   - VolumeRegimeIndicator: Volume vs Average, Volume Profile
   - VolumeRegimeThresholds: Low (<0.8x avg), Normal (0.8-1.2x), High (>1.2x)
   - VolumeRegimeLookback: Period for calculating average volume
   - VolumeRegimeAction: How to adjust position sizing based on volume

4. **Correlation Regime**
   - CorrelationRegimeIndicator: Market correlation level
   - CorrelationRegimeThresholds: Low (<0.5), Medium (0.5-0.7), High (>0.7)
   - CorrelationRegimeLookback: Period for calculating correlation
   - CorrelationRegimeAction: Diversification adjustments based on correlation

**Research Focus**: For each regime type, identify detection methods, thresholds, and strategy adaptation rules

### Category 4: Execution Quality (Priority: P1)

**Missing Execution Parameters to Research**:

1. **Slippage Modeling**
   - SlippageType: Fixed, Percentage, Volatility-Based, Volume-Based
   - SlippageValue: Amount of slippage (points, percentage, ATR multiplier)
   - SlippageCalculationMethod: How to calculate expected slippage
   - SlippageLimit: Maximum acceptable slippage before rejecting order

2. **Market Impact**
   - MarketImpactModel: Linear, Square-Root, Logarithmic
   - MarketImpactFactor: Coefficient for market impact calculation
   - OrderSizeVsVolume: Order size as % of average daily volume
   - MarketImpactLimit: Maximum acceptable market impact

3. **Fill Probability**
   - FillProbabilityModel: Based on order book depth, historical fill rates
   - MinFillProbability: Minimum probability required to submit order
   - FillProbabilityLookback: Period for calculating historical fill rates
   - PartialFillHandling: Accept, Reject, or Retry partial fills

4. **Execution Delay**
   - SignalToOrderDelay: Expected delay between signal and order placement
   - OrderToFillDelay: Expected delay between order placement and fill
   - DelayVariability: Variability in execution delays
   - DelayImpactOnStrategy: How delays affect strategy performance

5. **Liquidity Checks**
   - MinAverageDailyVolume: Minimum ADV required to trade
   - MaxOrderSizePercent: Max order size as % of ADV
   - MaxBidAskSpreadPercent: Maximum acceptable bid-ask spread
   - MinOpenInterest: Minimum open interest for options
   - LiquidityCheckFrequency: How often to check liquidity

**Research Focus**: For each execution parameter, identify modeling methods, validation rules, and impact on backtesting accuracy

### Category 5: Performance Tracking (Priority: P1)

**Missing Performance Parameters to Research**:

1. **Risk-Adjusted Returns**
   - SharpeRatioTarget: Target Sharpe ratio
   - SharpeRatioMinimum: Minimum acceptable Sharpe ratio
   - SortinoRatioTarget: Target Sortino ratio (downside risk-adjusted)
   - CalmarRatioTarget: Target Calmar ratio (return vs max drawdown)

2. **Drawdown Metrics**
   - MaxDrawdownLimit: Maximum allowed drawdown
   - MaxDrawdownDuration: Maximum time allowed in drawdown
   - DrawdownRecoveryTarget: Target time to recover from drawdown
   - ConsecutiveLossLimit: Maximum consecutive losing trades

3. **Win/Loss Metrics**
   - MinWinRatePercent: Minimum acceptable win rate
   - MinProfitFactor: Minimum profit factor (gross profit / gross loss)
   - MinExpectancy: Minimum expectancy per trade
   - MinRMultiple: Minimum R-multiple (profit in terms of initial risk)

4. **Performance-Based Actions**
   - DisableStrategyIfSharpeBelow: Disable if Sharpe falls below threshold
   - ReduceSizeIfDrawdownExceeds: Reduce position size if drawdown exceeds limit
   - StopTradingIfWinRateBelow: Stop trading if win rate falls below threshold
   - AlertIfProfitFactorBelow: Send alert if profit factor falls below threshold

**Research Focus**: For each performance metric, identify calculation methods, thresholds, and automated actions

### Category 6: Dynamic Adjustments (Priority: P2)

**Missing Dynamic Parameters to Research**:

1. **Performance-Based Sizing**
   - SizeAdjustmentMethod: Fixed, Percentage, Kelly Criterion
   - IncreaseAfterWin: How much to increase size after winning trade
   - DecreaseAfterLoss: How much to decrease size after losing trade
   - MaxSizeAdjustmentPercent: Maximum allowed size adjustment
   - SizeAdjustmentLookback: Number of trades to consider for adjustment

2. **Volatility-Based Adjustments**
   - StopLossAdjustmentMethod: Fixed, ATR-based, Volatility-based
   - StopLossVolatilityMultiplier: Multiplier for volatility-based stops
   - PositionSizeVolatilityAdjustment: Reduce size in high volatility
   - EntryThresholdVolatilityAdjustment: Stricter entry in high volatility

3. **Time-Based Adjustments**
   - TimeOfDayPositionSizing: Different sizes for open, mid-day, close
   - DayOfWeekAdjustments: Different parameters for Monday vs Friday
   - MonthOfYearAdjustments: Seasonal adjustments
   - HolidayAdjustments: Behavior around holidays

4. **Win Rate-Based Adjustments**
   - EntryThresholdIfWinRateLow: Stricter entry criteria if win rate is low
   - StopLossIfWinRateLow: Tighter stops if win rate is low
   - PositionSizeIfWinRateHigh: Larger positions if win rate is high

**Research Focus**: For each dynamic adjustment type, identify adjustment algorithms, limits, and safety mechanisms

### Category 7: Multi-Timeframe Analysis (Priority: P2)

**Missing Multi-Timeframe Parameters to Research**:

1. **Timeframe Hierarchy**
   - PrimaryTimeframe: Main trading timeframe (e.g., 5-minute)
   - ConfirmationTimeframe: Higher timeframe for trend confirmation (e.g., 1-hour)
   - FilterTimeframe: Lower timeframe for entry timing (e.g., 1-minute)
   - TimeframeSynchronization: How to align signals across timeframes

2. **Multi-Timeframe Logic**
   - RequireConfirmationFromHigherTF: Require higher timeframe confirmation
   - FilterWithLowerTF: Use lower timeframe for entry timing
   - ConflictingSignalHandling: What to do when timeframes disagree
   - TimeframeWeighting: Weight given to each timeframe

**Research Focus**: For each multi-timeframe parameter, identify synchronization methods and conflict resolution strategies

### Category 8: Options Greeks Management (Priority: P1 for options strategies)

**Missing Greeks Parameters to Research**:

1. **Delta Management**
   - TargetDelta: Target delta for portfolio
   - MaxDelta: Maximum allowed delta
   - DeltaNeutralTolerance: Tolerance for delta-neutral strategies
   - DeltaRebalanceThreshold: When to rebalance delta

2. **Gamma Management**
   - MaxGamma: Maximum allowed gamma
   - GammaScalpingEnabled: Enable gamma scalping
   - GammaRebalanceFrequency: How often to rebalance gamma

3. **Theta Management**
   - TargetTheta: Target theta (time decay)
   - MinTheta: Minimum acceptable theta
   - ThetaDecayStrategy: How to manage theta decay

4. **Vega Management**
   - MaxVega: Maximum volatility exposure
   - VegaNeutralTolerance: Tolerance for vega-neutral strategies
   - VegaHedgingStrategy: How to hedge vega exposure

**Research Focus**: For each Greek, identify calculation methods, target ranges, and hedging strategies

### Category 9: Liquidity Management (Priority: P0 for live trading)

**Missing Liquidity Parameters to Research**:

1. **Volume Requirements**
   - MinAverageDailyVolume: Minimum ADV to trade
   - MaxOrderSizeVsADV: Max order size as % of ADV
   - VolumeCheckLookback: Period for calculating ADV

2. **Spread Requirements**
   - MaxBidAskSpreadPercent: Maximum acceptable spread
   - MaxBidAskSpreadAbsolute: Maximum spread in absolute terms
   - SpreadCheckFrequency: How often to check spread

3. **Open Interest Requirements (Options)**
   - MinOpenInterest: Minimum OI to trade
   - MaxPositionVsOpenInterest: Max position as % of OI
   - OpenInterestCheckFrequency: How often to check OI

4. **Market Depth**
   - MinBidVolume: Minimum volume at best bid
   - MinAskVolume: Minimum volume at best ask
   - DepthLevels: How many price levels to check

**Research Focus**: For each liquidity parameter, identify thresholds, check frequencies, and actions when liquidity is insufficient

### Category 10: Commission and Fees (Priority: P1)

**Missing Commission Parameters to Research**:

1. **Broker Commissions**
   - PerTradeCommission: Fixed commission per trade
   - PerContractCommission: Commission per contract (options/futures)
   - PercentageCommission: Commission as % of trade value
   - VolumeTiers: Commission tiers based on monthly volume

2. **Exchange Fees**
   - NSETransactionFee: NSE transaction charges
   - BSETransactionFee: BSE transaction charges
   - MCXTransactionFee: MCX transaction charges
   - ClearingFee: Clearing corporation fees

3. **Regulatory Fees**
   - STT: Securities Transaction Tax
   - GST: Goods and Services Tax
   - StampDuty: Stamp duty charges
   - SEBITurnoverFee: SEBI turnover fee

4. **Other Costs**
   - DataFeed: Market data subscription costs
   - PlatformFee: Trading platform fees
   - AccountMaintenanceFee: Annual account maintenance

**Research Focus**: For each fee type, identify calculation methods, broker-specific variations, and impact on strategy profitability

---

## 💡 Implementation Priority Framework

### P0 (Critical - Implement First)

**Criteria**: High impact + Low-Medium effort + Critical for live trading

**Estimated Parameters**: 10-15 parameters

**Examples**:
- Limit orders (essential for live trading)
- Liquidity checks (prevent illiquid trades)
- Portfolio drawdown limits (risk management)
- Commission modeling (accurate P&L)
- Order size vs volume limits (prevent market impact)

**Timeline**: Implement in Phase 1 (Weeks 1-2)

### P1 (High Priority - Implement Second)

**Criteria**: High impact + Medium effort OR Medium impact + Low effort

**Estimated Parameters**: 15-20 parameters

**Examples**:
- Stop-limit orders
- Bracket orders
- Greeks management (for options)
- Slippage modeling
- Performance tracking (Sharpe, Sortino)
- Market regime detection

**Timeline**: Implement in Phase 2 (Weeks 3-4)

### P2 (Medium Priority - Implement Third)

**Criteria**: Medium impact + Medium effort

**Estimated Parameters**: 15-20 parameters

**Examples**:
- OCO orders
- TWAP/VWAP orders
- Dynamic adjustments
- Multi-timeframe analysis
- Correlation management

**Timeline**: Implement in Phase 3 (Weeks 5-6)

### P3 (Low Priority - Future Enhancement)

**Criteria**: Low impact OR High effort

**Estimated Parameters**: 10-15 parameters

**Examples**:
- Iceberg orders
- Advanced execution algorithms
- News/event integration
- Complex multi-strategy coordination

**Timeline**: Implement in Phase 4+ (Weeks 7+)

---

## 📊 Expected Research Output Summary

**Total Pages**: 25-35 pages

**Breakdown**:
1. Gap Analysis Report: 3-5 pages
2. Industry Standard Parameters: 8-10 pages
3. Prioritization Matrix: 2-3 pages
4. Implementation Specifications (Top 10): 10-15 pages
5. Quick Reference Guide: 2-3 pages

**Total New Parameters Expected**: 50-100 parameters

**Priority Distribution**:
- P0 (Critical): 10-15 parameters
- P1 (High): 15-20 parameters
- P2 (Medium): 15-20 parameters
- P3 (Low): 10-15 parameters

**Implementation Timeline**: 6-8 weeks for P0-P2 parameters

---

**END OF RESEARCH PROMPT B**

