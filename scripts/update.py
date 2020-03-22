import logging
import stocklab

stocklab.change_log_level(logging.DEBUG)

def _crawl(stock_id):
  date = '20200318'
  #stocklab.evaluate(f'transactions.{stock_id}.{date}')
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

for_each_stock_id(_crawl)
