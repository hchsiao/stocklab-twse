import numpy as np

import stocklab
from stocklab.date import Date, date_to_timestamp
from stocklab.error import InvalidDateRequested

class valid_dates(stocklab.MetaModule):
  TWSE_FIRST_DAY = Date('20100104')
  spec = {
      'update_threshold': 1440,
      'ignore_existed': True,
      'crawler': 'TwseCrawler.dates',
      'args': [
        ('target_date', Date),
        ('N', int),
        ('phase_shift', ['lead', 'zero', 'lag']),
        ],
      'schema': {
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp, 'key': True}
        }
      }

  def run(self, args):
    if args.target_date < valid_dates.TWSE_FIRST_DAY:
      raise InvalidDateRequested('Date requested eariler than' \
          + 'the earliest day in TWSE DB', args.target_date)
    elif args.target_date > Date.today():
      raise InvalidDateRequested('Future date requested', args.target_date)
    return self.access_db(args)

  def query_db(self, db, args):
    table = db[self.name]
    date_field = table.date

    lagphase_sql = "SELECT date(date, 'unixepoch')\
        FROM valid_dates\
        WHERE date <= strftime('%s', ?)\
        ORDER BY date DESC\
        LIMIT ?;"
    query = date_field <= args.target_date.timestamp()
    db(query).select(orderby=~date_field)
    leadphase_sql = "SELECT date(date, 'unixepoch')\
        FROM valid_dates\
        WHERE date >= strftime('%s', ?)\
        ORDER BY date ASC\
        LIMIT ?;"
    zerophase_sql = "SELECT date(date, 'unixepoch')\
        FROM valid_dates\
        ORDER BY Abs(date - strftime('%s', ?)) ASC\
        LIMIT ?;"

    if 'zero' == args.phase_shift:
      assert args.N % 2 == 1
      select_sql = zerophase_sql
    elif 'lead' == args.phase_shift:
      select_sql = leadphase_sql
    else: # 'lag'
      select_sql = lagphase_sql
    dates = [r[0] for r in db.execute(select_sql, (str(args.target_date), args.N))]
    sorted_idx = np.argsort([int(Date(i)) for i in dates])
    dates = np.array(dates)[sorted_idx]
    return dates, False, {}

  def check_update(self, db, last_args=None):
    table = db[self.name]
    date_field = table.date
    db_max_str = db().select(date_field.max())[0][date_field.max()]
    db_min_str = db().select(date_field.min())[0][date_field.min()]

    if not db_max_str:
      fetch_date = valid_dates.TWSE_FIRST_DAY
    elif last_args is None:
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
        assert Date(db_min_str, tstmp=True) == valid_dates.TWSE_FIRST_DAY
      else:
        fetch_date = Date(f'{max_month}01').shift(1, 'month')

    need_update = fetch_date is not None
    return need_update, {'fetch_date': fetch_date}
