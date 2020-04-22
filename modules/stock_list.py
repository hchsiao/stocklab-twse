import stocklab

class stock_list(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'ignore_existed': True,
      'crawler_entry': 'TwseCrawler.stock_list',
      'args': [],
      'schema': {
        'stock_id': {'key': True},
        'name': {},
        }
      }

  def evaluate(self, db, args):
    retval = db(db[self.name]).select()
    return retval
