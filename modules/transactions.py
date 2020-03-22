import time
import stocklab
from stocklab.date import Date

class transactions(stocklab.Module):
  spec = {
      'disable_cache': True,
      'crawler': 'TransactionCrawler.parser',
      'args': [
        'stock_id',
        ('date', Date),
        ],
      'schema': [
        ('stock_id text', "?", 'key'),
        ('date integer', "strftime('%s', ?)", 'key'),
        ('time integer', "strftime('%s', ?)", 'key'),
        ('buy real', "?"),
        ('sell real', "?"),
        ('deal real', "?"),
        ('volume integer', "?"),
        ]
      }

  def run(self, args):
    return self.access_db(args)

  def query_db(self, db, args):
    # Check stock validity
    stocklab.evaluate(f'twse.{args.stock_id}.{args.date}.open')

    select_sql = "SELECT *\
        FROM transactions\
        WHERE date = strftime('%s', ?) AND stock_id = ?"
    
    query = [r for r in db.execute(select_sql, (str(args.date), args.stock_id))]
    if query:
      return query, False, {'stock_id': args.stock_id, 'date': args.date}
    else:
      return query, True, {'stock_id': args.stock_id, 'date': args.date}
