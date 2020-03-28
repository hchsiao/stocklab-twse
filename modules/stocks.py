import stocklab

class stocks(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'ignore_existed': True,
      'crawler': 'TwseCrawler.stock_codes',
      'args': [
        ('mode', ['get', 'count']),
        ('type_id', str),
        ('internal_id', int),
        ],
      'schema': {
        'type_id': {'key': True},
        'internal_id': {'type': 'integer', 'key': True},
        'stock_id': {},
        'name': {},
        }
      }

  def run(self, args):
    return self.access_db(args)

  def check_update(self, db, last_args=None):
    if last_args is None:
      self.logger.info('Start updating stock list')
      types = [(row.type_id, row.name) for row in stocklab.metaevaluate('stock_types')]
      return True, {'targets': types}
    else:
      self.logger.info('End updating stock list')
      return False, {}

  def query_db(self, db, args):
    table = db[self.name]
    if args.mode == 'count':
      assert args.internal_id == None
      query = table.type_id == args.type_id
      retval = db(query).count()
      return retval, False, {}
    elif args.mode == 'get':
      type_rows = stocklab.metaevaluate('stock_types')
      targets = [row for row in type_rows if row.type_id == args.type_id]
      assert len(targets) == 1
      query = table.type_id == args.type_id
      query &= table.internal_id == args.internal_id
      retval = db(query).select()
      type_id = targets[0].type_id
      type_name = targets[0].name
      stock_id = retval[0].stock_id
      stock_name = retval[0].name
      return (stock_id, stock_name, type_name), False, {}
