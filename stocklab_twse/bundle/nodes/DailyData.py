from stocklab.node import *
from stocklab.crawler import CrawlerTrigger
from stocklab.core.runtime import TWSECrawler

from stocklab_twse.error import InvalidDateRequested
from stocklab_twse.utils.datetime import Date, date_to_timestamp

class DailyData(DataNode):
    crawler_entry = TWSECrawler.daily_data
    ignore_existed = True # API returns a month at once

    args = Args(
            stock = Arg(),
            date = Arg(type=Date),
            )

    schema = Schema(
            date = {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True},
            stock_id = {'key': True},
            delta_n_share = {'type': 'integer'},
            delta_price_share = {'type': 'integer'},
            open = {'type': 'double'},
            max = {'type': 'double'},
            min = {'type': 'double'},
            close = {'type': 'double'},
            n_transactions = {'type': 'integer'},
            )

    def evaluate(stock, date):
        table = DailyData.db[DailyData.name]
        query = table.stock_id == stock
        query &= table.date == date.timestamp()
        retval = DailyData.db(query).select(limitby=(0, 1))
        if retval:
            return {
                    'open': retval[0].open,
                    'max': retval[0].max,
                    'min': retval[0].min,
                    'close': retval[0].close,
                    'n_transactions': retval[0].n_transactions,
                    'delta_n_share': retval[0].delta_n_share,
                    'delta_price_share': retval[0].delta_price_share,
                    }
        else:
            raise CrawlerTrigger(date=date, stock=stock)
