import cloudscraper
import json
import time
import re

import stocklab
from stocklab.date import Date
from stocklab.error import NoLongerAvailable, ParserError

# Assumption: 2330 will have transactions everyday

class WantgooCrawler(stocklab.Crawler):
  MAX_SPEED = 0.8 # TODO: investigate its limit
  TICK = 0.01
  DATA_VALID_DAYS = 30
  RETRY_LMT = 3
  ROBUSTNESS = 2

  def __init__(self):
    super().__init__()
    self.scraper = cloudscraper.create_scraper()
    self.reset()
    self._last_date = None

  def reset(self):
    self.last_req = None

  def speed(self):
    if self.last_req is None:
      return 0.0
    now = time.time()
    return 1.0 / (now - self.last_req)

  def speed_limited_req(self, url_list, *args, **kwargs):
    speed = self.speed()
    while self.speed() > WantgooCrawler.MAX_SPEED:
      time.sleep(WantgooCrawler.TICK)
      speed = self.speed()
    retval = [self.scraper.get(url, *args, **kwargs) for url in url_list]
    self.logger.debug(f'Request sent, speed={speed}')
    self.last_req = time.time()
    return retval

  def _get_last_date(self):
    if self._last_date is None:
      ref_stock_id = '2330'
      url = f'https://www.wantgoo.com/stock/astock/agentstat?stockno={ref_stock_id}&type=3.5'
      resp = self.speed_limited_req([url])[0]

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

    for nth_try in range(WantgooCrawler.RETRY_LMT + 1):
      # retry if got different resp. w/ the same url
      resps = self.speed_limited_req([info_url] * WantgooCrawler.ROBUSTNESS)
      info_resps = [r.text for r in resps]
      if len(set(info_resps)) == 1:
        info = json.loads(info_resps[0])
        assert info['code'] == '0', str(info)
        break
      if nth_try == WantgooCrawler.RETRY_LMT:
        raise ParserError('bad response', {'res': info_resps})

    for nth_try in range(WantgooCrawler.RETRY_LMT + 1):
      # retry if got different resp. w/ the same url
      resps = self.speed_limited_req([data_url] * WantgooCrawler.ROBUSTNESS)
      data_resps = [r.text for r in resps]
      if len(set(data_resps)) == 1:
        data = json.loads(data_resps[0])
        assert data['code'] == '0', str(data)
        break
      if nth_try == WantgooCrawler.RETRY_LMT:
        raise ParserError('bad response', {'res': data_resps})

    info = json.loads(info['returnValues'])
    data = json.loads(data['returnValues'])

    if not info: # wantgoo returns empty list if the request is invalid
      return [(
            stock_id,
            str(date),
            None,
            None,
            None,
            None,
            None,
          )]
    # TODO: wait longer and retry (perhaps ROBUSTNESS can be 1)
    assert data, str((info, data)) # if this failed, wantgoo may have changed their api

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
    return retval