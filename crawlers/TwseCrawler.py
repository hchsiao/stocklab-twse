import requests
import cloudscraper # using its fake browser header utility
import json
import time
import re
from bs4 import BeautifulSoup
import bs4

import stocklab
from stocklab import set_state
from stocklab.datetime import Date
from stocklab.error import InvalidDateRequested, ParserError
from stocklab.crawler import SpeedLimiterMixin, RetryMixin

class TwseCrawler(stocklab.Crawler, SpeedLimiterMixin, RetryMixin):
  spec = {
      'max_speed': 0.39,
      'tick_period': 0.01,
      'retry_period': 5,
      'retry_limit': 3,
      }

  def __init__(self):
    super().__init__()
    self.sess = cloudscraper.create_scraper()

  def _request(self, url, method='get', data={}, mode='json', speed_limit=True):
    assert mode in ['json', 'plain']
    assert method in ['get', 'post']
    if 'get' == method:
      _req = self.sess.get
    else:
      _req = self.sess.post

    while True:
      try:
        self.logger.debug(url)
        if speed_limit:
          r = self.speed_limited_request(_req, url, data=data)
        else:
          r = _req(url, data=data)
        page = r.text
        if 'json' == mode:
          return json.loads(page) # may throw error
        else:
          return page
      except requests.exceptions.ConnectionError as e:
        if 'Connection aborted' in str(e):
          self.logger.error('Connection error, waiting for retry...')
          time.sleep(30)
          continue
        elif 'SSLError' in str(e):
          self.logger.error('Connection error(SSL), waiting for retry...')
          time.sleep(30)
        else:
          raise e
      except json.decoder.JSONDecodeError as e:
        if 'Expecting value' in str(e):
          self.logger.error('Too many requests? waiting for retry...')
          time.sleep(20*60)
          continue
        else:
          raise e

  def stock_day(self, date, stock_id):
    assert type(date) is Date
    date_s = str(date).replace('-', '')
    url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?'\
            + f'response=json&date={date_s}&stockNo={stock_id}'

    jsn = self.retry_when_failed(
        lambda: self._request(url),
        lambda _json: 'stat' in _json and 'fields' in _json \
            and _json['stat'] == 'OK' \
            and _json['fields'] == [
              '日期', '成交股數', '成交金額', '開盤價',
              '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數'],
        lambda _json: ParserError('bad response', {'res': _json})
        )
    
    # Parse
    data = jsn['data']
    def to_int(s):
      s = s.replace(',', '')
      return 0 if s == '' else int(s)
    
    def to_float(s):
      if '--' == s:
        return None
      s = s.replace(',', '')
      return 0 if s == '' else float(s)
    
    def transform(_date, _n_share, _p_share, _open, _max, \
                    _min, _close, _, _n_transac):
      return {
          'stock_id': stock_id,
          'date': Date(_date),
          'delta_n_share': to_int(_n_share),
          'delta_price_share': to_int(_p_share),
          'open': to_float(_open),
          'max': to_float(_max),
          'min': to_float(_min),
          'close': to_float(_close),
          'n_transactions': to_int(_n_transac)
          }

    retval = [transform(*cells) for cells in jsn['data']]
    if date not in [r['date'] for r in retval]:
      raise InvalidDateRequested('Please wait until the market close.'+
          + 'Make sure the date requested is not holiday.',
          {'date': date, 'stock_id': stock_id})
    return retval

  def dates(self, fetch_date):
    date_s = str(fetch_date).replace('-', '')
    url = 'https://www.twse.com.tw/exchangeReport/FMTQIK?'\
            + f'response=json&date={date_s}'
    jsn = self.retry_when_failed(
        lambda: self._request(url),
        lambda _json: 'stat' in _json and 'data' in _json\
            and _json['stat'] == 'OK',
        lambda _json: ParserError('bad response', {'res': _json})
        )
    return [{'date': Date(info[0])} for info in jsn['data']]

  def stock_codes(self, targets):
    retvals = []
    for type_id, type_name in targets:
      url = f'https://www.twse.com.tw/zh/api/codeFilters?filter={type_id}'
      stocks_jsn = self._request(url, speed_limit=False)
      s_list = stocks_jsn['resualt'] # resualt???
      _id = 0
      for s in s_list:
        stock_id, stock_name = s.split('\t')
        retvals.append({
          'type_id': type_id,
          'internal_id': _id,
          'stock_id': stock_id,
          'name': stock_name
          })
        _id += 1
    return retvals

  def stock_code_js(self):
    url = 'https://www.twse.com.tw/rsrc/js/stock-code.js'
    page = self._request(url, mode='plain', speed_limit=False)
    pattern = re.compile(r'\{(((?!(\{|\})).)*)\}')
    target = []
    for txt, _1, _2 in re.findall(pattern, page):
      if '證券' in txt and '其他' in txt:
        target.append(txt)
    assert len(target) == 1
    
    jsn_s = '{' + f'{target[0]}' + '}'
    # fix TWSE mistake
    jsn_s = jsn_s.replace('ETF', '"ETF"')
    jsn = json.loads(jsn_s)

    names = [name for name in jsn
        if 'http' not in jsn[name] \
            and '999' not in jsn[name]\
            and 'CB' not in jsn[name]\
            and '0049' not in jsn[name]\
            and '9299' not in jsn[name]\
            and '019919T' not in jsn[name]\
            and '0099P' not in jsn[name]\
            ]
    type_ids = [jsn[name] for name in names]

    return [{'type_id': type_id, 'name': name}
        for type_id, name in zip(type_ids, names)]

  def suspended_listing(self):
    url = 'https://www.twse.com.tw/zh/company/suspendListing'
    res = self._request(url, data={'selectYear': '', 'maxLength': '-1'}, \
        method='post', mode='plain')
    soup = BeautifulSoup(res, 'html.parser')
    tab = soup.find(class_='grid').tbody.contents
    retval = []
    for row in tab:
      if isinstance(row, bs4.element.Tag):
        if not row.contents[1].contents:
          continue # ignore TWSE erroneous data (with empty date)
        _date, _name, _sid = [e.contents[0] for e in row if isinstance(e, bs4.element.Tag)]
        _date = f'{_date[:3]}-{_date[4:6]}-{_date[7:9]}'
        retval.append({'stock_id': str(_sid), 'date': Date(_date)})
    return retval

  def etf_listing(self):
    url = 'https://www.twse.com.tw/zh/page/ETF/list.html'
    res = self._request(url, mode='plain')
    soup = BeautifulSoup(res, 'html.parser')
    tab = soup.find(class_='grid').tbody.contents
    retval = []
    for row in tab:
      if isinstance(row, bs4.element.Tag):
        _date, _sid, _name, _firm, _type = [e.contents[0] for e in row if isinstance(e, bs4.element.Tag)]
        retval.append({'stock_id': str(_sid), 'date': Date(_date)})
    return retval

  def _last_trade_date(self):
    url = 'https://mis.twse.com.tw/stock/data/mis_IDX.txt'
    res = self._request(url)
    date_str = res['msgArray'][0]['d']
    return Date(date_str)
