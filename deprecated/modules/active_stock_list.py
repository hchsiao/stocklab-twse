import stocklab
import stocklab.module

class active_stock_list(stocklab.module.StockList):
  spec = {
      'args': [],
      }

  def evaluate(self, db, args):
    all_stocks = [r.stock_id
        for r in stocklab.metaevaluate('stock_list')
        if all([c.isdigit() for c in r.stock_id])] # special stocks does not count
    suspended_stocks = [r.stock_id
        for r in stocklab.metaevaluate('suspended_stock_list')]
    return set(all_stocks) - set(suspended_stocks)
