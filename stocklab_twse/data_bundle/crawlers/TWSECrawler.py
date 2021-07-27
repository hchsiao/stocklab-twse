import re
import json
import time

from requests.exceptions import ConnectionError
import cloudscraper # using its fake browser header utility
from bs4 import BeautifulSoup
import bs4

from stocklab import DataIdentifier as DI
from stocklab.crawler import *

from stocklab_twse.utils.datetime import Date
from stocklab_twse.error import InvalidDateRequested, ParserError

class TWSECrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.sess = cloudscraper.create_scraper()

    @speed_limiter(max_speed=0.39)
    def _request(url, method='get', data={}, mode='json'):
        assert mode in ['json', 'plain']
        assert method in ['get', 'post']
        if 'get' == method:
            _req = TWSECrawler.sess.get
        else:
            _req = TWSECrawler.sess.post

        while True:
            try:
                TWSECrawler.logger.debug(url)
                r = _req(url, data=data)
                page = r.text
                if 'json' == mode:
                    return json.loads(page) # may throw error
                else:
                    return page
            except ConnectionError as e:
                if 'Connection aborted' in str(e):
                    TWSECrawler.logger.error('Connection error, waiting for retry...')
                    time.sleep(30) # TODO: use retry_helper to help this mess
                    continue
                elif 'SSLError' in str(e):
                    TWSECrawler.logger.error('Connection error(SSL), waiting for retry...')
                    time.sleep(30)
                else:
                    raise e
            except json.decoder.JSONDecodeError as e:
                if 'Expecting value' in str(e):
                    TWSECrawler.logger.error('Too many requests? waiting for retry...')
                    time.sleep(20*60)
                    continue
                else:
                    raise e

    @retry_helper(max_retry=3, interval=3, retry_on=(ParserError,))
    def date_trades(fetch_date):
        date_s = str(fetch_date).replace('-', '')
        url = 'https://www.twse.com.tw/exchangeReport/FMTQIK?'\
                        + f'response=json&date={date_s}'
        jsn = TWSECrawler._request(url)
        golden = 'stat' in jsn and 'data' in jsn and jsn['stat'] == 'OK'
        if not golden:
            raise ParserError('bad response', {'res': jsn})
        trade_days = [Date(info[0]) for info in jsn['data']]

        m1st = fetch_date.month_1st()
        days = [m1st.shift(d) for d in range(31) \
                if m1st.shift(d).mm == m1st.mm]
        retval = [{'date': d, 'trades': d in trade_days} for d in days]
        return retval

    @retry_helper(max_retry=3, interval=3, retry_on=(ParserError,))
    def daily_data(date, stock):
        assert DI('DateTrades')(date=date)

        date_s = str(date).replace('-', '')
        url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?'\
                        + f'response=json&date={date_s}&stockNo={stock}'

        jsn = TWSECrawler._request(url)
        golden = 'stat' in jsn and 'fields' in jsn \
                and jsn['stat'] == 'OK' \
                and jsn['fields'] == [
                    '日期', '成交股數', '成交金額', '開盤價',
                    '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']
        if not golden:
            raise ParserError('bad response', {'res': jsn})
        
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
                    'stock_id': stock,
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
                    {'date': date, 'stock_id': stock})
        return retval

    """ ======================= Non-node crawlers ======================= """

    def stock_list():
        targets = [t['type_id'] for t in TWSECrawler.stock_types()]
        stock_map = {}
        for type_id in targets:
            url = f'https://www.twse.com.tw/zh/api/codeFilters?filter={type_id}'
            stocks_jsn = TWSECrawler._request(url, speed_limit=False)
            s_list = stocks_jsn['resualt'] # resualt???
            for s in s_list:
                stock_id, stock_name = s.split('\t')
                stock_map[stock_id] = stock_name
        retval = [{'stock_id': sid, 'name': stock_map[sid]} for sid in stock_map.keys()]
        return retval

    def stock_types():
        url = 'https://www.twse.com.tw/rsrc/js/stock-code.js'
        page = TWSECrawler._request(url, mode='plain', speed_limit=False)
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

    def suspended_listing():
        url = 'https://www.twse.com.tw/zh/company/suspendListing'
        res = TWSECrawler._request(url, data={'selectYear': '', 'maxLength': '-1'}, \
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

    def etf_listing():
        url = 'https://www.twse.com.tw/zh/page/ETF/list.html'
        res = TWSECrawler._request(url, mode='plain')
        soup = BeautifulSoup(res, 'html.parser')
        tab = soup.find(class_='grid').tbody.contents
        retval = []
        for row in tab:
            if isinstance(row, bs4.element.Tag):
                _date, _sid, _name, _firm, _type = [e.contents[0] for e in row if isinstance(e, bs4.element.Tag)]
                retval.append({'stock_id': str(_sid), 'date': Date(_date)})
        return retval

    def last_trade_date():
        url = 'https://mis.twse.com.tw/stock/data/mis_IDX.txt'
        res = TWSECrawler._request(url)
        date_str = res['msgArray'][0]['d']
        return Date(date_str)
