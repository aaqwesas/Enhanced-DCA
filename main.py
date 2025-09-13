from datetime import datetime
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import backtrader as bt
from Strategy import EnhancedDCA, WeightedDCA, DollarCostAveraging
from utils import plot_vwap_benchmark


def get_trade_analysis(analyzers) -> None:
    """
    Extract and print trade summary from TradeAnalyzer.
    Handles cases with no trades gracefully.
    """
    try:
        trades = analyzers.trade.get_analysis()
        total = trades.get("total", {}).get("closed", 0)
        won = trades.get("won", {}).get("total", 0)
        lost = trades.get("lost", {}).get("total", 0)
        win_rate = (won / total * 100) if total > 0 else 0
        avg_pnl = trades.get("pnl", {}).get("net", {}).get("average", 0)
        avg_won = trades.get("won", {}).get("pnl", {}).get("average", 0)
        avg_lost = trades.get("lost", {}).get("pnl", {}).get("average", 0)

        print("\n--- Trade Summary ---")
        print(f"Total Trades: {total}")
        print(f"Winning Trades: {won}")
        print(f"Losing Trades: {lost}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Avg Trade PnL: ${avg_pnl:.2f}")
        print(f"Avg Win: ${avg_won:.2f}, Avg Loss: ${avg_lost:.2f}")

        if "streak" in trades:
            print(
                f"Max Win Streak: {trades['streak'].get('won', {}).get('longest', 0)}"
            )
            print(
                f"Max Loss Streak: {trades['streak'].get('lost', {}).get('longest', 0)}"
            )
    except Exception as e:
        print(f"Error in trade analysis: {e}")


def get_return_metrics(analyzers) -> None:
    """
    Extract and print return metrics from Returns analyzer.
    """
    try:
        returns = analyzers.returns.get_analysis()
        total_return = returns.get("rtot", 0) * 100
        annualized_return = returns.get("rnorm", 0) * 100
        print(f"Total Return: {total_return:.2f}%")
        print(f"Annualized Return: {annualized_return:.2f}%")
    except Exception as e:
        print(f"Error in return metrics: {e}")


def get_drawdown(analyzers) -> None:
    """
    Extract and print drawdown metrics from DrawDown analyzer.
    """
    try:
        drawdown = analyzers.drawdown.get_analysis()
        print(f"Max Drawdown: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
        print(f"Max Drawdown Duration: {drawdown.get('max', {}).get('len', 0)} bars")
    except Exception as e:
        print(f"Error in drawdown analysis: {e}")


def get_transaction_details(analyzers, max_to_show: int = 20) -> None:
    """
    Print transaction details (buys/sells) from Transactions analyzer.
    """
    try:
        transactions = analyzers.transactions.get_analysis()
        print(f"\n--- Transaction Details (First {max_to_show}) ---")
        for i, (dt, trades_list) in enumerate(transactions.items()):
            if i >= max_to_show:
                print("... More transactions omitted")
                break
            for trade in trades_list:
                size, price, value, *_ = trade
                action = "BUY" if size > 0 else "SELL"
                print(
                    f"{dt} | {action} {abs(size):.2f} @ ${price:.2f} (Value: ${value:.2f})"
                )
    except Exception as e:
        print(f"Error in transaction details: {e}")


def run_backtest(
    output,
    csv_file: str = "data/AAPL_1min_firstratedata.csv",
    initial_cash: float = 1_000_000.0,
    commission: float = 0.001,
    plot_results: bool = True,
    invest_amount: int = 10000,
    period: int = 1,
) -> None:
    # Load and prepare data
    df = pd.read_csv(csv_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df.set_index("timestamp", inplace=True)

    data_feed = bt.feeds.PandasData(
        dataname=df,
        open="open",
        high="high",
        low="low",
        close="close",
        volume="volume",
        openinterest=-1,
    )

    strategies = [
        ("Dollar Cost Averaging", DollarCostAveraging),
        ("Enhanced DCA", EnhancedDCA),
    ]

    results = []
    equity_curves = {}
    output_dir = f"backtest/{output}"
    os.makedirs(output_dir, exist_ok=True)
    for name, strategy_class in strategies:
        cerebro = bt.Cerebro()
        cerebro.adddata(data_feed)
        cerebro.addstrategy(strategy_class, invest_amount=invest_amount, period=period)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)
        cerebro.broker.set_coc(True)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")

        print(f"Running: {name}")
        result = cerebro.run()[0]

        port_value = cerebro.broker.getvalue()
        sharpe = result.analyzers.sharpe.get_analysis().get("sharperatio", 0)
        total_return = result.analyzers.returns.get_analysis()["rtot"]
        drawdown = result.analyzers.drawdown.get_analysis()["max"]["drawdown"]
        sqn = result.analyzers.sqn.get_analysis().get("sqn", 0)
        trade_analysis = result.analyzers.trades.get_analysis()
        num_trades = trade_analysis.get("total", {}).get("total", 0)

        results.append({
            "Strategy": name,
            "Final Value": port_value,
            "Total Return (%)": total_return * 100,
            "Sharpe Ratio": sharpe,
            "Max Drawdown (%)": drawdown,
            "SQN": sqn,
            "Num Trades": num_trades,
        })

        # Store equity curve
        equity_curves[name] = pd.Series(result.analyzers.timereturn.get_analysis())

        # Optional: Plot individual strategy
        if plot_results:
            fig = cerebro.plot(style='candlestick', volume=True, iplot=False)[0][0]
            fig.savefig(str(Path(f"{output_dir}/{name}")), dpi=200, bbox_inches='tight')

    results_df = pd.DataFrame(results).round(2)
    print("\n" + "="*60)
    print("STRATEGY COMPARISON REPORT")
    print("="*60)
    print(results_df.to_string(index=False))

    
    results_csv_path = f"{output_dir}/comparison_report.csv"
    results_df.to_csv(results_csv_path, index=False)
    print(f"Comparison report saved to: {results_csv_path}")

    if plot_results:
        first_close = df["close"].iloc[0]
        buy_hold_returns = (df["close"] / first_close - 1).values
        timestamps = df.index

        plt.figure(figsize=(14, 8))
        for name, series in equity_curves.items():
            series = series.reindex(timestamps, method='ffill')  # Align indices
            plt.plot(timestamps, series.values, label=name, linewidth=3, alpha=0.7)

        plt.plot(timestamps, buy_hold_returns, label="Buy & Hold", linestyle="--", alpha=0.8)
        plt.title("Cumulative Returns: Strategy vs Buy & Hold")
        plt.xlabel("Time")
        plt.ylabel("Cumulative Return")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plot_path = f"{output_dir}/cumulative_returns.png"
        plt.savefig(plot_path, dpi=200, bbox_inches='tight')


def main():
    dir_path = Path("data")
    for path in dir_path.iterdir():
        output_dir = path.stem
        run_backtest(csv_file="data/AMZN_1min_firstratedata.csv",output=output_dir)

if __name__ == "__main__":
    main()
