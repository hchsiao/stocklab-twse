import stocklab
from stocklab.datetime import Date

class stock_brokers(stocklab.Module):
  spec = {
      'db_dependencies': ['broker_deals'],
      'args': [
        'stock_id',
        'broker_id',
        ('date', Date),
        ('n_days', int),
        ],
      }

  def evaluate(self, db, args):
    dates = stocklab.metaevaluate(f'trade_dates.{args.date}.{args.n_days}.lag')
    [stocklab.peek(f'broker_deals.{args.stock_id}.{d}') for d in dates]

    table = db['broker_deals']
    query = table.stock_id == args.stock_id
    query &= table.date >= dates[0].timestamp()
    query &= table.date <= dates[-1].timestamp()
    query &= table.broker_id != None # ignore no-trade indicator
    if args.broker_id is not None:
      query &= table.broker_id == args.broker_id
    rows = db(query).select()
    retval = {}
    for r in rows:
      if r.broker_id not in retval:
        retval[r.broker_id] = {
            'buy_amt': r['buy_amt'],
            'sell_amt': r['sell_amt'],
            'buy_price': r['buy_price'],
            'sell_price': r['sell_price']
            }
      else:
        old = retval[r.broker_id]
        if r.buy_amt + old['buy_amt'] > 0:
          old['buy_price'] = (r.buy_price * r.buy_amt + old['buy_price'] * old['buy_amt']) / (r.buy_amt + old['buy_amt'])
          old['buy_amt'] += r.buy_amt
        if r.sell_amt + old['sell_amt'] > 0:
          old['sell_price'] = (r.sell_price * r.sell_amt + old['sell_price'] * old['sell_amt']) / (r.sell_amt + old['sell_amt'])
          old['sell_amt'] += r.sell_amt
    return retval
