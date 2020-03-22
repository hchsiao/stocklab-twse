import stocklab
from stocklab.date import Date
import logging

logger = logging.getLogger('_states')
logger.setLevel(stocklab.log_level)

with stocklab.get_db(logger) as c:
  # Create table
  create_sql = f"CREATE TABLE _states (\
      key text, val text,\
      PRIMARY KEY (key)\
  );"
  if not c.has_table('_states'):
    c.execute(create_sql)

def get(key):
  with stocklab.get_db(logger) as c:
    select_sql = f"SELECT val FROM _states WHERE key = ?"
    query_res = [r for r in c.execute(select_sql, (key,))]
    return query_res[0][0] if query_res else None
  assert False

def set(key, val, fmt='?'):
  assert type(val) is str, f'expected type is str, got {type(val)}'
  old_val = get(key)
  with stocklab.get_db(logger) as c:
    if old_val:
      sql = f"UPDATE _states SET val={fmt} WHERE key = ?"
      c.execute(sql, (val, key))
    else:
      sql = f"INSERT INTO _states(key, val) VALUES(?, {fmt})"
      c.execute(sql, (key, val))
    c.commit()
    return
  assert False
