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

ma_l = np.asarray(stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).8'))
ma_s = np.asarray(stocklab.evaluate(f'moving_average.{stock_id}.(${dates_expr}).3'))

plot(dates, ohlcs,
    aux={
      'ma_l': ma_l,
      'ma_s': ma_s
      },
    top_aux={
      'macd': ma_l - ma_s
      }
    )
