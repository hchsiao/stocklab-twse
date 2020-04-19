import time
import stocklab
from stocklab.datetime import Date, date_to_timestamp

class broker_deals(stocklab.Module):
  spec = {
      'update_offset': (17, 0),
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

  def peak_db(self, db, args):
    table = db[self.name]
    assert args.stock_id is not None
    query = table.stock_id == args.stock_id
    query &= table.date == args.date.timestamp()
    retval = db(query).select(limitby=(0, 1))
    if retval:
      return True, False, {'stock_id': args.stock_id, 'date': args.date}
    else:
      return False, True, {'stock_id': args.stock_id, 'date': args.date}

  def query_db(self, db, args):
    table = db[self.name]
    if args.stock_id is None:
      query = table.date == args.date.timestamp()
      retval = db(query).select(table.stock_id, distinct=True)
      return retval, False, {}
    else:
      query = table.stock_id == args.stock_id
      query &= table.date == args.date.timestamp()
      retval = db(query).select()
      if retval:
        if retval[0].broker_id is None:
          return [], False, {}
        else:
          return retval, False, {}
      else:
        return retval, True, {'stock_id': args.stock_id, 'date': args.date}
