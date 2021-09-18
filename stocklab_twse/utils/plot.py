from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import date2num, num2date, DateFormatter
from mplfinance.original_flavor import candlestick_ohlc

LARGE_NUM = 5000

def plot(dates, ohlc, signs=None, aux={}, top_aux={}, side_aux={}, show_non_trading=False):
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    plt.style.use('dark_background')

    fig = plt.figure()
    fig.set_figwidth(13)
    fig.set_figheight(6)
    gs = fig.add_gridspec(3, 3)
    assert not side_aux, 'Not implemented yet' # TODO

    if top_aux:
        ax = fig.add_subplot(gs[1:, :])
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        axt = fig.add_subplot(gs[0, :], sharex=ax)
        plt.setp(plt.gca().get_xticklabels(), color='w')
    else:
        ax = fig.add_subplot(gs[:, :])
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        axt = None

    ax.set_ylim(ohlc[:,2].min(), ohlc[:,1].max())
    ax.autoscale_view()
    
    if show_non_trading:
        ax.xaxis.set_major_formatter(DateFormatter('%F'))
        ax.xaxis_date()
        idxs = np.asarray([date2num(d.datetime) for d in dates])
    else:
        def f(x, pos):
            try:
                return str(dates[int(round(x))])
            except IndexError:
                return ''
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(f))
        idxs = np.arange(len(dates))

    ohlc = np.asarray(ohlc)

    candlestick_ohlc(ax, np.hstack((idxs[:,np.newaxis], ohlc)),
            width=0.5, colorup='r', colordown='green', alpha=0.6)

    for k, v in top_aux.items():
        v = np.asarray(v)
        axt.plot(idxs, v, label=k, drawstyle='steps-post')
    if aux and axt:
        axt.legend(loc='upper left')

    for k, v in aux.items():
        v = np.asarray(v)
        ax.plot(idxs, v, label=k, drawstyle='steps-post')
    if aux:
        ax.legend(loc='upper left')
    
    def interleave(a, b):
        retval = np.empty((len(a) + len(b),), dtype=a.dtype)
        retval[0::2] = a
        retval[1::2] = b
        return retval
    
    if signs is not None:
        signs = np.asarray(signs)
        int_idx = interleave(
                idxs,
                idxs + 1
                )
        bull_sign = signs > 0
        bear_sign = signs < 0
        ax.fill_between(int_idx, LARGE_NUM,
                        where=interleave(bull_sign, bull_sign),
                        facecolor='red', alpha=0.2)
        ax.fill_between(int_idx, LARGE_NUM,
                        where=interleave(bear_sign, bear_sign),
                        facecolor='green', alpha=0.2)

    plt.show()
