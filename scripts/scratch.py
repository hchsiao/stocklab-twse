import numpy as np
import logging
import stocklab
from stocklab.datetime import Date
from stocklab.utils import simulate, plot
stocklab.change_log_level(logging.DEBUG)

@stocklab.declare
class sign(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ]
      }
  def evaluate(self, db, args):
    dates_expr = f'trade_dates.{args.date}.2.lag'
    ma_l = stocklab.evaluate(f'moving_average.{args.stock_id}.(${dates_expr}).24')
    ma_s = stocklab.evaluate(f'moving_average.{args.stock_id}.(${dates_expr}).6')
    ml = ma_l[1] - ma_l[0]
    ms = ma_s[1] - ma_s[0]
    cross = (ma_l[1] - ma_s[1]) * (ma_l[0] - ma_s[0]) <= 0
    bear = ml > ms
    bull = ml < ms
    return (0 if not cross else 1 if bull else -1 if bear else 0)

date = 20200424
days = 50
stock_id = 2330

dates_expr = f'trade_dates.{date}.{days}.lag'
dates = stocklab.metaevaluate(dates_expr)
ohlcs = np.array(stocklab.evaluate(f'ohlc.{stock_id}.(${dates_expr})'))
prices = ohlcs[:,3]
signs = stocklab.evaluate(f'sign.{stock_id}.(${dates_expr})')

simulate(dates, signs, prices)
plot(dates, ohlcs, signs,
    aux={
      'ma_l': stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).24'),
      'ma_s': stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).6')
      },
    top_aux={
      'volumn': stocklab.evaluate(f'volumn.{stock_id}.(${dates_expr})'),
      }
    )
