#!/usr/bin/env python3
"""
Extract Strategy 107 Details from ALL_PORTFOLIOS Backtest Results

This script extracts the full details of Strategy 107 (highest Sharpe ratio)
from the ALL_PORTFOLIOS backtest results file.

Usage:
    python3 extract_strategy_107.py
"""

import pandas as pd
import sys
import os

# File path
BACKTEST_FILE = "/Users/maruth/projects/backtester-worktree-1/Trades/ALL_PORTFOLIOS 24082025 181358.xlsx"

def main():
    print("="*80)
    print("EXTRACTING STRATEGY 107 DETAILS")
    print("="*80)
    
    try:
        # Read Excel file
        xl_file = pd.ExcelFile(BACKTEST_FILE)
        print(f"\nFile: {BACKTEST_FILE}")
        print(f"Total sheets: {len(xl_file.sheet_names)}")
        
        # Find Metrics sheet
        metrics_sheets = [s for s in xl_file.sheet_names if 'Metrics' in s]
        if len(metrics_sheets) == 0:
            print("ERROR: No Metrics sheet found")
            sys.exit(1)
        
        print(f"\nMetrics sheet: {metrics_sheets[0]}")
        
        # Read Metrics sheet
        df_metrics = pd.read_excel(BACKTEST_FILE, sheet_name=metrics_sheets[0])
        
        # Find Strategy 107 (column index 107)
        # Columns are: Particulars, Combined, Strategy 1, Strategy 2, ..., Strategy N
        # So Strategy 107 is at column index 107 + 2 = 109 (0-indexed: 108)
        
        if df_metrics.shape[1] < 109:
            print(f"ERROR: Not enough columns. Found {df_metrics.shape[1]} columns")
            sys.exit(1)
        
        # Get column name for Strategy 107
        strategy_107_col = df_metrics.columns[108]  # 0-indexed
        print(f"\nStrategy 107 column: {strategy_107_col}")
        
        # Extract Strategy 107 metrics
        print("\n" + "="*80)
        print("STRATEGY 107 PERFORMANCE METRICS")
        print("="*80)
        
        for idx, row in df_metrics.iterrows():
            metric_name = row['Particulars']
            metric_value = row[strategy_107_col]
            print(f"{metric_name:50s}: {metric_value}")
        
        # Now find the corresponding strategy sheets
        # Strategy sheets are named like: "NIFTY_TEST PortfolioParameter", "NIFTY_TEST GeneralParameter", etc.
        # We need to find which strategy corresponds to column 108
        
        print("\n" + "="*80)
        print("SEARCHING FOR STRATEGY 107 CONFIGURATION SHEETS")
        print("="*80)
        
        # The sheet naming pattern suggests each strategy has multiple sheets:
        # - PortfolioParameter
        # - GeneralParameter
        # - LegParameter
        # - Metrics
        # - Max Profit and Loss
        # - PORTFOLIO Trans
        # - PORTFOLIO Results
        # - Individual leg sheets
        
        # Let's find all unique strategy prefixes
        strategy_prefixes = set()
        for sheet_name in xl_file.sheet_names:
            # Extract prefix (everything before the last space)
            parts = sheet_name.rsplit(' ', 1)
            if len(parts) == 2:
                prefix = parts[0]
                strategy_prefixes.add(prefix)
        
        strategy_prefixes = sorted(list(strategy_prefixes))
        print(f"\nFound {len(strategy_prefixes)} unique strategy prefixes")
        
        # Strategy 107 should be the 107th strategy (0-indexed: 106)
        if len(strategy_prefixes) > 106:
            strategy_107_prefix = strategy_prefixes[106]
            print(f"\nStrategy 107 prefix: {strategy_107_prefix}")
            
            # Find all sheets for this strategy
            strategy_107_sheets = [s for s in xl_file.sheet_names if s.startswith(strategy_107_prefix)]
            print(f"\nStrategy 107 sheets ({len(strategy_107_sheets)}):")
            for sheet in strategy_107_sheets:
                print(f"  - {sheet}")
            
            # Read key configuration sheets
            print("\n" + "="*80)
            print("STRATEGY 107 CONFIGURATION")
            print("="*80)
            
            # Portfolio Parameters
            portfolio_param_sheet = f"{strategy_107_prefix} PortfolioParameter"
            if portfolio_param_sheet in xl_file.sheet_names:
                print(f"\n--- {portfolio_param_sheet} ---")
                df_portfolio = pd.read_excel(BACKTEST_FILE, sheet_name=portfolio_param_sheet)
                print(df_portfolio.to_string(index=False))
            
            # General Parameters
            general_param_sheet = f"{strategy_107_prefix} GeneralParameter"
            if general_param_sheet in xl_file.sheet_names:
                print(f"\n--- {general_param_sheet} ---")
                df_general = pd.read_excel(BACKTEST_FILE, sheet_name=general_param_sheet)
                print(df_general.to_string(index=False))
            
            # Leg Parameters
            leg_param_sheet = f"{strategy_107_prefix} LegParameter"
            if leg_param_sheet in xl_file.sheet_names:
                print(f"\n--- {leg_param_sheet} ---")
                df_leg = pd.read_excel(BACKTEST_FILE, sheet_name=leg_param_sheet)
                print(df_leg.to_string(index=False))
            
            # Portfolio Results
            portfolio_results_sheet = f"{strategy_107_prefix} PORTFOLIO Results"
            if portfolio_results_sheet in xl_file.sheet_names:
                print(f"\n--- {portfolio_results_sheet} ---")
                df_results = pd.read_excel(BACKTEST_FILE, sheet_name=portfolio_results_sheet)
                print(f"Shape: {df_results.shape}")
                print(f"Columns: {list(df_results.columns)}")
                print(f"\nFirst 10 rows:")
                print(df_results.head(10).to_string(index=False))
            
            # Portfolio Transactions
            portfolio_trans_sheet = f"{strategy_107_prefix} PORTFOLIO Trans"
            if portfolio_trans_sheet in xl_file.sheet_names:
                print(f"\n--- {portfolio_trans_sheet} ---")
                df_trans = pd.read_excel(BACKTEST_FILE, sheet_name=portfolio_trans_sheet)
                print(f"Shape: {df_trans.shape}")
                print(f"Columns: {list(df_trans.columns)}")
                print(f"\nFirst 10 rows:")
                print(df_trans.head(10).to_string(index=False))
            
        else:
            print(f"ERROR: Not enough strategies. Found {len(strategy_prefixes)} strategies")
            sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

