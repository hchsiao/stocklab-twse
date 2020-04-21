import stocklab
from stocklab.datetime import Date
from stocklab.lang import expr
import numpy as np

import logging
stocklab.change_log_level(logging.DEBUG)

def map_for_each_stock_id(cb):
  retval = []
  # TODO: metamodule active_stock_list
  # TODO: make this a transformer (mapper) built inside active_stock_list metamodule
  suspended = [row.stock_id for row in stocklab.metaevaluate('suspended')]
  stock_list = stocklab.metaevaluate(f'stock_list')
  for row in stock_list:
    stock_id = row.stock_id
    if not all([c.isdigit() for c in stock_id]):
      continue # ignore special stock
    if stock_id in suspended:
      continue
    retval.append(cb(stock_id))
  return retval

def map_selected(cb, S=[3698, 3034]):
  retval = []
  for sid in S:
    retval.append(cb(sid))
  return retval

def f(sid, date):
  TH = 5
  bsf = stocklab.evaluate(f'tendency.sell.{sid}.{date}.1')
  bsf = bsf[bsf > TH]
  def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
      return v
    return v / norm
  return normalize(bsf).var() if len(bsf) else 0.0

def map_dates(cb, date=20200401, days=2, mode='lag'):
  retval = []
  dates = stocklab.metaevaluate(f'valid_dates.{date}.{days}.{mode}')
  for d in dates:
    retval.append((d, cb(d)))
  return retval

ff = lambda d: lambda s: f(s, d)
fff = lambda d: map_selected(ff(d))

a = (map_dates(fff, days=10))
