# Enhanced DCA vs. Traditional DCA Strategy Comparison

This project implements and compares three **Dollar-Cost Averaging (DCA)** investment strategies using [Backtrader](https://www.backtrader.com/), a Python framework for backtesting trading algorithms.

The goal is to evaluate the performance of each strategy and compare them using different performance metric

---

## Strategies Overview

### 1. **Traditional DCA**
- Invests a **fixed dollar amount** at regular intervals (e.g., every 3 days).
- Does not adjust for market conditions.
- Simple, disciplined, and passive.

$$
H_t = I \quad \text{for all } t = 0, 1, 2, \dots
$$

where:  
- $H_t$: investment amount at time $t$,  
- $I$: constant (base) investment amount (e.g., \$100 per interval).


---

### 2. **Enhanced DCA (EDCA)**
- Also invests at fixed intervals.
- **Dynamically adjusts investment size** based on price movement since the last buy:
  - If price has **dropped**, increase investment by a fixed amount (buy more on dips).
  - If price has **risen**, reduce investment by a fixed amount (avoid overbuying at highs).
- Formula:  
$$H_t = 
\begin{cases}
I & \text{if } t = 0 \\
H_{t-1} + f & \text{if } t > 0 \text{ and } p_t < p_{t-1} \\
H_{t-1} - f & \text{if } t > 0 \text{ and } p_t > p_{t-1} \\
H_{t-1} & \text{if } t > 0 \text{ and } p_t = p_{t-1}
\end{cases}$$

where:
- $H_t$: investment amount at time $t$,
- $I$: base investment,
- $f$: fixed adjustment amount,
- $p_t$: asset price at time $t$.


- The implementation idea is based on the paper [here](https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1025&context=financefacpub) with modification

### 3. **Weighted DCA (EDCA)**
- Similar to **EDCA**, but this strategy will determine the quantity to buy based on the market movement in percentage
signal is caluclate like the following 
```py
price_change_pct = (current_price - self.last_buy_price) / self.last_buy_price

signal_strength = (1 - price_change_pct) * 2

signal_strength = max(0.5, min(2.0, signal_strength))
```
the reason for mutliply signal strength by 2 is to just make the strategy more aggressive. Modify if needed

the mathematical formulation:
$$r_t = \frac{p_t - p_{t-1}}{p_{t-1}}, \quad$$
$$s_t = \max\left(0.5,\; \min\left(2.0,\; 2(1 - r_t)\right)\right)$$

Then:
$$H_t = 
\begin{cases}
I & \text{if } t = 0 \\
s_t \cdot H_{t-1} & \text{if } t > 0
\end{cases}
$$


> This creates a **mean-reverting bias**, buying more when assets are cheaper.

---

## Backtesting Setup
run the following command to your virtual environment
```bash
pip install -r requirements.txt
```
then just run
```bash
python main.py
```

---


## Performance Metrics

Each strategy is evaluated using the following metrics:

- **Final Portfolio Value**
- **Total Return (%)**
- **Sharpe Ratio** (risk-adjusted return)
- **Max Drawdown (%)**
- **Cumulative Return vs Buy & Hold**

These are computed using Backtrader’s built-in analyzers.

---

## Results

working on it

---

## Key Insights

---