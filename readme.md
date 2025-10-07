# Enhanced DCA vs. Traditional DCA Strategy Comparison

This project implements and compares three **Dollar-Cost Averaging (DCA)** investment strategies using [Backtrader](https://www.backtrader.com/), a Python framework for backtesting trading algorithms.

The goal is to evaluate whether an **adaptive, market-aware Enhanced DCA (EDCA)** strategy outperforms a **fixed-interval DCA** approach over time in terms of return, risk, and efficiency.

---

## Strategies Overview

### 1. **Traditional DCA**
- Invests a **fixed dollar amount** at regular intervals (e.g., every 3 days).
- Does not adjust for market conditions.
- Simple, disciplined, and passive.

### 2. **Enhanced DCA (EDCA)**
- Also invests at fixed intervals.
- **Dynamically adjusts investment size** based on price movement since the last buy:
  - If price has **dropped**, increase investment (buy more on dips).
  - If price has **risen**, reduce investment (avoid overbuying at highs).
- Formula:  
  Investment adjustment =  
    - **+2×% drop** (e.g., 2% drop → +4% investment)  
    - **–% gain** (e.g., 3% gain → –3% investment) 
- The implementation idea is based on the paper [here](https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1025&context=financefacpub) with modification
- All the investment parameter are configurable

### 3. **Weighted DCA (EDCA)**
- Similar to **EDCA**, but this strategy will be more aggressively buying into the market when the price drop 

> This creates a **mean-reverting bias**, buying more when assets are cheaper.

---

## Backtesting Setup
Put your csv file in the data folder

| Parameter | Value |
|--------|-------|
| Data Source | 1-minute OHLCV data (e.g., AAPL, META) |
| Timeframe | Multiple days/weeks (intraday or daily) |
| Initial Capital | $1,000,000 |
| Commission | 0.1% per trade |
| Rebalance Period | default: every 7 days 9 (Configurable) |
| Base Investment | $2,000 per period |

Strategies are tested on historical data with realistic transaction costs.

---

## Performance Metrics

Each strategy is evaluated using the following metrics:

- **Final Portfolio Value**
- **Total Return (%)**
- **Sharpe Ratio** (risk-adjusted return)
- **Max Drawdown (%)**
- **Number of Trades**
- **SQN (System Quality Number)**
- **Cumulative Return vs Buy & Hold**

These are computed using Backtrader’s built-in analyzers.

---

## Results

Below are visualizations of the backtest results using tickerMSFT with 1 min timeframe, the result would be more informative if using other timeframe like the daily timeframe.

![Cumulative Returns](/cumulative_returns.png)
> *Comparison of cumulative returns: EDCA vs DCA vs Buy & Hold*

![DCA](/Dollar%20Cost%20Averaging.png)
> *DCA alone*

![Enhanced DCA](/Enhanced%20DCA.png)
> *Enhanced DCA*

---

## Key Insights

- **EDCA tends to outperform DCA** in volatile or sideways markets by increasing exposure during pullbacks.
- In strong bull markets, **DCA may underperform** as it reduces buys on new highs.
- The adaptive sizing in EDCA improves **risk-adjusted returns** (higher Sharpe).

---


## How to Run

### Prerequisites
- Python 3.8+
- Install dependencies:
  ```bash
  pip install backtrader pandas matplotlib pyfolio
  ```
  run:
    ```bash
    python main.py
    ```



## To be implemeneted:
- a more complicated DCA strategy (Weighted DCA strategy), which would take into account of other important factor (volume, std, volatility, trend, etc)
