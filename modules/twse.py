import stocklab
from stocklab.date import Date

class twse(stocklab.Module):
  ATTR_NAMES = ['delta_n_share', 'delta_price_share', \
          'open', 'max', 'min', 'close', 'n_transactions']

  spec = {
      'ignore_nonunique': True, # API returns a month at once
      'disable_cache': False,
      'crawler': 'TwseCrawler.stock_day',
      'args': [
        'stock_id', # default type: str
        ('date', Date),
        ('attr', ATTR_NAMES),
        ],
      'schema': [
        ('stock_id text', "?", 'key'),
        ('date integer', "strftime('%s', ?)", 'key'),
        ('delta_n_share integer', "?"),
        ('delta_price_share integer', "?"),
        ('open real', "?"),
        ('max real', "?"),
        ('min real', "?"),
        ('close real', "?"),
        ('n_transactions integer', "?"),
        ]
      }

  def run(self, args):
    # Check date validity
    stocklab.metaevaluate(f'valid_dates.{args.date}.1.lag')
    return self.access_db(args)[args.attr]

  def query_db(self, db, args):
    select_sql = "SELECT *\
        FROM twse\
        WHERE date = strftime('%s', ?) AND stock_id = ?"
    
    query = [r for r in db.execute(select_sql, (str(args.date), args.stock_id))]
    if query:
      query_res = {}
      for i in range(len(twse.spec['schema'])):
        field_name = twse.spec['schema'][i][0].split(' ')[0]
        query_res[field_name] = query[0][i]
      db_miss = False
    else:
      query_res = None
      db_miss = True
    return query_res, db_miss, {'date': args.date, 'stock_id': args.stock_id}
