import stocklab
from stocklab.datetime import Date, date_to_timestamp

class last_trade_date(stocklab.MetaModule):
  spec = {
      'update_offset': (9, 0),
      'update_existed': True,
      'crawler_entry': 'TwseCrawler.last_trade_date',
      'args': [],
      'schema': {
        'date': {'type': 'integer', 'pre_proc': date_to_timestamp},
        'dummy_id': {'key': True},
        }
      }

  def evaluate(self, db, args):
    rows = db(db[self.name]).select()
    return Date(rows[0].date, tstmp=True)
