"""TODO: refactor this entire file."""
import math
import copy
import functools
import time
from datetime import datetime, timedelta
from datetime import date as dt_date
from dateutil.relativedelta import relativedelta
import calendar

from stocklab.core.config import get_config

def datetime_to_timestamp(dt):
  return int(calendar.timegm(dt.timetuple()))

def now():
  _offset = timedelta(seconds=time.timezone)
  return datetime.now() + _offset + \
          timedelta(hours=get_config('timezone_offset', may_not_exist=False))

@functools.total_ordering
class Date:
  def today():
    cfg_today = get_config('today_is')
    if cfg_today is not None:
      return Date(cfg_today)
    else:
      dt = now()
      return Date(f'{dt.year:04}-{dt.month:02}-{dt.day:02}')

  def __init__(self, date, tstmp=False):
    if isinstance(date, Date):
      self.yyyy = date.yyyy
      self.mm = date.mm
      self.dd = date.dd
    else:
      if tstmp:
        if type(date) is str:
          date = int(date)
        date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')
      if type(date) is int or type(date) is dt_date:
        date = str(date)
      if '-' in date or '/' in date:
        y, m, d = date.split('-') if '-' in date else date.split('/')
        assert len(y) == 3 or len(y) == 4 # taiwanese or western year
        y = int(y) if len(y) == 4 else int(y) + 1911
        _date = str(y) + m.zfill(2) + d.zfill(2)
      else:
        _date = date
      assert len(_date) == 8, f"Cannot convert '{date}' to Date object"
      self.yyyy = int(_date[:4])
      self.mm = int(_date[4:6])
      self.dd = int(_date[6:8])
    self.datetime = datetime(self.yyyy, self.mm, self.dd)

  def month_1st(self):
    tmp = copy.copy(self)
    tmp.dd = 1
    tmp.datetime = datetime(self.yyyy, self.mm, tmp.dd)
    return tmp

  def date(self):
    return self.datetime.date()

  def shift(self, amt, unit='day'):
    if 'year' == unit:
      delta = relativedelta(years=abs(amt))
    elif 'month' == unit:
      delta = relativedelta(months=abs(amt))
    else:
      delta = relativedelta(days=abs(amt))
    result = copy.copy(self)
    if amt < 0:
      result.datetime = self.datetime - delta
    else:
      result.datetime = self.datetime + delta
    result.yyyy = result.datetime.year
    result.mm = result.datetime.month
    result.dd = result.datetime.day
    return result

  def timestamp(self):
    return datetime_to_timestamp(self.datetime)

  def __str__(self):
    return self.datetime.strftime('%Y-%m-%d')

  def __repr__(self):
    return self.datetime.strftime('%Y-%m-%d')

  def __int__(self):
    return int(self.datetime.strftime('%Y%m%d'))

  def __eq__(self, other):
    assert type(other) is Date
    return int(self) == int(other)

  def __lt__(self, other):
    return int(self) < int(other)

  def __sub__(self, other):
    return (self.datetime - other.datetime).days

def date_to_timestamp(date):
  assert type(date) is Date
  return date.timestamp()

def in_time_window(dt, offset=0, period=(1, 0, 0)):
  if type(period) is tuple:
    assert len(period) == 3
    d, h, m = period
    period = 60*(d*24*60 + h*60 + m)
  if type(offset) is tuple:
    assert len(offset) == 2
    h, m = offset
    offset = h*60 + m
  if type(offset) is int:
    offset = timedelta(minutes=offset)
  
  _norm = lambda _dt: datetime_to_timestamp(_dt - offset) / period
  curr_dt = now()
  return _norm(curr_dt) < math.ceil(_norm(dt))
