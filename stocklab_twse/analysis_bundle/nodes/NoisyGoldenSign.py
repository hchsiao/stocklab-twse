from stocklab.node import *
from stocklab import DataIdentifier as DI
from stocklab_twse.utils.datetime import Date
from stocklab_twse.utils import date_range

class NoisyGoldenSign(Node):
    args = Args(
            stock = Arg(),
            date = Arg(type=Date),
            window = Arg(type=int),
            )

    def evaluate(stock, date, window):
        raise NotImplementedError()
