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
    def dates(fetch_date):
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
