import stocklab
from stocklab.date import Date
import numpy as np

# all types
type_ids, type_names = list(zip(*stocklab.metaevaluate('stock_types')))

def rand_stock(targets=None):
  if targets is None:
    targets = type_ids
  # get n_stocks
  type_counts = np.array([
      stocklab.metaevaluate(f'stocks.count.{s_type}._') for s_type in targets])
  n = np.random.randint(type_counts.sum(), size=1)[0]
  acc_counts = np.cumsum(type_counts)
  target_idx = np.argwhere(acc_counts > n)[0][0]
  acc_counts[-1] = 0
  inclass_id = n - acc_counts[target_idx-1] 
  type_id = targets[target_idx]
  return stocklab.metaevaluate(f'stocks.get.{type_id}.{inclass_id}')

# TODO: use numpy random
def rand_date(start, end, size=1):
  #conn = sqlite3.connect(stocklab.DATABASE_FILE)
  # use pyDAL instead
  c = conn.cursor()
  
  start = str(Date(start))
  end = str(Date(end))
  stocklab.evaluate(f'valid_dates.{start}.1.lag')
  stocklab.evaluate(f'valid_dates.{end}.1.lag')

  sql = "SELECT date(date, 'unixepoch')\
      FROM valid_dates\
      WHERE date <= strftime('%s', ?)\
      AND date >= strftime('%s', ?)\
      ORDER BY RANDOM()\
      LIMIT ?;"
  result = [r[0] for r in c.execute(sql, (end, start, size))]

  if conn:
    conn.close()
  
  return result
