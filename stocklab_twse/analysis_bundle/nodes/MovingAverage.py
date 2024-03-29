from stocklab.node import *
from stocklab import DataIdentifier as DI
from stocklab_twse.utils.datetime import Date
from stocklab_twse.utils import date_range

class MovingAverage(Node):
    args = Args(
            stock = Arg(),
            date = Arg(type=Date),
            window = Arg(type=int),
            )

    def evaluate(stock, date, window):
        prices = [DI('DailyData')(stock=stock, date=d)['close'] \
                  for d in date_range(end=date, window=window)]
        return sum(prices)/len(prices)
