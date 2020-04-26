import numpy as np
import stocklab
from stocklab.datetime import Date

class moving_average(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ('N', int),
        ]
      }
  def evaluate(self, db, args):
    return np.array(stocklab.evaluate(
      f'ohlc.{args.stock_id}.($trade_dates.{args.date}.{args.N}.lag)'
      )).mean()
