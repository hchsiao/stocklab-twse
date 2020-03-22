import stocklab

class stocks(stocklab.MetaModule):
  spec = {
      'update_threshold': 1440,
      'ignore_nonunique': True,
      'crawler': 'TwseCrawler.stock_codes',
      'args': [
        ('mode', ['get', 'count']),
        ('type_id', str),
        ('id', int),
        ],
      'schema': [
        ('type_id text', '?', 'key'),
        ('id integer', '?', 'key'),
        ('stock_id text', '?'),
        ('name text', '?'),
        ]
      }

  def run(self, args):
    return self.access_db(args)

  def check_update(self, db, last_args=None):
    if last_args is None:
      self.logger.info('Start updating stock list')
      types = stocklab.metaevaluate('stock_types')
      return True, {'targets': types}
    else:
      self.logger.info('End updating stock list')
      return False, {}

  def query_db(self, db, args):
    types = stocklab.metaevaluate('stock_types')
    targets = [t for t in types if t[0] == args.type_id]
    if args.mode == 'count':
      assert args.id == None
      select_sql = "SELECT COUNT(type_id) AS cnt FROM stocks WHERE type_id=?;"
      query_res = [r for r in db.execute(select_sql, (args.type_id,))]
      return query_res[0][0], False, {}
    elif args.mode == 'get':
      assert len(targets) == 1
      select_sql = "SELECT * FROM stocks WHERE type_id=? AND id=?;"
      query_res = [r for r in db.execute(select_sql, (args.type_id, args.id))]
      type_id = targets[0][0]
      type_name = targets[0][1]
      stock_id = query_res[0][2]
      stock_name = query_res[0][3]
      return (stock_id, stock_name, type_name), False, {}
