import numpy as np

import stocklab
from stocklab.datetime import Date, date_to_timestamp
from stocklab.error import InvalidDateRequested
from stocklab.crawler import CrawlerTrigger

# TODO: base type: stocklab.module.DateList
class trade_dates(stocklab.MetaModule):
  TWSE_FIRST_DAY = Date('20100104')
  spec = {
      'update_offset': (13, 40),
      'ignore_existed': True,
      'crawler_entry': 'TwseCrawler.dates',
      'args': [
        ('target_date', Date),
        ('N', int),
        ('phase_shift', ['lead', 'zero', 'lag']),
        ],
      'schema': {
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True}
        }
      }

  def evaluate(self, db, args):
    if args.target_date < trade_dates.TWSE_FIRST_DAY:
      raise InvalidDateRequested('Date requested eariler than' \
          + 'the earliest day in TWSE DB', args.target_date)
    elif args.target_date > Date.today():
      raise InvalidDateRequested('Future date requested', args.target_date)

    table = db[self.name]

    if 'zero' == args.phase_shift:
      assert args.N % 2 == 1
      half_N = int(args.N / 2) + 1
      query = table.date >= args.target_date.timestamp()
      lead = db(query).select(orderby=table.date, limitby=(0, half_N))
      query = table.date <= args.target_date.timestamp()
      lag = db(query).select(orderby=~table.date, limitby=(0, half_N))
      dates = [Date(r.date, tstmp=True) for r in lag] \
          + [Date(r.date, tstmp=True) for r in lead][1:]
    elif 'lead' == args.phase_shift:
      query = table.date >= args.target_date.timestamp()
      retval = db(query).select(orderby=table.date, limitby=(0, args.N))
      dates = [Date(r.date, tstmp=True) for r in retval]
    elif 'lag' == args.phase_shift: # 'lag'
      query = table.date <= args.target_date.timestamp()
      retval = db(query).select(orderby=~table.date, limitby=(0, args.N))
      dates = [Date(r.date, tstmp=True) for r in retval]
    sorted_idx = np.argsort([int(i) for i in dates])
    dates = np.asarray(dates)[sorted_idx].tolist()

    if len(dates) < args.N:
      raise InvalidDateRequested('date out-of-range', args)
    if args.target_date not in dates:
      raise InvalidDateRequested('Date requested is not weekday?', args.target_date)
    return dates

  def db_is_fresh(self, db, last_crawl):
    table = db[self.name]
    db_max_str = db().select(table.date.max())[0][table.date.max()]
    db_min_str = db().select(table.date.min())[0][table.date.min()]

    if not db_max_str:
      fetch_date = trade_dates.TWSE_FIRST_DAY
    elif last_crawl is None:
      max_date = Date(db_max_str, tstmp=True)
      max_month = int(int(max_date) / 100)
      fetch_date = Date(f'{max_month}01')
    else:
      max_date = Date(db_max_str, tstmp=True)
      max_month = int(int(max_date) / 100)
      this_month = int(int(Date.today()) / 100)
      if max_month == this_month:
        fetch_date = None
        self.logger.info('Update complete')
        assert Date(db_min_str, tstmp=True) == trade_dates.TWSE_FIRST_DAY
      else:
        fetch_date = Date(f'{max_month}01').shift(1, 'month')

    if fetch_date is not None:
      raise CrawlerTrigger(fetch_date=fetch_date)
