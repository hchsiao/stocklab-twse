import time
import stocklab
from stocklab.date import Date

class broker_deals(stocklab.Module):
  spec = {
      'disable_cache': True,
      'crawler': 'WantgooCrawler.brokers',
      'args': [
        'stock_id',
        ('date', Date),
        ],
      'schema': [
        ('stock_id text', "?", 'key'),
        ('date integer', "strftime('%s', ?)", 'key'),
        ('broker_id text', "?", 'key'),
        ('buy_amt integer', "?"),
        ('sell_amt integer', "?"),
        ('buy_price real', "?"),
        ('sell_price real', "?"),
        ]
      }

  def run(self, args):
    return self.access_db(args)

  def query_db(self, db, args):
    select_sql = "SELECT *\
        FROM broker_deals\
        WHERE date = strftime('%s', ?) AND stock_id = ?"
    
    query = [r for r in db.execute(select_sql, (str(args.date), args.stock_id))]
    if query:
      return query, False, {'stock_id': args.stock_id, 'date': args.date}
    else:
      return query, True, {'stock_id': args.stock_id, 'date': args.date}
