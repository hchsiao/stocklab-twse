import logging
import stocklab
from stocklab.datetime import Date
from stocklab.error import NoLongerAvailable, InvalidDateRequested
from stocklab.utils import *

stocklab.change_log_level(logging.DEBUG)

def for_each_stock_id(cb):
  # all types
  type_ids = [row.type_id for row in stocklab.metaevaluate('stock_types')]
  type_names = [row.name for row in stocklab.metaevaluate('stock_types')]

  suspended = [row.stock_id for row in stocklab.metaevaluate('suspended')]
  for type_id in type_ids:
    type_count = stocklab.metaevaluate(f'stocks.count.{type_id}._')
    for s_idx in range(type_count):
      stock_id, stock_name, stock_type = stocklab.metaevaluate(f'stocks.get.{type_id}.{s_idx}')
      if not all([c.isdigit() for c in stock_id]):
        continue # ignore special stock
      if stock_id in suspended:
        continue
      cb(stock_id)

def up_to_date(mod_name, table_may_not_exist=True):
  assert type(date) is Date
  def _cb(stock_id):
    stocklab.evaluate(f'{mod_name}.{stock_id}.{date}')

  if not is_outdated(mod_name):
    return True

  _force_offline = stocklab.config['force_offline']
  stocklab.config['force_offline'] = True
  try:
    for_each_stock_id(_cb)
  except NoLongerAvailable as e:
    return False
  except Exception as e:
    # since exception types depend on DB
    # it is hard to track every possible types
    if table_may_not_exist:
      # This also hides other error
      return False
    else:
      raise e
  finally:
    stocklab.config['force_offline'] = _force_offline

  set_last_update_datetime(mod_name)
  return True

volatile = ['transactions', 'broker_deals']
date = Date.today()
try:
  stocklab.metaevaluate(f'valid_dates.{date}.1.lag')
  for mod_name in volatile:
    _crawl = lambda sid: stocklab.evaluate(f'{mod_name}.{sid}.{date}')
    if not up_to_date(mod_name, date):
      for_each_stock_id(_crawl)
except InvalidDateRequested:
  print('weekend or holiday')
  pass
