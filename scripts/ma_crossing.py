import numpy as np
import logging
import stocklab
from stocklab.datetime import Date
from stocklab.utils import simulate, plot, random_simulate
#stocklab.change_log_level(logging.DEBUG)

@stocklab.declare
class my_sign(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ]
      }
  def evaluate(self, db, args):
    dates_expr = f'trade_dates.{args.date}.2.lag'
    ma_l = stocklab.evaluate(f'moving_average.{args.stock_id}.(${dates_expr}).8')
    ma_s = stocklab.evaluate(f'moving_average.{args.stock_id}.(${dates_expr}).3')
    ml = ma_l[1] - ma_l[0]
    ms = ma_s[1] - ma_s[0]
    cross = (ma_l[1] - ma_s[1]) * (ma_l[0] - ma_s[0]) <= 0
    bear = ml > ms
    bull = ml < ms
    return (0 if not cross else 1 if bull else -1 if bear else 0)

date = 20200424
days = 50

# pick a stock randomly and simulate
rand_sim = random_simulate(date, days, verbose=True,
    dates_expr=lambda d, n: f'trade_dates.{d}.{n}.lag',
    ohlc_expr=lambda s, d: f'ohlc.{s}.{d}',
    sign_expr=lambda s, d: f'my_sign.{s}.{d}',
    #stocks_expr='stocks.1702'
    )
stock_id, gain = next(rand_sim)
print(f'stock_id: {stock_id}, gain: {gain:.3}')

# plot it
dates_expr = f'trade_dates.{date}.{days}.lag'
dates = stocklab.metaevaluate(dates_expr)
ohlcs = np.asarray(stocklab.evaluate(f'ohlc.{stock_id}.(${dates_expr})'))
prices = ohlcs[:,3]
signs = stocklab.evaluate(f'my_sign.{stock_id}.(${dates_expr})')

plot(dates, ohlcs, signs,
    aux={
      'ma_l': stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).8'),
      'ma_s': stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).3')
      },
    top_aux={
      'volumn': stocklab.evaluate(f'volumn.{stock_id}.(${dates_expr})'),
      }
    )
