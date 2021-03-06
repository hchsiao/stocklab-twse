import stocklab
from stocklab.datetime import date_to_timestamp

class etf_stock_list(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'ignore_existed': True,
      'crawler_entry': 'TwseCrawler.etf_listing',
      'args': [],
      'schema': {
        'stock_id': {'key': True},
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp},
        }
      }

  def evaluate(self, db, args):
    retval = db(db[self.name]).select()
    return retval
