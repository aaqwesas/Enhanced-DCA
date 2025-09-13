import pandas as pd


def plot_vwap_benchmark(df: pd.DataFrame) -> None:
    """
    Calculate and print the final VWAP (Volume Weighted Average Price) for the dataset.
    Optionally plot if needed (currently prints only).
    """
    df = df.set_index("timestamp").sort_index()
    df["typical_price"] = (df["high"] + df["low"]) / 2
    df["cumulative_tp_vol"] = (df["typical_price"] * df["volume"]).cumsum()
    df["cumulative_volume"] = df["volume"].cumsum()
    df["vwap"] = df["cumulative_tp_vol"] / df["cumulative_volume"]
    total_vwap = df["vwap"].iloc[-1]
    print(f"Final VWAP: {total_vwap:.4f}")
