import stocklab
from stocklab.datetime import Date

class nearest(stocklab.MetaModule):
  spec = {
      'db_dependencies': ['trade_dates'],
      'args': [
        ('target_date', Date),
        ],
      }

  def evaluate(self, db, args):
    first_day = stocklab.get_module('trade_dates').TWSE_FIRST_DAY
    if args.target_date < first_day:
      raise InvalidDateRequested('Date requested eariler than' \
          + 'the earliest day in TWSE DB', args.target_date)
    elif args.target_date > Date.today():
      raise InvalidDateRequested('Future date requested', args.target_date)

    table = db['trade_dates']
    query = table.date <= args.target_date.timestamp()
    retval = db(query).select(orderby=~table.date, limitby=(0, 1))[0].date
    return Date(retval, tstmp=True)
