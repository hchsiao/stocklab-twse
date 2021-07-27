import numpy as np

from stocklab.node import *
from stocklab.crawler import CrawlerTrigger
from stocklab.core.runtime import TWSECrawler

from stocklab_twse.error import InvalidDateRequested
from stocklab_twse.utils.datetime import Date, date_to_timestamp

class DateTrades(DataNode):
    TWSE_FIRST_DAY = Date('20100104')

    crawler_entry = TWSECrawler.dates
    ignore_existed = True

    args = Args(
            date = Arg(type=Date),
            )

    schema = Schema(
            date = {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True},
            trades = {'type': 'integer', 'pre_proc': int},
            )

    def evaluate(date):
        if date < DateTrades.TWSE_FIRST_DAY:
            raise InvalidDateRequested('Date requested eariler than' \
                    + 'the earliest day in TWSE DB', date)
        elif date > Date.today():
            raise InvalidDateRequested('Future date requested', date)

        db = DateTrades.db
        table = db[DateTrades.name]
        query = table.date == date.timestamp()
        retval = db(query).select(limitby=(0, 1))
        res = [(Date(r.date, tstmp=True), bool(r.trades)) for r in retval]

        if not res:
            raise CrawlerTrigger(fetch_date=date)
        else:
            return res[0][1]
