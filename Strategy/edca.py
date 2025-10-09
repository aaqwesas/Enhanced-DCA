import backtrader as bt

class EnhancedDCA(bt.Strategy):
    params = (
        ('period', 3),
        ('invest_amount', 100),
        ('adjustment', 5),
        ('max_investment', 200),
        ('min_investment', 50),
    )

    def __init__(self) -> None:
        self.order = None
        self.last_buy_date = None
        self.last_buy_price = None
        self.current_investment = float(self.p.invest_amount)

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status == order.Completed:
            # self.log(f"Executed BUY: Price={order.executed.price:.2f}, "
            #          f"Size={order.executed.size:.2f}, Cost={order.executed.value:.2f}")

            self.last_buy_date = self.data.datetime.date(0)
            self.last_buy_price = order.executed.price
        self.order = None

    def _update_next_investment(self, current_buy_price):
        if self.last_buy_price is None:
            self.current_investment = self.p.invest_amount
            return

        price_change = current_buy_price - self.last_buy_price
        if price_change < 0:
            self.current_investment += self.p.adjustment
        elif price_change > 0:
            self.current_investment -= self.p.adjustment

        self.current_investment = max(self.p.min_investment, min(self.p.max_investment, self.current_investment))


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

        cash = self.broker.getcash()
        current_price = self.data.close[0]
        self._update_next_investment(current_price)
        invest_amount = min(self.current_investment, cash)
        
        stake = invest_amount / current_price
        
        if stake > 0:
            self.order = self.buy(size=stake, exectype=bt.Order.Market)