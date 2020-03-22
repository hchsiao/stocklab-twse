from stocklab.date import Date

class ExceptionWithInfo(Exception):
  def __init__(self, message, info):
    super().__init__(message)
    self.info = info

  def __str__(self):
    return f'{super().__str__()} {str(self.info)}'

class InvalidDateRequested(ExceptionWithInfo):
  pass

class NoLongerAvailable(Exception):
  pass

class ParserError(ExceptionWithInfo):
  pass
