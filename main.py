from pathlib import Path
from typing import Dict, Tuple, List, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import backtrader as bt
from Strategy import EnhancedDCA, WeightedDCA, DollarCostAveraging
import yfinance as yf
import json
import multiprocessing

def add_analyzers(cerebro) -> None:
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")

def test_strategy(
        Strategy,
        data_feed,
        commission,
        output_dir,
        name,
        initial_cash,
        **kwargs) -> Tuple[Dict[str, float], pd.Series]:
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy=Strategy, **kwargs)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.broker.set_coc(True)
    
    add_analyzers(cerebro=cerebro)

    result = cerebro.run()[0]
    
    

    port_value = cerebro.broker.getvalue()
    sharpe_analysis = result.analyzers.sharpe.get_analysis()
    drawdown_analysis = result.analyzers.drawdown.get_analysis()
    returns_analysis = result.analyzers.returns.get_analysis()

    sharpe = sharpe_analysis.get("sharperatio", 0) or 0
    total_return = returns_analysis["rtot"]
    max_drawdown = drawdown_analysis["max"]["drawdown"]
    
    # fig = cerebro.plot(volume=False, style="line", loc="black", plotvaluetags=False,plotlinevalues=False)[0][0]
    # fig.savefig(f"{output_dir}/{name.replace(' ', '_')}")
    
    timereturn = result.analyzers.timereturn.get_analysis()
    curve: pd.Series = pd.Series(timereturn)
    
    res = {
        "Strategy": name,
        "Final Value": round(port_value, 2),
        "Total Return (%)": round(total_return * 100, 2),
        "CAGR (%)": round((port_value / initial_cash) ** (252 / len(curve)) - 1, 4) * 100,
        "Sharpe Ratio": round(sharpe, 3),
        "Max Drawdown (%)": round(max_drawdown, 2),
    }
    
    return res, curve

def run_backtest(
    ticker: str,
    output_path: Path,
    initial_cash: int = 100_000,
    commission: float = 0.001,
    invest_amount: int = 100,
    period: int = 7,
) -> Optional[pd.DataFrame]:
    try:    
        df = yf.download(tickers=ticker, interval="1d", period="max", auto_adjust=True, multi_level_index=False)
    except Exception as e:
        print(f"Error downloading data for {ticker}: {e}")
        return None

    if df.empty:
        print(f"No data for {ticker}")
        return None
    df.index.name = ticker
    
    data_feed = bt.feeds.PandasData(
        dataname=df,
        open="Open",
        high="High",
        low="Low",
        close="Close",
        volume="Volume",
        openinterest=-1,
    )

    strategies = [
        ("DCA", DollarCostAveraging, {"invest_amount": invest_amount, "period": period}),
        ("Enhanced DCA", EnhancedDCA, {"invest_amount": invest_amount, "period": period, "adjustment": 5, "max_investment": 30, "min_investment": 10}),
        ("Weighted DCA", WeightedDCA, {"invest_amount": invest_amount, "period": period, "max_investment": 50, "min_investment": 7.5}),
    ]
    
    results = []
    # equity_curves = {}
    output_dir = output_path / f"backtest_{ticker}"
    # output_dir.mkdir(exist_ok=True)
    
    for name, strategy, params in strategies:
        try:
            res, curve = test_strategy(
                Strategy=strategy,
                data_feed=data_feed,
                initial_cash=initial_cash,
                output_dir=output_dir,
                name=name,
                commission=commission,
                **params
            )
            if res:
                # equity_curves[name] = curve
                results.append(res)
        except Exception as e:
            print(f"skipped {name}, {ticker}, got error: {e}")
            continue
            
    if not results:
        return None

    results_df = pd.DataFrame(results).round(2)
    results_df["Ticker"] = ticker
    # csv_path = output_dir / "comparison_report.csv"
    # results_df.to_csv(csv_path, index=False)

    
    # timestamps = df.index

    # plt.figure(figsize=(14, 8))
    # for name, series in equity_curves.items():
    #     series = series.reindex(timestamps, method='ffill')
    #     plt.plot(timestamps, series.values, label=name, linewidth=2.5, alpha=0.8)

    # plt.title(f"Cumulative Returns: {ticker}")
    # plt.xlabel("Time")
    # plt.ylabel("Cumulative Return")
    # plt.legend()
    # plt.grid(True, alpha=0.3)
    # plt.tight_layout()

    # plot_path = output_dir / "cumulative_returns.png"
    # plt.savefig(plot_path, dpi=150, bbox_inches='tight'
    print(f"ticker: {ticker} finished")
    return results_df

def generate_summary(output_dir: Path, all_results: List[pd.DataFrame]):
    if not all_results:
        print("No results to summarize")
        return

    full_results = pd.concat(all_results, ignore_index=True)
    full_results.sort_values(by=["Ticker", "Total Return (%)"], ascending=[True, False], inplace=True)

    full_csv = output_dir / "all_strategies_all_stocks.csv"
    full_results.to_csv(full_csv, index=False)

    tickers = full_results["Ticker"].unique()
    strategies = full_results["Strategy"].unique()
    win_counts = {s: 0 for s in strategies}

    for ticker in tickers:
        df_ticker = full_results[full_results["Ticker"] == ticker]
        best_strategy = df_ticker.loc[df_ticker["Total Return (%)"].idxmax(), "Strategy"]
        win_counts[best_strategy] += 1

    total_comparisons = len(tickers)
    win_rate_data = []
    for strategy in strategies:
        wins = win_counts[strategy]
        win_rate = (wins / total_comparisons) * 100
        win_rate_data.append({
            "Strategy": strategy,
            "Wins": wins,
            "Total Comparisons": total_comparisons,
            "Win Rate (%)": round(win_rate, 2)
        })

    win_rate_df = pd.DataFrame(win_rate_data)
    win_rate_csv = output_dir / "strategy_win_rates.csv"
    win_rate_df.to_csv(win_rate_csv, index=False)

def main(tickers_file: Path, output_path: Path):
    output_path.mkdir(exist_ok=True)

    # Load all tickers first
    tickers = []
    with open(tickers_file, "r") as f:
        for line in f:
            row = json.loads(line.strip())
            ticker = row.get("ticker") or row.get("symbol")
            if ticker:
                tickers.append(ticker)

    num_workers = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_workers) as pool:
        args = [(ticker, output_path, 5000.0, 0.001, 15, 3) for ticker in tickers]
        all_results = pool.starmap(run_backtest, args)
    
    all_results = [df for df in all_results if df is not None]

    generate_summary(output_dir=output_path, all_results=all_results)




if __name__ == "__main__":
    tickers = Path("company_tickers.jsonl")
    output_path = Path("backtest")
    main(tickers_file=tickers, output_path=output_path)