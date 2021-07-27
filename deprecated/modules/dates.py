import stocklab
from stocklab.datetime import Date

class dates(stocklab.MetaModule):
  spec = {
      'args': ['dates_str'],
      }

  def evaluate(self, db, args):
    return [Date(d) for d in args.dates_str.split('|')]
