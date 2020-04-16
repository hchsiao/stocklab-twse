import logging
import stocklab
from stocklab.datetime import Date
from stocklab.error import NoLongerAvailable, InvalidDateRequested
from stocklab.utils import *

stocklab.change_log_level(logging.DEBUG)

def for_each_stock_id(cb):
  suspended = [row.stock_id for row in stocklab.metaevaluate('suspended')]
  stock_list = stocklab.metaevaluate(f'stock_list')
  for row in stock_list:
    stock_id = row.stock_id
    if not all([c.isdigit() for c in stock_id]):
      continue # ignore special stock
    if stock_id in suspended:
      continue
    cb(stock_id)

_stock_count = 0
def accumulate(stock_id):
  global _stock_count
  _stock_count += 1
for_each_stock_id(accumulate)
  
def up_to_date(mod_name, date):
  # TODO: current implementation assumes that 'suspended' and 'stock_list' remain fixed
  # target module should take the same parameters as 'transactions' module
  assert type(date) is Date
  if not is_outdated(mod_name):
    return True

  global _stock_count
  todays_count = len(stocklab.evaluate(f'{mod_name}._.{date}'))
  assert not todays_count > _stock_count
  if todays_count == _stock_count:
    set_last_update_datetime(mod_name)
    return True
  else:
    return False

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
