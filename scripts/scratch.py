import numpy as np
import logging
import stocklab
from stocklab.datetime import Date
from stocklab.utils import *
#stocklab.change_log_level(logging.DEBUG)

date = stocklab.metaevaluate('nearest.20200424')
days = 100
stock_id = 3034

# plot it
dates_expr = f'trade_dates.{date}.{days}.lag'
dates = stocklab.metaevaluate(dates_expr)
ohlcs = np.asarray(stocklab.evaluate(f'ohlc.{stock_id}.(${dates_expr})'))

plot(dates, ohlcs,
    aux={
      'ma_l': stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).8'),
      'ma_s': stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).3')
      },
    top_aux={
      'rsi': stocklab.evaluate(f'rsi_array.{stock_id}.{date}.{days}.14'),
      'rsi_avg': convolve(stocklab.evaluate(f'rsi_array.{stock_id}.{date}.{days}.14'), n=9),
      }
    )
