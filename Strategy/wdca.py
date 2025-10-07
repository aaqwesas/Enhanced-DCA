from typing import Tuple
import backtrader as bt
from Indicator import AccumulativeSwingIndex

class WeightedDCA(bt.Strategy):
    params: Tuple[Tuple[str,int]] = (
        ('sma_period', 30),           
        ('std_period', 30),           
        ('vol_period', 30),           
        ('atr_period', 14),           
        ('base_risk_percent', 0.5),   
        ('min_entry_distance', 0.05),
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.sma_period)
        self.std = bt.indicators.StdDev(self.data.close, period=self.params.std_period)
        self.avg_volume = bt.indicators.SMA(self.data.volume, period=self.params.vol_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.asi = AccumulativeSwingIndex(self.data, T_percent=0.02)
        self.unrealized_pnl_history = []
        
        self.entries = []
        self.entry_sizes = []
        self.lowest_entry = None
        self.order = None 

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            if order.isbuy():
                entry_price = order.executed.price
                self.entries.append(entry_price)
                self.entry_sizes.append(order.size)
                
                # Update lowest entry
                if self.lowest_entry is None or entry_price < self.lowest_entry:
                    self.lowest_entry = entry_price
                
                self.log(f"BUY EXECUTED, Price: {entry_price:.2f}, Size: {order.size}, Total: {self.position.size}")
            elif order.issell():
                self.log(f"SELL EXECUTED, Price: {order.executed.price:.2f}, Size: {order.size}")
                
                # Reset after full exit
                if self.position.size == 0:
                    self.entries = []
                    self.entry_sizes = []
                    self.lowest_entry = None

        self.order = None

    def calculate_signal_strength(self):
        """Calculate how aggressively to buy based on multiple factors"""
        current_price = self.data.close[0]
        
        # 1. Distance from SMA (more weight when below SMA)
        sma_diff = (self.sma[0] - current_price) / self.sma[0]
        sma_factor = min(sma_diff * 5, 1)
        
        # 2. Volatility factor (less aggressive when volatile)
        volatility_factor = 1.0 / (1.0 + (self.atr[0] / current_price))
        
        # 3. Volume factor (more weight when volume is high)
        volume_factor = self.data.volume[0] / self.avg_volume[0]
        volume_factor = max(min(volume_factor, 4), 1)
        
        current_asi = self.asi.asi[0]
        prev_asi = self.asi.asi[-1]
        if prev_asi != 0:
            asi_change = (current_asi - prev_asi) / abs(prev_asi)
        else:
            asi_change = 1.0 if current_asi > 0 else -1.0 if current_asi < 0 else 0.0
        
        trend_factor = min(max(asi_change * 10 + 1.0, 0.5), 3.0)
        
        
        signal_strength = (
            sma_factor * 0.4 +
            volatility_factor * 0.2 +
            volume_factor * 0.3 +
            trend_factor * 0.1
        )
        
        return signal_strength
    def get_average_entry_price(self):
        """
        Calculate the weighted average entry price based on all executed buys.
        Returns 0 if no positions are held.
        """
        if not self.entries or not self.entry_sizes:
            return 0.0
        
        total_cost = sum(price * size for price, size in zip(self.entries, self.entry_sizes))
        total_size = sum(self.entry_sizes) 
        
        return total_cost / total_size if total_size > 0 else 0.0

    def calculate_entry_size(self) -> int:
        """Calculate position size based on signal strength"""
        current_price = self.data.close[0]
        account_value = self.broker.getvalue()
        
        base_size = (account_value * (self.params.base_risk_percent / 100)) / current_price
        
        # Apply signal strength
        signal_strength = self.calculate_signal_strength()
        size = base_size * signal_strength
        
        return max(1, int(size))

    def can_enter_position(self):
        """Check if we can add another entry"""

        current_price = self.data.close[0]
        
        # If no entries yet, always allow
        if not self.entries:
            return True
            
        last_entry = self.entries[-1]
        price_diff_percent = (last_entry - current_price) / last_entry * 100
        
        return price_diff_percent >= self.params.min_entry_distance

    def next(self):
        if self.order:
            return
        
        if self.position.size != 0:
            unrealized_pnl = (self.data.close[0] - self.position.price) * self.position.size
            self.unrealized_pnl_history.append(unrealized_pnl)
        else:
            self.unrealized_pnl_history.append(0.0)
            
        current_price = self.data.close[0]
        
        # ——— Entry Logic ———
        if self.can_enter_position():
            size = self.calculate_entry_size()
            self.log(f"BUY CREATE, Price: {current_price:.2f}, Size: {size}, Signal: {self.calculate_signal_strength():.2f}")
            self.order = self.buy(size=size)
