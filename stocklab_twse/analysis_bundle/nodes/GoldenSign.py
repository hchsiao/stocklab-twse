from stocklab.node import *
from stocklab import DataIdentifier as DI
from stocklab_twse.utils.datetime import Date
from stocklab_twse.utils import date_range

class GoldenSign(Node):
    # Heuristic: to increase coverage, expanding window
    # is better than lowering gain threshold
    BASE_GAIN = 1.005876
    
    args = Args(
            stock = Arg(),
            date = Arg(type=Date),
            window = Arg(type=int),
            gain = Arg(type=float),
            mode = Arg(oneof=['bull', 'bear', 'price_first', 'time_first']),
            )

    def evaluate(stock, date, window, gain, mode):
        gain = GoldenSign.BASE_GAIN * gain
        
        prices = [DI('DailyData')(stock=stock, date=d) \
                  for d in date_range(start=date, window=window)]

        init_price = prices[0]['close']
        # TODO: also try 'max' or 'min' instead of 'close'
        max_price = max([p['close'] for p in prices[1:]])
        min_price = min([p['close'] for p in prices[1:]])
        buy = max_price > init_price * gain
        sell = min_price * gain < init_price
        if not buy and not sell:
            return 0
        if buy and not sell:
            return 1 if mode != 'bear' else 0
        if not buy and sell:
            return -1 if mode != 'bull' else 0
        
        # Both buy and sell flags are asserted
        if mode == 'bull':
            return 1
        elif mode == 'bear':
            return -1
        elif mode == 'price_first':
            buy_gain = max_price / init_price
            sell_gain = init_price / min_price
            return 1 if buy_gain > sell_gain else -1
        else: # mode == 'time_first'
            buy_delay = [p['close'] > init_price * gain for p in prices[1:]].index(True)
            sell_delay = [p['close'] * gain < init_price for p in prices[1:]].index(True)
            return 1 if buy_delay < sell_delay else -1