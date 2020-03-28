import stocklab
from stocklab.datetime import Date
import numpy as np

class myma(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('N', int),
        ]
      }
  def run(self, args):
    # operations
    indices = stocklab.metaevaluate(f'valid_dates.{args.date}.{args.N}.zero')
    paths = [f'twse.{args.stock_id}.{_date}.min' for _date in indices]
    low = np.array([stocklab.evaluate(p) for p in paths])
    paths = [f'twse.{args.stock_id}.{_date}.max' for _date in indices]
    high = np.array([stocklab.evaluate(p) for p in paths])

    return (low + high).mean()/2
