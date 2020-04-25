import stocklab
from stocklab.datetime import date_to_timestamp

class suspended_stock_list(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'disable_cache': False,
      'ignore_existed': True,
      'crawler_entry': 'TwseCrawler.suspended_listing',
      'args': [],
      'schema': {
        'stock_id': {'key': True},
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp},
        }
      }

  def evaluate(self, db, args):
    retval = db(db[self.name]).select()
    return retval
