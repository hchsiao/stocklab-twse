import stocklab
from stocklab.datetime import Date

import numpy as np
import pandas as pd
import mplfinance as mpf

import logging
stocklab.change_log_level(logging.DEBUG)

date = 20200424
days = 100
stock_id = 2330

@stocklab.declare
class myma(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('N', int),
        ]
      }
  def evaluate(self, db, args):
    data = np.array(stocklab.evaluate(
      f'ohlc.{args.stock_id}.($trade_dates.{args.date}.{args.N}.lag)'
      ))
    return data[:,3].mean()

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
    ma_l = stocklab.evaluate(f'myma.{args.stock_id}.(${dates_expr}).24')
    ma_s = stocklab.evaluate(f'myma.{args.stock_id}.(${dates_expr}).6')
    ml = ma_l[1] - ma_l[0]
    ms = ma_s[1] - ma_s[0]
    cross = (ma_l[1] - ma_s[1]) * (ma_l[0] - ma_s[0]) <= 0
    bear = ml > ms
    bull = ml < ms
    return (0 if not cross else 1 if bull else -1 if bear else 0)

from matplotlib.dates import date2num
from matplotlib.dates import MONDAY, DateFormatter, DayLocator, WeekdayLocator
mondays = WeekdayLocator(MONDAY)
alldays = DayLocator()
weekFormatter = DateFormatter('%F')

dates_expr = f'trade_dates.{date}.{days}.lag'
dates = stocklab.metaevaluate(dates_expr)
dates = [pd.to_datetime(str(d)) for d in dates]

data = np.array(stocklab.evaluate(f'ohlc.{stock_id}.(${dates_expr})'))
columns = ['Open', 'High', 'Low', 'Close']
df = pd.DataFrame(data, columns=columns, index=dates)

mal = pd.DataFrame(stocklab.evaluate(f'myma.{stock_id}.(${dates_expr}).24'), index=dates)
mas = pd.DataFrame(stocklab.evaluate(f'myma.{stock_id}.(${dates_expr}).6'), index=dates)
sig = np.array(stocklab.evaluate(f'sign.{stock_id}.(${dates_expr})'))
bull_sign = mal.copy()
bull_sign[1 != sig] = np.nan
bear_sign = mal.copy()
bear_sign[-1 != sig] = np.nan
aux_plts = [
    mpf.make_addplot(mal),
    mpf.make_addplot(mas),
    mpf.make_addplot(bull_sign,scatter=True,markersize=100,marker='^'),
    mpf.make_addplot(bear_sign,scatter=True,markersize=100,marker='v')
    ]
mpf.plot(df, type='candle', style='mike', figscale=0.7, addplot=aux_plts)
