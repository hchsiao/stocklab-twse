import stocklab
from stocklab.datetime import Date
import numpy as np
import matplotlib.pyplot as plt
#import mpl_finance as mpf
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.ticker as ticker

import logging
stocklab.change_log_level(logging.DEBUG)

L, S = 10, 5

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

# Golden sign
#@stocklab.declare
#class sign(stocklab.Module):
#  spec = {
#      'args': [
#        'stock_id', # string
#        ('date', Date),
#        ]
#      }
#  def evaluate(self, args):
#    indices = stocklab.metaevaluate(f'trade_dates.{args.date}.2.lead')
#    paths = [f'twse.{args.stock_id}.{_date}.close' for _date in indices]
#    data = np.array([stocklab.evaluate(p) for p in paths])
#    buy = data[1] > data[0]
#    sell = data[1] < data[0]
#    return 1 if buy else -1 if sell else 0

# Moving-average crossing method
@stocklab.declare
class sign(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ]
      }
  def evaluate(self, args):
    indices = stocklab.metaevaluate(f'trade_dates.{args.date}.2.lag')
    ma_l = [stocklab.evaluate(f'myma.{args.stock_id}.{_date}.{L}')
        for _date in indices]
    ma_s = [stocklab.evaluate(f'myma.{args.stock_id}.{_date}.{S}')
        for _date in indices]
    ml = ma_l[1] - ma_l[0]
    ms = ma_s[1] - ma_s[0]
    cross = (ma_l[1] - ma_s[1]) * (ma_l[0] - ma_s[0]) <= 0
    bear = ml > ms
    bull = ml < ms
    return (0 if not cross else 1 if bull else -1 if bear else 0)

# Ont-stock simulator
@stocklab.declare
class simulate(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ('N', int),
        ('sell_th', float),
        ]
      }
  def sim(self, stock_id, dates, balance=0, cost=None, sell_th=None):
    assert len(dates) > 0
    date = dates[0]
    price = stocklab.evaluate(f'twse.{stock_id}.{date}.close')
    if len(dates) == 1:
      if cost:
        print(f'[{date}] sell (terminate) @ {price} (gain: {price-cost})')
        return balance + price
      else:
        return balance
    else:
      sign = stocklab.evaluate(f'sign.{stock_id}.{date}')
      if sell_th and cost and price - cost > sell_th:
        print(f'[{date}] sell (over threshold) @ {price} (gain: {price-cost})')
        return self.sim(stock_id, dates[1:], balance + price, None, sell_th)
      elif 1 == sign and not cost:
        print(f'[{date}] buy @ {price}')
        return self.sim(stock_id, dates[1:], balance - price, price, sell_th)
      elif -1 == sign and cost:
        print(f'[{date}] sell @ {price} (gain: {price-cost})')
        return self.sim(stock_id, dates[1:], balance + price, None, sell_th)
      else:
        return self.sim(stock_id, dates[1:], balance, cost, sell_th)
  def evaluate(self, args):
    dates = stocklab.metaevaluate(f'trade_dates.{args.date}.{args.N}.lead')
    signs = [stocklab.evaluate(f'sign.{args.stock_id}.{d}') for d in dates]
    print(signs)
    return self.sim(args.stock_id, dates, sell_th=args.sell_th)

from matplotlib.dates import date2num
from matplotlib.dates import MONDAY, DateFormatter, DayLocator, WeekdayLocator
mondays = WeekdayLocator(MONDAY)
alldays = DayLocator()
weekFormatter = DateFormatter('%F')

date = 20200424
days = 20
stock_id = 2330

LARGE_NUM = 5000

dates_expr = f'trade_dates.{date}.{days}.lag'
dates = np.array([date2num(d.datetime) for d in stocklab.metaevaluate(dates_expr)])

data = np.array(stocklab.evaluate(f'ohlc.{stock_id}.(${dates_expr})'))
quotes = np.hstack((dates[:,np.newaxis], data))

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_minor_locator(alldays)
ax.xaxis.set_major_formatter(weekFormatter)

candlestick_ohlc(ax, quotes,
    width=0.5, colorup='r', colordown='green', alpha=0.6)

ax.grid()
ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

ma = np.array(stocklab.evaluate(f'myma.{stock_id}.(${dates_expr}).{days}'))
ax.plot(ma, label='ma_l')
#ax.plot(data['ma_s'], label='ma_s')
ax.legend(loc='upper left')
def f(x, pos):
    try:
        return str(dates[int(round(x))])
    except IndexError:
        print(x)
        return ''

#def interleave(a, b):
#  retval = np.empty((len(a) + len(b),), dtype=a.dtype)
#  retval[0::2] = a
#  retval[1::2] = b
#  return retval
#
#int_idx = interleave(
#    np.arange(len(dates)) - 0.5,
#    np.arange(len(dates)) + 0.5
#    )
#bull_sign = data['sign'] == 1
#bear_sign = data['sign'] == -1
#ax.fill_between(int_idx, LARGE_NUM,
#        where=interleave(bull_sign, bull_sign),
#        facecolor='green', alpha=0.2)
#ax.fill_between(int_idx, LARGE_NUM,
#        where=interleave(bear_sign, bear_sign),
#        facecolor='red', alpha=0.2)
plt.show()
