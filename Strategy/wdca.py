import backtrader as bt

class WeightedDCA(bt.Strategy):
    params = (
        ('invest_amount', 100),
        ('max_investment', 200),
        ("min_investment", 50),
        ('period', 1),
    )

    def __init__(self):
        self.last_buy_date = None
        self.last_buy_price = None
        self.order = None 

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            # self.log(f"Executed BUY: Price={order.executed.price:.2f}, "
            #          f"Size={order.executed.size:.2f}, Cost={order.executed.value:.2f}")

            self.last_buy_date = self.data.datetime.date(0)
            self.last_buy_price = order.executed.price
            
        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log(f"Order failed: {order.getstatusname()}")

        self.order = None

    def calculate_signal_strength(self):
        current_price = self.data.close[0]
        
        # Default signal strength if any problem occur
        default_signal = 1.0

        if self.last_buy_price is None:
            return default_signal
            
        if self.last_buy_price == 0:
            # self.log("Warning: Last buy price is zero, using default signal strength")
            return default_signal
        
        if current_price == 0:
            # self.log("Warning: Current price is zero, using default signal strength")
            return default_signal
        
        price_change_pct = (current_price - self.last_buy_price) / self.last_buy_price
        
        signal_strength = (1 - price_change_pct) * 2
        
        signal_strength = max(0.5, min(2.0, signal_strength))
        
        return signal_strength

    def calculate_entry_size(self) -> float:
        current_price = self.data.close[0]
        cash = self.broker.getcash()
        if current_price == 0:
            # self.log("Warning: Current price is zero")
            return 0.0
        
        signal_strength = self.calculate_signal_strength()
        adjusted_dollars =  max(self.p.min_investment,min(self.p.max_investment, self.p.invest_amount * signal_strength))
        size = min(adjusted_dollars / current_price, cash / current_price)
        
        return max(0.0, size)

    def should_buy_today(self):
        current_date = self.data.datetime.date(0)
        if self.last_buy_date is None:
            return True
        days_since_last = (current_date - self.last_buy_date).days
        return days_since_last >= self.p.period

    def next(self):
        if self.order:
            return
        
        if not self.should_buy_today():
            return
            
        size = self.calculate_entry_size()
        if size > 0:
            self.order = self.buy(size=size, exectype=bt.Order.Market)