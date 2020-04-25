import numpy as np
import stocklab
from stocklab.datetime import Date

class force_variance(stocklab.Module):
  spec = {
      'args': [
        ('mode', ['buy', 'sell']),
        'stock_id',
        ('date', Date),
        ('days', int),
        ('min_force', int),
        ],
      }

  def evaluate(self, db, args):
    bsf = stocklab.evaluate(f'tendency.{args.mode}.{args.stock_id}.{args.date}.{args.days}')
    bsf = bsf[bsf > args.min_force]
    def normalize(v):
      norm = np.linalg.norm(v)
      if norm == 0: 
        return v
      return v / norm
    return normalize(bsf).var() if len(bsf) else 0.0
