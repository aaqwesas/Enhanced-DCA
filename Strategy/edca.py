import backtrader as bt

class EnhancedDCA(bt.Strategy):
    params = (
        ('period', 3),
        ('invest_amount', 1000),
        ('max_increase', 1),
        ('max_decrease', 0.50),
    )

    def __init__(self):
        self.order = None
        self.last_buy_date = None
        self.last_buy_price = None
        self.current_investment = float(self.params.invest_amount)

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            order_type = "BUY" if order.isbuy() else "SELL"
            self.log(f"Executed {order_type}: Price={order.executed.price:.2f}, Size={order.executed.size:.2f}, Cost={order.executed.value:.2f}")

            if order.isbuy():
                self.last_buy_date = self.data.datetime.date(0)
                self.last_buy_price = order.executed.price

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"Order failed: {order.getstatusname()}")

        self.order = None

    def should_buy_today(self):
        current_date = self.data.datetime.date(0)
        if self.last_buy_date is None:
            return True
        days_since_last = (current_date - self.last_buy_date).days
        return days_since_last >= self.params.period

    def adjust_investment_size(self):
        if self.last_buy_price is None:
            return

        current_price = self.data.close[0]
        price_change_pct = (current_price - self.last_buy_price) / self.last_buy_price

        adjustment_factor = 0.0

        if price_change_pct < 0:
            adjustment_factor = -2.0 * price_change_pct
        else:
            adjustment_factor = -price_change_pct

        max_up = self.params.max_increase
        max_down = -self.params.max_decrease
        adjustment_factor = max(max_down, min(adjustment_factor, max_up))

        self.current_investment = self.params.invest_amount * (1 + adjustment_factor)

    def next(self):
        if self.order:
            return

        if not self.should_buy_today():
            return

        self.adjust_investment_size()

        cash = self.broker.getcash()
        current_price = self.data.close[0]
        stake = self.current_investment / current_price

        if stake > 0 and cash >= self.current_investment * 1.01:
            self.log(f"Buying ${self.current_investment:.2f} at {current_price:.2f}")
            self.order = self.buy(size=stake)
        else:
            self.log("Insufficient cash")