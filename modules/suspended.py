import stocklab

class suspended(stocklab.MetaModule):
  spec = {
      'update_threshold': 1440,
      'ignore_nonunique': True,
      'crawler': 'TwseCrawler.suspended_listing',
      'args': [],
      'schema': [
        ('stock_id text', '?', 'key'),
        ('date integer', "strftime('%s', ?)"),
        ]
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
    select_sql = "SELECT * FROM suspended;"
    query_res = [r for r in db.execute(select_sql)]
    return query_res, False, {}
