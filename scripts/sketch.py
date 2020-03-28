import stocklab
from stocklab.datetime import Date
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf
import matplotlib.ticker as ticker

@stocklab.declare
class bull(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ]
      }
  def run(self, args):
    indices = stocklab.metaevaluate(f'valid_dates.{args.date}.2.lag')
    paths = [f'myma.{args.stock_id}.{_date}.40' for _date in indices]
    data = np.array([stocklab.evaluate(p) for p in paths])

    k = 0.25
    return data[1] - data[0] > k

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
    indices = stocklab.metaevaluate(f'valid_dates.{args.date}.{args.N}.lag')
    paths = {
            'open': [f'twse.{args.stock_id}.{_date}.open' for _date in indices],
            'close': [f'twse.{args.stock_id}.{_date}.close' for _date in indices],
            'high': [f'twse.{args.stock_id}.{_date}.max' for _date in indices],
            'low': [f'twse.{args.stock_id}.{_date}.min' for _date in indices],
            'volume': [f'twse.{args.stock_id}.{_date}.delta_price_share' for _date in indices],
            'ma': [f'myma.{args.stock_id}.{_date}.7' for _date in indices],
            'bull': [f'bull.{args.stock_id}.{_date}' for _date in indices],
            }
    data = {
            'open': np.array([stocklab.evaluate(p) for p in paths['open']]),
            'close': np.array([stocklab.evaluate(p) for p in paths['close']]),
            'high': np.array([stocklab.evaluate(p) for p in paths['high']]),
            'low': np.array([stocklab.evaluate(p) for p in paths['low']]),
            'volume': np.array([stocklab.evaluate(p) for p in paths['volume']]),
            'ma': np.array([stocklab.evaluate(p) for p in paths['ma']]),
            'bull': np.array([stocklab.evaluate(p) for p in paths['bull']]),
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
    ax.plot(data['ma'], label='test')
    ax.legend(loc='upper left')
    def f(x, pos):
        try:
            return indices[int(round(x))]
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
    ax.fill_between(indices, LARGE_NUM, where=data['bull'],
            facecolor='green', alpha=0.2)
    plt.show()
    return data['bull']

import logging
stocklab.change_log_level(logging.DEBUG)
#res = stocklab.evaluate('valid_dates.20200110.1.lag')
res = stocklab.evaluate('transactions.2330.20200214')
print(res)
exit()
from stocklab.sampling import rand_stock, rand_date
#print(rand_stock(['24', '13']))
#print(rand_date(20130911, 20150111, 3))
from stocklab.simulate import simulate
#print(simulate(20130911, 5, '3034'))
