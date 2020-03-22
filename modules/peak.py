import stocklab
from stocklab.date import Date
import numpy as np

class peak(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ]
      }
  def run(self, args):
    indices = stocklab.metaevaluate(f'valid_dates.{args.date}.3.zero')
    paths = [f'twse.{args.stock_id}.{_date}.close' for _date in indices]
    data = np.array([stocklab.evaluate(p) for p in paths])

    return data[1] > data[0] and data[1] > data[2]
