import time
import stocklab
from stocklab.date import Date, date_to_timestamp

class broker_deals(stocklab.Module):
  spec = {
      'disable_cache': True,
      'crawler': 'WantgooCrawler.brokers',
      'args': [
        'stock_id',
        ('date', Date),
        ],
      'schema': {
        'stock_id': {'key': True},
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True},
        'broker_id': {'key': True},
        'buy_amt': {'type': 'integer'},
        'sell_amt': {'type': 'integer'},
        'buy_price': {'type': 'double'},
        'sell_price': {'type': 'double'},
        }
      }

  def run(self, args):
    return self.access_db(args)

  def query_db(self, db, args):
    table = db[self.name]
    query = table.stock_id == args.stock_id
    query &= table.date == args.date.timestamp()
    retval = db(query).select()
    if retval:
      return retval, False, {'stock_id': args.stock_id, 'date': args.date}
    else:
      return retval, True, {'stock_id': args.stock_id, 'date': args.date}
