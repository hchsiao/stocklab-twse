import stocklab
from stocklab.date import Date, date_to_timestamp

class twse(stocklab.Module):
  ATTR_NAMES = ['delta_n_share', 'delta_price_share', \
          'open', 'max', 'min', 'close', 'n_transactions']

  spec = {
      'ignore_existed': True, # API returns a month at once
      'disable_cache': False,
      'crawler': 'TwseCrawler.stock_day',
      'args': [
        'stock_id', # default type: str
        ('date', Date),
        ('attr', ATTR_NAMES),
        ],
      'schema': {
        'stock_id': {'key': True},
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True},
        'delta_n_share': {'type': 'integer'},
        'delta_price_share': {'type': 'integer'},
        'open': {'type': 'double'},
        'max': {'type': 'double'},
        'min': {'type': 'double'},
        'close': {'type': 'double'},
        'n_transactions': {'type': 'integer'},
        }
      }

  def run(self, args):
    # Check date validity
    stocklab.metaevaluate(f'valid_dates.{args.date}.1.lag')
    return self.access_db(args)[args.attr]

  def query_db(self, db, args):
    table = db[self.name]
    query = table.stock_id == args.stock_id
    query &= table.date == args.date.timestamp()
    retval = db(query).select()
    if retval:
      return retval[0], False, {'date': args.date, 'stock_id': args.stock_id}
    else:
      return None, False, {'date': args.date, 'stock_id': args.stock_id}
