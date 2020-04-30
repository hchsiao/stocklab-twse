import numpy as np
import stocklab
from stocklab.datetime import Date

class rsi_array(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ('days', int),
        ('n', int),
        ]
      }
  def evaluate(self, db, args):
    n = args.n
    days = args.days + n
    prices = np.asarray(stocklab.evaluate(
      f'ohlc.{args.stock_id}.($trade_dates.{args.date}.{days}.lag)'
      ))[:,3]

    deltas = np.diff(prices)
    seed = deltas[:n - 1]
    up = seed[seed > 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100. / (1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi[n:]
