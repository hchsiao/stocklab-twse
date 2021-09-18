'''
import stocklab

def random_simulate(date, days, dates_expr, ohlc_expr, sign_expr, stocks_expr=None, verbose=False):
    dates_expr = dates_expr(date, days)
    dates = stocklab.metaevaluate(dates_expr)
    if not stocks_expr:
        stocks_expr = stocklab.config['stocks_of_interest']

    stocks = np.asarray(list(stocklab.metaevaluate(stocks_expr)))
    np.random.shuffle(stocks)

    def _sim(stock_id):
        ohlcs = np.asarray(stocklab.evaluate(ohlc_expr(stock_id, f'(${dates_expr})')))
        prices = ohlcs[:,3]
        signs = stocklab.evaluate(sign_expr(stock_id, f'(${dates_expr})'))
        return simulate(dates, signs, prices, verbose)

    for sid in stocks:
        yield sid, _sim(sid)

def convolve(xs, kernel='average', n=None):
        KERNEL_MAPPERS = {
                'average': lambda n: np.ones(n),
                'exp': lambda n: np.exp(np.linspace(-1., 0., n)),
                }
        if kernel in KERNEL_MAPPERS.keys():
            assert n
            kernel = KERNEL_MAPPERS[kernel](n)
            kernel /= kernel.sum()

        assert len(xs) > len(kernel)
        xs = np.asarray(xs)
        ys = np.convolve(xs, kernel, mode='same')
        n_boundary = (len(kernel) - 1) / 2.0
        left_boundary = int(n_boundary)
        ys[:left_boundary] = np.nan
        ys[left_boundary + len(xs) - len(kernel) + 1:] = np.nan
        return ys
'''
import numpy as np

from stocklab import DataIdentifier as DI
from stocklab_twse.utils.datetime import Date

def date_range(start=None, mid=None, end=None, window=None, trade_date_only=True):
    if window is None:
        assert start and end and mid is None
        raise NotImplementedError()
    else:
        assert start or mid or end
        if mid is not None:
            raise NotImplementedError()
        curr_date = Date(start or end)
        delta = 1 if start else -1
        while window > 0:
            if DI('DateTrades')(date=curr_date):
                yield curr_date
                window -= 1 if trade_date_only else 0
            window -= 0 if trade_date_only else 1
            curr_date = curr_date.shift(delta)


class Simulator:
    def __init__(self, balance=None, max_share=1):
        self.n_share = 0
        self.balance = 0 if balance is None else balance
        self.budget_limited = balance is not None
        self.max_share = max_share
        self.price = None
        self.buy_rate = 1.001425
        self.sell_rate = 1 / 1.004425

    def can_buy(self):
        assert self.price is not None
        affordable = not self.budget_limited or \
                self.balance >= self.price
        return affordable and \
                self.n_share < self.max_share

    def can_sell(self):
        assert self.price is not None
        return self.n_share > 0

    def update(self, price):
        self.price = price

    def current_hold(self):
        return self.balance + self.n_share * self.price

    def __call__(self, dates, sign, prices):
        balance_seq = np.empty(len(dates))
        for i in range(len(dates)):
            self.update(prices[i])
            if sign[i] > 0 and self.can_buy():
                self.trade(prices[i], 1)
            if sign[i] < 0 and self.can_sell():
                self.trade(prices[i], -1)
            balance_seq[i] = self.current_hold()
        return balance_seq

    def trade(self, price, buy_amount):
        rate = self.buy_rate if buy_amount > 0 else self.sell_rate
        self.balance -= price * buy_amount * rate
        self.n_share += buy_amount
