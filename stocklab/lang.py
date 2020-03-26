import stocklab

class Expr:
  def __init__(self, argv=[], meta=False):
    self.argv = argv
    self.meta = meta
    if argv:
      self.module = stocklab.get_module(argv[0])
      self.arg_len = len(self.module.spec['args'])
    else:
      self.module = None
      self.arg_len = None

  def __getattr__(self, attr):
    attr = str(attr)
    if attr[-1] == '_':
      return None # to ignore things like: ipython_canary_method_should_not_exist_

    new_argv = self.argv + [attr.lstrip('_')]
    new_expr = Expr(new_argv, meta=self.meta)
    if self.arg_len and self.arg_len == len(self.argv):
      if self.meta:
        return stocklab.metaevaluate(str(new_expr))
      else:
        return stocklab.evaluate(str(new_expr))
    else:
      return new_expr

  def __getitem__(self, key):
    return self.__getattr__(key)

  def __str__(self):
    if not self.module:
      return ''
    else:
      arg_spec = self.module.spec['args']
      arg_spec = [(a, str) if type(a) is str else a for a in arg_spec]
      arg_names = [f'<field: {a[0]}>' for a in arg_spec]
      arg_types = [a[1] for a in arg_spec]
      return '.'.join(self.argv + arg_names[len(self.argv) - 1:])

  def __repr__(self):
    return self.__str__()

expr = Expr()
meta = Expr(meta=True)
