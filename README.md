# Enhanced DCA vs. Traditional DCA Strategy Comparison

This project implements and compares three **Dollar-Cost Averaging (DCA)** investment strategies using [Backtrader](https://www.backtrader.com/), a Python framework for backtesting trading algorithms.

The goal is to evaluate the performance of each strategy and compare them using different performance metric

---

## Strategies Overview

### 1. **Traditional DCA**
- Invests a **fixed dollar amount** at regular intervals (e.g., every 3 days).
- Does not adjust for market conditions.
- Simple, disciplined, and passive.

```math
H_t = I \quad \text{for all } t = 0, 1, 2, \dots
```

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
```math
H_t = 
\begin{cases}
I & \text{if } t = 0 \\
H_{t-1} + f & \text{if } t > 0 \text{ and } p_t < p_{t-1} \\
H_{t-1} - f & \text{if } t > 0 \text{ and } p_t > p_{t-1} \\
H_{t-1} & \text{if } t > 0 \text{ and } p_t = p_{t-1}
\end{cases}
```

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

```math
r_t = \frac{p_t - p_{t-1}}{p_{t-1}}, \quad
s_t = \max\left(0.5, \min\left(2.0, 2(1 - r_t)\right)\right)
```

Then:
```math
H_t=
\begin{cases}
I & \text{if } t = 0 \\
s_t \cdot H_{t-1} & \text{if } t > 0\end{cases}
```


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
<!-- - **Cumulative Return vs Buy & Hold** -->

These are computed using Backtrader’s built-in analyzers.

---

## Analysis Results

### Sharpe Ratio:
The Sharpe ratio shows a roughly normal distribution but with very high kurtosis. This means that while most DCA strategies perform within normal ranges, there are more extreme outcomes than expected. Some strategies perform exceptionally well, while others perform very poorly. This makes sense because none of the strategies use take-profit or stop-loss rules, so there's no limit on how high or low returns can go. The high kurtosis tells us that "black swan" events (extreme results) happen more often than normal statistics would predict.

### Total Return:
The total return distribution is positively skewed, meaning most values are on the lower side with some very high returns pulling up the average. The mode (most common value) is around 0%, showing that many investments break even or have small returns. However, the mean return is 109.17%, which is much higher than the mode. This difference happens because a few investments with very high returns significantly boost the average.

### Maximum Drawdown:
The average maximum drawdown is 57.53%, which seems quite high. This means that on average, investments lose more than half their value at some point before the end of the investment period. This high drawdown suggests that DCA strategies can be quite risky in terms of temporary losses, even if they end up profitable.

### CAGR (Compound Annual Growth Rate):
The average CAGR is 7.27%, which is lower than the typical market return of around 10% annually. This happens because many of the investments in the dataset include penny stocks or poor-performing companies that drag down the overall average. If you only invested in well-performing stocks using fundamental analysis, the CAGR would likely be much higher. The current average reflects the reality of investing in a mix of good and bad companies.

### Win Rate by Strategy:
- Weighted DCA: 50.2% win rate
- Enhanced DCA: 32.5% win rate  
- DCA: 17.3% win rate

The win rate shows that Weighted DCA wins most often, followed by Enhanced DCA, with regular DCA winning least often. This suggests that the weighted approach (buying more when prices are lower) is more effective than the other strategies.

### Maximum Drawdown by Strategy:
- Weighted DCA has the highest maximum drawdown on average
- Enhanced DCA has the lowest maximum drawdown on average

This result is interesting because Weighted DCA, which buys more shares when prices drop, ends up with higher maximum drawdowns. This happens because when prices keep falling, the strategy keeps buying more, which increases the total loss. On the other hand, Enhanced DCA has the lowest drawdown, suggesting it's the most protective against large losses, even though it doesn't win as often.

### Strategy Performance Summary:
The results show that different strategies have different strengths:
- Weighted DCA wins most often but takes the most risk (highest drawdown)
- Enhanced DCA takes the least risk but wins less often
- Regular DCA performs the worst in both win rate and risk management

This suggests that the Enhanced DCA approach might need adjustment, as it doesn't perform as well as expected despite having lower risk.

## Key Insights

1. **Risk vs Reward**: There's a clear trade-off between winning frequency and risk. Strategies that win more often tend to have higher maximum losses.

2. **Market Reality**: The average returns are lower than market benchmarks because the dataset includes many poor-performing stocks. Real-world investing would likely show better results with careful stock selection.

3. **Strategy Choice**: The choice of DCA strategy depends on your risk tolerance. If you want to win more often, Weighted DCA is best, but you'll face higher temporary losses. If you want to minimize losses, Enhanced DCA is better, but you'll win less often.

4. **Extreme Events**: The high kurtosis in Sharpe ratios means you should expect more extreme outcomes than normal statistics suggest. This is important for managing expectations and risk.

5. **Parameter Optimization**: The Enhanced DCA strategy may need parameter adjustments, as its performance doesn't match expectations given its lower risk profile.