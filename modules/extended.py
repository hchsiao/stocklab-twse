import stocklab
from stocklab.datetime import Date
import numpy as np

class extended(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('N', int),
        ]
      }
  def run(self, args):
    indices = stocklab.metaevaluate(f'valid_dates.{args.date}.{args.N}.lag')
    paths = [f'peak.{args.stock_id}.{_date}' for _date in indices]
    data = np.array([stocklab.evaluate(p) for p in paths])

    return data.any()
