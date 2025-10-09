import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def plot_distribution(df, metrics):
    """ plot total return, CAGR, Sharpe Ratio, and Max Drawdown using boxplot  """
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, metric in enumerate(metrics):
        if metric in df.columns:
            # Overall distribution
            axes[i].hist(df[metric], bins=100, alpha=0.7, color='skyblue', edgecolor='black')
            axes[i].set_title(f'Distribution of {metric}')
            axes[i].set_xlabel(metric)
            axes[i].set_ylabel('Frequency')
            axes[i].grid(True, alpha=0.3)
            
            # Add statistics
            mean_val = df[metric].mean()
            std_val = df[metric].std()
            axes[i].axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
            axes[i].legend()
            
    axes[5].remove()
    plt.tight_layout()
    plt.show()

def plot_and_analyze():
    df = pd.read_csv("all_strategies_all_stocks.csv")
    print(f"Total records: {len(df)}")
    print(f"Unique tickers: {df['Ticker'].nunique()}")
    print(f"Unique strategies: {df['Strategy'].unique()}")
    
    metrics = ['Total Return (%)', 'CAGR (%)', 'Sharpe Ratio', 'Max Drawdown (%)', 'Final Value']
    plot_distribution(df=df, metrics=metrics)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        if metric in df.columns:
            sns.boxplot(data=df, x='Strategy', y=metric, ax=axes[i])
            axes[i].set_title(f'{metric} Distribution by Strategy')
            axes[i].tick_params(axis='x', rotation=45)

    # Remove the extra subplot
    axes[5].remove()
    plt.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    plot_and_analyze()