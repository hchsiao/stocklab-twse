import stocklab

class stocks(stocklab.MetaModule):
  spec = {
      'args': ['stocks_str'],
      }

  def evaluate(self, db, args):
    return args.stocks_str.split('|')
