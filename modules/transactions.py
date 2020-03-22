import time
import stocklab
from stocklab.date import Date, date_to_timestamp

class transactions(stocklab.Module):
  spec = {
      'disable_cache': True,
      'crawler': 'TransactionCrawler.parser',
      'args': [
        'stock_id',
        ('date', Date),
        ],
      'schema': {
        'stock_id': {'key': True},
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True},
        'time': {'type': 'integer', 'key': True},
        'buy': {'type': 'double'},
        'sell': {'type': 'double'},
        'deal': {'type': 'double'},
        'volume': {'type': 'integer'},
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
