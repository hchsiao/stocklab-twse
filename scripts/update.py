import logging
import stocklab
from stocklab.date import Date
from stocklab.error import NoLongerAvailable

stocklab.change_log_level(logging.DEBUG)

def _crawl(stock_id):
  date = Date.today()
  stocklab.evaluate(f'transactions.{stock_id}.{date}')
  stocklab.evaluate(f'twse.{stock_id}.{date}.open')
  stocklab.evaluate(f'broker_deals.{stock_id}.{date}')

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

def check_update(mod_name, date):
  # TODO: handle table-not-exist
  assert type(date) is Date
  def _cb(stock_id):
    stocklab.evaluate(f'{mod_name}.{stock_id}.{date}')

  state_key = f'{mod_name}__db_latest_date'
  state = stocklab.get_state(state_key)
  if state:
    db_date = Date(state, tstmp=True)
    if db_date >= date:
      return True

  stocklab.force_offline = True
  try:
    for_each_stock_id(_cb)
  except NoLongerAvailable as e:
    return False

  stocklab.set_state(state_key, str(date.timestamp()))
  return True

volatile_modules = ['transactions', 'broker_deals']
#for_each_stock_id(_crawl)
