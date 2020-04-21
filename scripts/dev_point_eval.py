import stocklab
from stocklab.datetime import Date
from stocklab.lang import expr
import numpy as np

import logging
stocklab.change_log_level(logging.DEBUG)

sid = 3698
date = 20200401
days = 25 # n-consecutive points

# a simple bear golden
@stocklab.declare
class my_golden(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('days', int),
        ('th', int), # in percentage
        ('mode', ['bear', 'bull'])
        ]
      }
  def run(self, args):
    indices = stocklab.metaevaluate(f'valid_dates.{args.date}.{args.days}.lead')
    paths = [f'twse.{args.stock_id}.{_date}.close' for _date in indices]
    data = np.array([stocklab.evaluate(p) for p in paths])
    th = data[0] * (args.th / 100.0)
    if 'bear' == args.mode:
      return np.any(data < data[0] - th)
    else:
      return np.any(data > data[0] + th)

# the sign to test
@stocklab.declare
class my_score(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('days', int),
        ('force_th', int),
        ]
      }
  def run(self, args):
    def normalize(v):
      norm = np.linalg.norm(v)
      if norm == 0: 
        return v
      return v / norm
    bsf = stocklab.evaluate(f'tendency.sell.{args.stock_id}.{args.date}.{args.days}')
    bsf = bsf[bsf > args.force_th]
    def normalize(v):
      norm = np.linalg.norm(v)
      if norm == 0: 
        return v
      return v / norm
    bsf_var = normalize(bsf).var() if len(bsf) else 0.0
    return bsf_var*1000

@stocklab.declare
class my_score2(stocklab.Module):
  spec = {
      'args': [
        'stock_id', # string
        ('date', Date),
        ('days', int),
        ]
      }
  def run(self, args):
    def normalize(v):
      norm = np.linalg.norm(v)
      if norm == 0: 
        return v
      return v / norm
    buy = stocklab.evaluate(f'tendency.buy.{args.stock_id}.{args.date}.{args.days}')
    sell = stocklab.evaluate(f'tendency.sell.{args.stock_id}.{args.date}.{args.days}')
    return buy.sum(), sell.sum(), buy.sum() - sell.sum()

GAIN_TH = 3
GAIN_WITHIN = 3
FORCE_TH = 5
FORCE_DAYS = 2
SCORE_TH = 8

@stocklab.declare
class my_inspector(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ]
      }
  def run(self, args):
    g = expr.my_golden[args.stock_id][args.date][GAIN_WITHIN][GAIN_TH].bear
    score = expr.my_score[args.stock_id][args.date][FORCE_DAYS][FORCE_TH]
    score2 = expr.my_score2[args.stock_id][args.date][FORCE_DAYS]
    return score, score2, g

@stocklab.declare
class my_tester(stocklab.Module):
  spec = {
      'args': [
        'stock_id',
        ('date', Date),
        ]
      }
  def run(self, args):
    s1, s2, g = expr.my_inspector[args.stock_id][args.date]
    score = s1
    sign = score > SCORE_TH
    if not sign:
      return 0
    else:
      return 1 if g else -1

# only for exploration purpose
def map_dates(cb, mode='lag'):
  retval = []
  dates = stocklab.metaevaluate(f'valid_dates.{date}.{days}.{mode}')
  for d in dates:
    retval.append((d, cb(d)))
  return retval

#[print(row) for row in map_dates(lambda d: expr.my_tester[sid][d])]
[print(row) for row in map_dates(lambda d: expr.my_inspector[sid][d])]
