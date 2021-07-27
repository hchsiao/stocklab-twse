from stocklab.node import *
from stocklab import DataIdentifier as DI
from stocklab_twse.utils.datetime import Date

class MovingAverage(Node):
    args = Args(
            stock = Arg(),
            date = Arg(type=Date),
            window = Arg(type=int),
            )

    def evaluate(stock, date, window):
        dates = [date.shift(-d) for d in range(window)]
        prices = [DI('DailyData')(stock=stock, date=d)['close'] \
                for d in dates if DI('DateTrades')(date=d)]
        return sum(prices)/len(prices)
