import requests
import json
from bs4 import BeautifulSoup
import bs4
from datetime import datetime

import stocklab
import stocklab.states
from stocklab.date import Date, datetime_to_timestamp
from stocklab.error import NoLongerAvailable

SRC = 'pchome' # TODO: cnyes has updated their website

class TransactionCrawler(stocklab.Crawler):
  def __init__(self):
    super().__init__()
    if 'cnyes' == SRC:
      self._trans = self._cnyes
    elif 'pchome' == SRC:
      self._trans = self._pchome
    else:
      assert False, f'Data source not supported'

  def _pchome(self, stock_id):
    url = f'http://stock.pchome.com.tw/stock/sto0/ock3/sid{stock_id}.html'
    self.logger.info(f'loading: {url}')
    # TODO: detect and retry when timeout
    r = requests.post(url, data={'is_check': '1'})
    page = r.text

    not_found = '查無此股票代號' in page
    if not_found:
      self.logger.info(f'no transaction record found')
      exit()
    
    soup = BeautifulSoup(r.content, 'html5lib') # use html5lib to cope with the crappy html
    assert soup.find(id='tb_chart') is not None # TODO will fail when timed out
    tab = soup.find(id="tb_chart").contents[0].contents
    retval = []
    for row in tab:
      def f(col):
        cell = col
        while isinstance(cell, bs4.element.Tag):
          cell = cell.contents[0]
        return cell
      values = [f(col) for col in row]
      if not values[0] == '時間':
        time_str, buy, sell, deal, _, vol = values[:6]
        retval.append((time_str, buy, sell, deal, vol))
    return retval

  def _cnyes(self, stock_id):
    r = requests.get(f'https://traderoom.cnyes.com/tse/quote2FB_HTML5.aspx?code={stock_id}')
    
    soup = BeautifulSoup(r.content, 'html.parser')
    tab = soup.find(id="real_1").div.div.table.contents
    retval = []
    for row in tab:
      values = [col.contents[0] for col in row]
      if not values[0] == '時間':
        time_str, sell, buy, deal, _, vol = values
        retval.append((time_str, buy, sell, deal, vol))
    return retval

  def parser(self, stock_id, date):
    # Check date validity (TODAY will be valid after the market closed)
    stocklab.metaevaluate(f'valid_dates.{date}.1.lag')
    # Check the date requested matches data on the website
    trade_date = Date(stocklab.states.get('d_last_trade'), tstmp=True)
    if date != trade_date:
      raise NoLongerAvailable('Requested date not available. Unless another source of data are found')

    retval = self._trans(stock_id)

    def f(s):
      if '--' == s:
        return None
      return 0 if s == '' else float(s)
    def t(s):
      assert len(s.split(':')) == 3
      dt = datetime.strptime(f'1970-01-01 {s}', '%Y-%m-%d %H:%M:%S')
      return datetime_to_timestamp(dt)
    result = []
    for time_str, buy, sell, deal, vol in retval:
      curr_t = t(time_str)
      result.append({
        'stock_id': stock_id,
        'date': trade_date,
        'time': curr_t,
        'buy': f(buy),
        'sell': f(sell),
        'deal': f(deal),
        'volume': int(vol)
        })
    if not result:
      result.append({
        'stock_id': stock_id,
        'date': trade_date,
        'time': None,
        'buy': None,
        'sell': None,
        'deal': None,
        'volume': None
        })
    return result
