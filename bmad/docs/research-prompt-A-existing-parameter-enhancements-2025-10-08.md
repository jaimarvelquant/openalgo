# Research Prompt A: Existing Parameter Enhancement Research

**Generated**: 2025-10-08  
**Target Platforms**: ChatGPT Deep Research / Gemini Deep Research / Grok DeepSearch  
**Research Type**: Parameter System Enhancement Analysis  
**Estimated Research Time**: 90-120 minutes

---

## 🎯 Research Objective

Conduct comprehensive research on industry best practices and enhancement opportunities for all currently implemented parameters in the backtester's `Util.py` module. The goal is to identify specific, actionable improvements that will make the parameter system more robust, flexible, and aligned with professional trading platform standards.

---

## 📋 Context and Background

### Project Overview

We are integrating a Python-based algorithmic trading backtester with MarvelQuant (a Flask-based multi-broker trading platform) to enable live trading execution. The backtester contains an extensive parameter system implemented in `btrun/Util.py` (3,761 lines) that controls:

- **Strategy Execution**: Entry/exit logic, timing, combinations
- **Risk Management**: Stop-loss, take-profit, trailing stops
- **Position Sizing**: Lot sizing, capital allocation
- **Re-entry Logic**: Re-entry types, cool-down periods, conditions
- **Market Data**: Strike selection, expiry handling, underlying selection
- **Indicators**: VWAP, EMA, RSI, Supertrend, Volume SMA
- **Portfolio Management**: Portfolio-level targets, stop-loss, trailing

### Current Parameter System

The `Util.py` module contains numerous parameter categories including:

**Strategy-Level String Parameters** (STGY_STR_PARA_COLUMN_NAME_UPPER):
- StrategyName, Index, TgtTrackingFrom, TgtRegisterPriceFrom, SlTrackingFrom, SlRegisterPriceFrom
- PnLCalculationFrom, ConsiderHedgePnLForStgyPnL, CheckPremiumDiffCondition
- PremiumDiffType, PremiumDiffChangeStrike, PremiumDiffDoForceEntry
- Underlying, Tradertype, MoveSlToCost, ChangeStrikeForIndicatorBasedReEntry
- OnExpiryDayTradeNextExpiry, ConsiderVwapForEntry/Exit, ConsiderEMAForEntry/Exit
- ConsiderSTForEntry/Exit, ConsiderRSIForEntry/Exit, ConsiderVolSmaForEntry/Exit
- StrategyType

**Leg-Level Parameters** (LEG_STR_PARA_COLUMN_NAME):
- Instrument, Transaction, W&Type, StrikeMethod, MatchPremium
- SLType, TGTType, TrailSLType, Expiry
- SL_ReEntryType, TGT_ReEntryType, ReEntryType
- OpenHedge, HedgeStrikeMethod, IsIdle
- OnEntry_SqOffAllLegs, OnExit_SqOffAllLegs, OnExit_OpenAllLegs
- TrailW&T

**Alias Mappings**:
- EXPIRY_ALIAS: CURRENT → WEEKLY, NEXT → NEXT_WEEKLY, MONTHLY → MONTHLY
- RE_ENTRY_ALIAS: INSTANT SAME STRIKE → IMMIDIATE, ORIGINAL → AS_ORIGINAL, COST → RE_COST
- TGT_SL_ALIAS: POINT, PERCENTAGE, INDEX_POINT, INDEX_PERCENTAGE, PREMIUM, ABSOLUTE_DELTA
- UNDERLYING_ALIAS: SPOT → CASH, FUTURE → FUTURE

**Backtest Fields** (BT_FIELDS - 100+ parameters):
- Entry/Exit: StartTime, EndTime, LastEntryTime, StrikeSelectionTime
- Risk: SLValue, TGTValue, SLType, TGTType, TrailSLType, SL_TrailAt, SL_TrailBy
- Re-entry: SL_ReEntryType, TGT_ReEntryType, SL_ReEntryNo, TGT_ReEntryNo, ReEnteriesCount
- Indicators: VwapEntryCondition, EmaEntryCondition, StEntryCondition, RsiEntryCondition
- Portfolio: PortfolioTarget, PortfolioStoploss, PortfolioTrailingType
- Strategy: StrategyProfit, StrategyLoss, StrategyProfitReExecuteNo, StrategyLossReExecuteNo
- Timing: StoplossCheckingInterval, TargetCheckingInterval, ReEntryCheckingInterval
- And many more...

### Integration Goals

1. **Live Trading Readiness**: Parameters must support real-time execution via MarvelQuant API
2. **Excel/JSON Dual Format**: Parameters must map cleanly between Excel input sheets and JSON schemas
3. **Validation and Safety**: Enhanced validation to prevent configuration errors in live trading
4. **Industry Alignment**: Parameters should match or exceed industry standards from platforms like QuantConnect, TradeStation, Interactive Brokers

---

## 🔍 Specific Research Questions

**YOU MUST ANSWER THESE QUESTIONS:**

### 1. Re-entry Parameter Enhancements

**Current Implementation**:
- RE_ENTRY_ALIAS: "INSTANT SAME STRIKE" → IMMIDIATE, "ORIGINAL" → AS_ORIGINAL, "COST" → RE_COST, "INSTANT NEW STRIKE" → IMMIDIATE_NC
- SL_ReEntryType, TGT_ReEntryType, ReEntryType
- SL_ReEntryNo, TGT_ReEntryNo, ReEnteriesCount
- ReEntryCheckingInterval

**Research Questions**:
- What additional re-entry strategies are used in professional trading platforms? (pyramiding, scaling in/out, averaging down/up, grid trading)
- How do platforms like QuantConnect and TradeStation implement re-entry logic?
- What are best practices for re-entry cool-down periods? (fixed time, dynamic based on volatility, market regime-based)
- How should re-entry be handled differently for live trading vs backtesting?
- What validation rules prevent excessive re-entries that could lead to over-leveraging?

### 2. Stop-Loss Parameter Enhancements

**Current Implementation**:
- SLType, SLValue, TrailSLType, SL_TrailAt, SL_TrailBy
- TGT_SL_ALIAS: POINT, PERCENTAGE, INDEX_POINT, INDEX_PERCENTAGE, PREMIUM, ABSOLUTE_DELTA
- MoveSlToCost

**Research Questions**:
- What trailing stop variations are industry-standard? (ATR-based, percentage-based, time-based, chandelier stops)
- How do professional platforms implement volatility-adjusted stop-losses?
- What are best practices for "move SL to cost" logic? (when to trigger, partial vs full move)
- How should stop-loss be calculated for multi-leg strategies? (per-leg, strategy-level, portfolio-level)
- What are time-based stop-loss strategies? (exit after X minutes/hours regardless of P&L)

### 3. Position Sizing Parameter Enhancements

**Current Implementation**:
- Lots (quantity parameter)
- FIELDS_TO_MULTIPLY_BY_PORTFOLIO_MULTIPLIER: Lots

**Research Questions**:
- What position sizing methods are industry-standard? (Kelly Criterion, fixed fractional, volatility-based, risk parity)
- How do platforms implement dynamic position sizing based on account equity?
- What are best practices for position sizing in multi-leg strategies?
- How should position sizing adapt to market volatility? (VIX-based, ATR-based)
- What validation rules prevent over-leveraging or excessive risk?

### 4. Strike Selection Parameter Enhancements

**Current Implementation**:
- StrikeMethod, StrikeValue, TradeStrikeValue
- HedgeStrikeMethod, HedgeStrikeValue
- MatchPremium, StrikePremiumCondition, HedgeStrikePremiumCondition
- PremiumDiffType, PremiumDiffChangeStrike, PremiumDiffDoForceEntry

**Research Questions**:
- What strike selection methods are used in professional options trading platforms?
- How do platforms handle dynamic strike selection based on market conditions?
- What are best practices for premium-based strike selection?
- How should strike selection differ for different option strategies? (straddle, strangle, iron condor, butterfly)
- What validation ensures selected strikes are liquid and tradeable?

### 5. Indicator-Based Entry/Exit Enhancements

**Current Implementation**:
- ConsiderVwapForEntry/Exit, VwapEntryCondition, VwapExitCondition
- ConsiderEMAForEntry/Exit, EmaEntryCondition, EmaExitCondition, EMAPeriod
- ConsiderSTForEntry/Exit, StEntryCondition, StExitCondition, STPeriod, STMultiplier
- ConsiderRSIForEntry/Exit, RsiEntryCondition, RsiExitCondition, RsiPeriod
- ConsiderVolSmaForEntry/Exit, VolSmaEntryCondition, VolSmaExitCondition, VolSMAPeriod

**Research Questions**:
- What are industry best practices for combining multiple indicators? (AND vs OR logic, weighted scoring)
- How do platforms implement indicator parameter optimization? (period optimization, threshold optimization)
- What additional indicators should be supported? (MACD, Bollinger Bands, Ichimoku, ADX)
- How should indicator calculations differ for live trading vs backtesting? (real-time vs historical data)
- What validation prevents indicator parameter combinations that are too restrictive or too loose?

### 6. Portfolio-Level Parameter Enhancements

**Current Implementation**:
- PortfolioTarget, PortfolioStoploss, PortfolioTrailingType
- PortfolioName, PortfolioID
- MaxOpenPositions

**Research Questions**:
- What portfolio-level risk management parameters are industry-standard? (max drawdown limits, correlation-based limits)
- How do platforms implement portfolio-level trailing stops?
- What are best practices for managing multiple strategies within a portfolio?
- How should portfolio-level limits interact with strategy-level limits?
- What validation ensures portfolio-level parameters don't conflict with strategy-level parameters?

### 7. Timing Parameter Enhancements

**Current Implementation**:
- StartTime, EndTime, LastEntryTime, StrikeSelectionTime
- StoplossCheckingInterval, TargetCheckingInterval, ReEntryCheckingInterval
- PnLCalTime, SqOff1Time, SqOff2Time

**Research Questions**:
- What are best practices for time-based entry/exit logic in live trading?
- How do platforms handle time zone conversions for global markets?
- What are industry standards for checking intervals? (real-time, 1-second, 5-second, tick-by-tick)
- How should timing parameters adapt to market volatility? (faster checks during high volatility)
- What validation prevents timing conflicts? (LastEntryTime before EndTime, etc.)

### 8. Expiry Handling Parameter Enhancements

**Current Implementation**:
- Expiry, EXPIRY_ALIAS: CURRENT → WEEKLY, NEXT → NEXT_WEEKLY, MONTHLY → MONTHLY
- OnExpiryDayTradeNextExpiry
- DTE (Days to Expiry)

**Research Questions**:
- What are best practices for handling expiry rollovers in live trading?
- How do platforms implement automatic expiry detection and rollover?
- What are industry standards for DTE-based strategy adjustments?
- How should expiry handling differ for different instruments? (weekly options, monthly options, futures)
- What validation ensures expiry parameters are consistent with market calendars?

### 9. Hedge Management Parameter Enhancements

**Current Implementation**:
- OpenHedge, HedgeStrikeMethod, HedgeStrikeValue, HedgeStrikePremiumCondition
- ConsiderHedgePnLForStgyPnL

**Research Questions**:
- What are industry best practices for dynamic hedging in options strategies?
- How do platforms implement delta-neutral hedging?
- What are best practices for hedge ratio calculations?
- How should hedge management differ for different market regimes? (trending vs ranging)
- What validation ensures hedge parameters are consistent with main strategy parameters?

### 10. Strategy Type Parameter Enhancements

**Current Implementation**:
- StrategyType: TBS, ORB, VWAP, HEIKIN_RSI_EMA, HEIKIN_RSI_ST, 5_EMA, OI, INDICATOR
- USER_BT_TYPE_ENGINE_MAPPING

**Research Questions**:
- What additional strategy types should be supported? (mean reversion, momentum, arbitrage)
- How do platforms implement strategy type-specific parameter validation?
- What are best practices for strategy type classification and organization?
- How should strategy type affect default parameter values?
- What validation ensures strategy type is compatible with selected parameters?

---

## 📊 Required Analysis Areas

### Area 1: Parameter Validation and Safety

**Analyze**:
- Current validation logic in `Util.py`
- Industry best practices for parameter validation in trading systems
- Common parameter configuration errors and how to prevent them
- Validation rules for cross-parameter dependencies
- Safety mechanisms to prevent dangerous configurations in live trading

**Deliverable**: Comprehensive validation rule library with code examples

### Area 2: Parameter Default Values

**Analyze**:
- Current default values for all parameters
- Industry best practices for default parameter values
- How defaults should differ for live trading vs backtesting
- How defaults should differ for different strategy types
- How defaults should differ for different instruments (options, futures, equities)

**Deliverable**: Default value recommendations with justification

### Area 3: Parameter Ranges and Constraints

**Analyze**:
- Current valid ranges for numeric parameters
- Industry best practices for parameter ranges
- How ranges should differ for different market conditions
- How ranges should differ for different account sizes
- Dynamic range adjustment based on market volatility

**Deliverable**: Valid range specifications for all parameters

### Area 4: Parameter Dependencies

**Analyze**:
- Current parameter dependencies (which parameters depend on others)
- Industry best practices for managing parameter dependencies
- How to validate parameter combinations
- How to handle conflicting parameter values
- How to provide user-friendly error messages for dependency violations

**Deliverable**: Parameter dependency matrix with validation rules

### Area 5: Parameter Optimization

**Analyze**:
- Which parameters are candidates for optimization
- Industry best practices for parameter optimization methods
- How to prevent over-fitting during optimization
- How to validate optimized parameters before live deployment
- How to monitor parameter performance in live trading

**Deliverable**: Parameter optimization framework with best practices

---

## 📄 Expected Deliverables

### 1. Executive Summary (2-3 pages)

**Content**:
- Key findings from research
- Priority enhancements ranked by impact and effort
- Quick wins (low effort, high impact)
- Long-term enhancements (high effort, high impact)
- Risk areas requiring immediate attention

**Format**: Markdown with bullet points, tables, and priority matrix

### 2. Parameter Enhancement Catalog (10-15 pages)

**Content**:
- For EACH parameter currently in `Util.py`:
  - Current implementation details
  - Industry best practices for similar parameters
  - At least 3 specific enhancement opportunities
  - Examples from leading platforms (QuantConnect, TradeStation, IB)
  - Implementation complexity estimate (low/medium/high)
  - Priority ranking (P0/P1/P2/P3)

**Format**: Table with columns: Parameter Name, Current Implementation, Industry Best Practice, Enhancement Opportunities, Examples, Complexity, Priority

### 3. Implementation Roadmap (2-3 pages)

**Content**:
- Prioritized list of enhancements
- Effort estimates (person-days)
- Dependencies between enhancements
- Phased implementation plan (Phase 1: Quick Wins, Phase 2: Medium Effort, Phase 3: Long-term)
- Risk mitigation strategies

**Format**: Gantt chart (described in text), priority matrix, dependency graph

### 4. Code Examples (5-7 pages)

**Content**:
- Complete, runnable code examples for top 5 priority enhancements
- Before/after comparisons
- Validation logic examples
- Unit test examples
- Integration with existing `Util.py` code

**Format**: Python code blocks with detailed comments

### 5. Validation Rule Library (3-5 pages)

**Content**:
- Comprehensive validation rules for all parameters
- Cross-parameter validation rules
- Error message templates
- Validation code examples
- Test cases for validation logic

**Format**: Table with validation rules + Python code examples

---

## ✅ Success Criteria

**The research is successful if it provides:**

1. ✅ **Complete Coverage**: All parameters from `Util.py` are documented and analyzed
2. ✅ **Specific Enhancements**: At least 3 enhancement opportunities identified per parameter
3. ✅ **Industry Grounded**: All recommendations cite industry best practices with sources
4. ✅ **Implementation Ready**: Code examples are complete, runnable, and integrate with existing code
5. ✅ **Prioritized**: Clear priority ranking with justification (impact vs effort)
6. ✅ **Validated**: Validation rules cover all edge cases and prevent dangerous configurations
7. ✅ **Live Trading Ready**: Enhancements specifically address live trading requirements
8. ✅ **Excel/JSON Compatible**: Enhancements work with dual-format configuration system
9. ✅ **Backward Compatible**: Enhancements don't break existing backtest configurations
10. ✅ **Actionable**: Development team can immediately start implementing from the research

---

## 🔗 Preferred Sources and References

### Trading Platform Documentation

1. **QuantConnect LEAN Engine** (open-source): https://github.com/QuantConnect/Lean
   - Parameter system implementation
   - Risk management parameters
   - Position sizing algorithms

2. **Interactive Brokers API**: https://interactivebrokers.github.io/tws-api/
   - Order types and parameters
   - Risk management features
   - Portfolio management

3. **TradeStation**: https://www.tradestation.com/platforms-and-tools/
   - Strategy parameters
   - Risk management tools
   - Position sizing methods

4. **Alpaca Trading API**: https://alpaca.markets/docs/
   - Order parameters
   - Risk management
   - Portfolio management

5. **TradingView Pine Script**: https://www.tradingview.com/pine-script-docs/
   - Indicator parameters
   - Strategy parameters
   - Risk management

### Academic and Industry Research

6. **Risk Management Best Practices**:
   - "The Mathematics of Money Management" by Ralph Vince
   - "Trade Your Way to Financial Freedom" by Van K. Tharp
   - "Quantitative Trading" by Ernest Chan

7. **Position Sizing Methods**:
   - Kelly Criterion research papers
   - Fixed fractional position sizing
   - Volatility-based position sizing

8. **Options Trading Parameters**:
   - CBOE (Chicago Board Options Exchange) documentation
   - Options Industry Council (OIC) resources
   - Professional options trading platforms

### Technical Documentation

9. **Python Trading Libraries**:
   - pandas documentation (data handling)
   - numpy documentation (numerical calculations)
   - TA-Lib documentation (technical indicators)

10. **Validation and Safety**:
    - JSON Schema documentation
    - Python validation libraries (pydantic, marshmallow)
    - Trading system safety best practices

---

## 🎯 Technology Stack Constraints

**ALL RECOMMENDATIONS MUST WORK WITHIN THIS STACK:**

- **Backend**: Python 3.8+, Flask 2.x with Blueprints
- **Data Processing**: pandas, numpy
- **File Handling**: openpyxl (Excel), JSON (configuration)
- **Validation**: JSON Schema, custom Python validation
- **Integration**: MarvelQuant API for live trading
- **Database**: SQLite 3.x

**DO NOT SUGGEST**: Technologies outside this stack (e.g., PostgreSQL, Redis, React, Vue)

---

## 🤖 Platform-Specific Optimization Tips

### For ChatGPT Deep Research

- Emphasize: "Analyze QuantConnect LEAN engine GitHub repository for parameter implementation patterns"
- Request: "Provide complete Python code examples compatible with Python 3.8+"
- Specify: "Include validation logic using JSON Schema and pydantic"

### For Gemini Deep Research

- Start with: "Research parameter enhancement opportunities for algorithmic trading backtester"
- Request: "Generate comparison tables for different enhancement approaches"
- Follow-up: "Provide detailed code examples for top 5 priority enhancements"

### For Grok DeepSearch

- Specify: "Focus on 2024-2025 best practices for trading system parameters"
- Request: "Search for recent discussions on trading platform parameter design"
- Use Think Mode: "Reason through trade-offs between different enhancement approaches"

---

## 📋 Validation Checklist

After research completion, verify:

- [ ] All parameters from `Util.py` BT_FIELDS are analyzed
- [ ] At least 3 enhancements per parameter
- [ ] Industry sources cited (QuantConnect, TradeStation, IB, etc.)
- [ ] Code examples are Python 3.8+ compatible
- [ ] Validation rules cover edge cases
- [ ] Priority ranking is justified
- [ ] Implementation roadmap is realistic
- [ ] Backward compatibility is addressed
- [ ] Live trading requirements are met
- [ ] Excel/JSON compatibility is maintained

---

**END OF RESEARCH PROMPT A**

