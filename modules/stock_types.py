import stocklab

class stock_types(stocklab.MetaModule):
  spec = {
      'update_threshold': 1440,
      'ignore_nonunique': True,
      'crawler': 'TwseCrawler.stock_code_js',
      'args': [],
      'schema': [
        ('type_id text', '?', 'key'),
        ('name text', '?'),
        ]
      }

  def run(self, args):
    return self.access_db(args)

  def check_update(self, db, last_args=None):
    if last_args is None:
      self.logger.info('Start refreshing stock types')
      return True, {}
    else:
      self.logger.info('End refreshing stock types')
      return False, {}

  def query_db(self, db, args):
    select_sql = "SELECT * FROM stock_types;"
    query_res = [r for r in db.execute(select_sql)]
    return query_res, False, {}
