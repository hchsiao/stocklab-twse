import stocklab
from stocklab.date import date_to_timestamp

class suspended(stocklab.MetaModule):
  spec = {
      'update_threshold': 1440,
      'ignore_existed': True,
      'crawler': 'TwseCrawler.suspended_listing',
      'args': [],
      'schema': {
        'stock_id': {'key': True},
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp},
        }
      }

  def run(self, args):
    return self.access_db(args)

  def check_update(self, db, last_args=None):
    if last_args is None:
      self.logger.info('Start suspended list update')
      return True, {}
    else:
      self.logger.info('End suspended list update')
      return False, {}

  def query_db(self, db, args):
    retval = db(db[self.name]).select()
    return retval, False, {}
