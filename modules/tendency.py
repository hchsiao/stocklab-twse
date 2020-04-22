import numpy as np
import stocklab
from stocklab.datetime import Date

class tendency(stocklab.Module):
  spec = {
      'args': [
        ('buy_or_sell', ['buy', 'sell']),
        'stock_id',
        ('date', Date),
        ('n_days', int),
        ],
      }

  def evaluate(self, args):
    brokers = stocklab.evaluate(f'stock_brokers.{args.stock_id}._.{args.date}.{args.n_days}')
    force_list = np.array([b['buy_amt'] - b['sell_amt'] for bid, b in brokers.items()])
    if 'buy' == args.buy_or_sell:
      return force_list[force_list > 0]
    else:
      return -force_list[force_list < 0]
