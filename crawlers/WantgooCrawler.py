import cloudscraper
import json
import time
import re

import stocklab
from stocklab.datetime import Date
from stocklab.error import NoLongerAvailable, ParserError
from stocklab.crawler import SpeedLimiterMixin, RetryMixin

# Assumption: 2330 (TSMC) will have transactions everyday

class WantgooCrawler(stocklab.Crawler, SpeedLimiterMixin, RetryMixin):
  spec = {
      'max_speed': 5.0,
      'tick_period': 0.01,
      'retry_period': 30,
      'retry_limit': 3,
      }
  DATA_VALID_DAYS = 30
  ROBUSTNESS = 2

  def __init__(self):
    super().__init__()
    self.scraper = cloudscraper.create_scraper()
    self._last_date = None

  def speed_limited_requests(self, url_list, *args, **kwargs):
    return [self.speed_limited_request(self.scraper.get, url,
      *args, **kwargs) for url in url_list]

  def _get_last_date(self):
    if self._last_date is None:
      ref_stock_id = '2330'
      url = f'https://www.wantgoo.com/stock/astock/agentstat?stockno={ref_stock_id}&type=3.5'
      resp = self.speed_limited_request(self.scraper.get, url)

      pat = r'var _EndDate = "([0-9]+)";'
      date_str = re.search(pat, resp.text).group(1)
      self._last_date = Date(date_str)
    return self._last_date # TODO: do not froze (once set) until session ends

  def brokers(self, stock_id, date):
    assert type(date) is Date
    date_s = str(date).replace('-', '')

    # Check date validity
    stocklab.metaevaluate(f'valid_dates.{date}.1.lag')
    date_lag = self._get_last_date() - date
    if date_lag > WantgooCrawler.DATA_VALID_DAYS or date_lag < 0:
      raise NoLongerAvailable('Requested date not available. Unless another source of data are found')

    data_url = f'https://www.wantgoo.com/stock/astock/agentstat_ajax?StockNo={stock_id}&Types=3.5&StartDate={date_s}&EndDate={date_s}&Rows=35'
    info_url = f'https://www.wantgoo.com/stock/astock/agentstat_total_ajax?StockNo={stock_id}&StartDate={date_s}&EndDate={date_s}&Rows=35'

    def crawl():
      # first crawl metadata of the stock
      def get_info():
        resps = self.speed_limited_requests([info_url] * WantgooCrawler.ROBUSTNESS)
        return [r.text for r in resps]

      info_resps = self.retry_when_failed(get_info,
          lambda resps: len(set(resps)) == 1,
          lambda resps: ParserError('bad response', {'res': resps})
          )
      info = json.loads(info_resps[0])
      assert info['code'] == '0', str(info)
      info = json.loads(info['returnValues'])

      # then crawl the data
      def get_data():
        resps = self.speed_limited_requests([data_url] * WantgooCrawler.ROBUSTNESS)
        return [r.text for r in resps]

      data_resps = self.retry_when_failed(get_data,
          lambda resps: len(set(resps)) == 1,
          lambda resps: ParserError('bad response', {'res': resps})
          )
      data = json.loads(data_resps[0])
      assert data['code'] == '0', str(data)
      data = json.loads(data['returnValues'])

      return info, data

    # if this keep failing, wantgoo may have changed their api
    info, data = self.retry_when_failed(crawl,
        lambda info_data: not info_data[0] or bool(info_data[1]),
        lambda resps: ParserError('bad response', {'res': resps})
        )

    if not info: # wantgoo returns empty list if the request is invalid
      return [{
        'stock_id': stock_id,
        'date': date,
        'broker_id': None,
        'buy_amt': None,
        'sell_amt': None,
        'buy_price': None,
        'sell_price': None,
        }]

    def to_int(s):
      f = to_float(s)
      i = int(f)
      assert f == float(i)
      return i
    
    def to_float(s):
      return float(s)

    def parse_name(s):
      return s.replace(' ', '').replace(')', '').split('(')[-1]
    
    def get_buyer(e):
      if not e['券商名稱']:
        return None
      else:
        retval = {
            'stock_id': stock_id,
            'date': date,
            'broker_id': parse_name(e['券商名稱']),
            'buy_amt': to_int(e['買量']),
            'sell_amt': to_int(e['賣量']),
            'buy_price': to_float(e['買價']),
            'sell_price': to_float(e['賣價']),
            }
      return retval
    
    def get_seller(e):
      if not e['券商名稱2']:
        return None
      else:
        retval = {
            'stock_id': stock_id,
            'date': date,
            'broker_id': parse_name(e['券商名稱2']),
            'buy_amt': to_int(e['買量2']),
            'sell_amt': to_int(e['賣量2']),
            'buy_price': to_float(e['買價2']),
            'sell_price': to_float(e['賣價2']),
            }
      return retval

    retval = []
    for e in data:
      b = get_buyer(e)
      s = get_seller(e)
      if b:
        retval.append(b)
      if s:
        retval.append(s)
      assert b or s

    # abnormality detector
    assert '2330' != stock_id or len(retval) > 50, 'abnormality detected'

    return retval
