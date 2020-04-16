import stocklab

class stock_list(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'ignore_existed': True,
      'crawler': 'TwseCrawler.stock_list',
      'args': [],
      'schema': {
        'stock_id': {'key': True},
        'name': {},
        }
      }

  def run(self, args):
    return self.access_db(args)

  def check_update(self, db, last_args=None):
    if last_args is None:
      self.logger.info('Start updating stock list')
      return True, {}
    else:
      self.logger.info('End updating stock list')
      return False, {}

  def query_db(self, db, args):
    retval = db(db[self.name]).select()
    return retval, False, {}
