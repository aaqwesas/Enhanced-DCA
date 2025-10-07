import backtrader as bt


class DollarCostAveraging(bt.Strategy):
    params = (
        ("invest_amount", 100),
        ("period", 3),
    )

    def __init__(self):
        self.order = None
        self.last_date = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            self.log(f"Executed: Price={order.executed.price:.2f}, "
                     f"Size={order.executed.size:.2f}, Cost={order.executed.value:.2f}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"Order failed: {order.getordername()}")

        self.order = None

    def next(self):
        if self.order:
            return

        current_date = self.datas[0].datetime.date(0)

        if self.last_date is None:
            days_passed = self.params.period
        else:
            days_passed = (current_date - self.last_date).days

        if days_passed < self.params.period:
            return

        cash = self.broker.get_cash()
        invest_amount = min(self.params.invest_amount, cash)

        if invest_amount <= 0:
            self.log("No cash to invest")
            return

        price = self.datas[0].close[0]
        size = invest_amount / price

        if size > 0:
            self.order = self.buy(
                size=size,
                exectype=bt.Order.Market,
            )
            self.last_date = current_date
            self.log(f"Buy: {size:.4f} shares at ${price:.2f} | Invested: ${invest_amount:.2f}")