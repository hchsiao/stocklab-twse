import stocklab
from stocklab.datetime import Date

class volumn(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ],
      }

  def evaluate(self, db, args):
    data = stocklab.evaluate(f'twse.{args.stock_id}.{args.date}')
    return data.delta_price_share
