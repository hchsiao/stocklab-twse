import stocklab
from stocklab.datetime import Date
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf
import matplotlib.ticker as ticker

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
  def run(self, args):
    # operations
    indices = stocklab.metaevaluate(f'trade_dates.{args.date}.{args.N}.lag')
    paths = [f'twse.{args.stock_id}.{_date}.close' for _date in indices]
    prices = np.array([stocklab.evaluate(p) for p in paths])

    return prices.mean()

# Golden sign
#@stocklab.declare
#class sign(stocklab.Module):
#  spec = {
#      'args': [
#        'stock_id', # string
#        ('date', Date),
#        ]
#      }
#  def run(self, args):
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
  def run(self, args):
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
  def run(self, args):
    dates = stocklab.metaevaluate(f'trade_dates.{args.date}.{args.N}.lead')
    signs = [stocklab.evaluate(f'sign.{args.stock_id}.{d}') for d in dates]
    print(signs)
    return self.sim(args.stock_id, dates, sell_th=args.sell_th)

@stocklab.declare
class plot(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('N', int),
        ]
      }
  def run(self, args):
    LARGE_NUM = 5000
    indices = stocklab.metaevaluate(f'trade_dates.{args.date}.{args.N}.lead')
    paths = {
            'open': [f'twse.{args.stock_id}.{_date}.open' for _date in indices],
            'close': [f'twse.{args.stock_id}.{_date}.close' for _date in indices],
            'high': [f'twse.{args.stock_id}.{_date}.max' for _date in indices],
            'low': [f'twse.{args.stock_id}.{_date}.min' for _date in indices],
            'volume': [f'twse.{args.stock_id}.{_date}.delta_price_share' for _date in indices],
            'ma_l': [f'myma.{args.stock_id}.{_date}.{L}' for _date in indices],
            'ma_s': [f'myma.{args.stock_id}.{_date}.{S}' for _date in indices],
            'sign': [f'sign.{args.stock_id}.{_date}' for _date in indices],
            }
    data = {
            'open': np.array([stocklab.evaluate(p) for p in paths['open']]),
            'close': np.array([stocklab.evaluate(p) for p in paths['close']]),
            'high': np.array([stocklab.evaluate(p) for p in paths['high']]),
            'low': np.array([stocklab.evaluate(p) for p in paths['low']]),
            'volume': np.array([stocklab.evaluate(p) for p in paths['volume']]),
            'ma_l': np.array([stocklab.evaluate(p) for p in paths['ma_l']]),
            'ma_s': np.array([stocklab.evaluate(p) for p in paths['ma_s']]),
            'sign': np.array([stocklab.evaluate(p) for p in paths['sign']]),
            }

    N_DATE_LABELS = 5
    ticks = np.linspace(0, len(indices), N_DATE_LABELS)
    ticks = np.unique(ticks.astype(int))
    ticks[-1] -= 1
    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 1)
    ax.grid()
    bx = fig.add_subplot(2, 1, 2)
    bx.grid()
    mpf.candlestick2_ochl(ax, data['open'], data['close'], data['high'], data['low'],width=0.5, colorup='r', colordown='green',alpha=0.6)
    bx.plot(data['volume'])
    ax.plot(data['ma_l'], label='ma_l')
    ax.plot(data['ma_s'], label='ma_s')
    ax.legend(loc='upper left')
    def f(x, pos):
        try:
            return str(indices[int(round(x))])
        except IndexError:
            print(x)
            return ''
    ax.set_xlim(-0.5, len(indices) - 0.5)
    ax.set_ylim(data['low'].min(), data['high'].max())
    bx.set_xlim(-0.5, len(indices) - 0.5)
    ax.set_xticks(np.unique(ticks))
    ax.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
    bx.set_xticks(np.unique(ticks))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(f))
    bx.xaxis.set_major_formatter(ticker.FuncFormatter(f))

    def interleave(a, b):
      retval = np.empty((len(a) + len(b),), dtype=a.dtype)
      retval[0::2] = a
      retval[1::2] = b
      return retval

    int_idx = interleave(
        np.arange(len(indices)) - 0.5,
        np.arange(len(indices)) + 0.5
        )
    bull_sign = data['sign'] == 1
    bear_sign = data['sign'] == -1
    ax.fill_between(int_idx, LARGE_NUM,
            where=interleave(bull_sign, bull_sign),
            facecolor='green', alpha=0.2)
    ax.fill_between(int_idx, LARGE_NUM,
            where=interleave(bear_sign, bear_sign),
            facecolor='red', alpha=0.2)
    print(data['sign'])
    #print(data['ma_l'])
    #print(data['ma_s'])
    plt.show()
    return data['sign']

import logging
#stocklab.change_log_level(logging.DEBUG)

res = stocklab.evaluate(f'simulate.2330.20191202.80._')
#res = stocklab.evaluate(f'plot.3034.20191202.50')
print(res)
#indices = stocklab.metaevaluate(f'trade_dates.20200120.20.lead')
#prices = [stocklab.evaluate(f'twse.2330.{d}.close') for d in indices]
#print({str(k):v for k, v in zip(indices, prices)})
