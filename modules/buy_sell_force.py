import numpy as np
import time
import stocklab
from stocklab.datetime import Date

class buy_sell_force(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ('n_days', int),
        ],
      }

  def run(self, args):
    brokers = stocklab.evaluate(f'stock_brokers.{args.stock_id}._.{args.date}.{args.n_days}')
    force_list = np.array([b['buy_amt'] - b['sell_amt'] for bid, b in brokers.items()])
    return force_list
