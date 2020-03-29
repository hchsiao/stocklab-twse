import stocklab
from stocklab.datetime import Date, date_to_timestamp

class last_trade_date(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'update_existed': True,
      'crawler': 'TwseCrawler.last_trade_date',
      'args': [],
      'schema': {
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp},
        'dummy_id': {'key': True},
        }
      }

  def run(self, args):
    return Date(self.access_db(args)[0].date, tstmp=True)

  def check_update(self, db, last_args=None):
    if last_args is None:
      self.logger.info('Start refreshing last_trade_date list')
      return True, {}
    else:
      self.logger.info('End refreshing last_trade_date list')
      return False, {}

  def query_db(self, db, args):
    retval = db(db[self.name]).select()
    return retval, False, {}
