import stocklab
import stocklab.module
from stocklab.datetime import Date

class ohlc(stocklab.module.CandleStick):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ],
      }

  def evaluate(self, db, args):
    data = stocklab.evaluate(f'twse.{args.stock_id}.{args.date}')
    return data.open, data.max, data.min, data.close
