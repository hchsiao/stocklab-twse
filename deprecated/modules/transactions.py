import stocklab
import stocklab.module
from stocklab.datetime import Date, date_to_timestamp
from stocklab.crawler import CrawlerTrigger

class transactions(stocklab.module.Primitive):
  spec = {
      'update_offset': (13, 40),
      'disable_cache': True,
      'crawler_entry': 'TransactionCrawler.parser',
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

  def evaluate(self, db, args):
    table = db[self.name]
    query = table.stock_id == args.stock_id
    query &= table.date == args.date.timestamp()
    retval = db(query).select()
    if retval:
      return retval
    else:
      raise CrawlerTrigger(stock_id=args.stock_id, date=args.date)
