import stocklab
import stocklab.module
from stocklab.datetime import Date, date_to_timestamp
from stocklab.crawler import CrawlerTrigger

class twse(stocklab.module.Primitive):
  spec = {
      'ignore_existed': True, # API returns a month at once
      'disable_cache': False,
      'crawler_entry': 'TwseCrawler.stock_day',
      'args': [
        'stock_id',
        ('date', Date),
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

  def evaluate(self, db, args):
    table = db[self.name]
    query = table.stock_id == args.stock_id
    query &= table.date == args.date.timestamp()
    retval = db(query).select(limitby=(0, 1))
    if retval:
      return retval[0]
    else:
      raise CrawlerTrigger(date=args.date, stock_id=args.stock_id)
