import abc

import logging

import stocklab
class Crawler(metaclass=abc.ABCMeta):
  def __init__(self):
    self.name = type(self).__name__
    self.logger = logging.getLogger(self.name)

    log_handler = logging.StreamHandler()
    log_format = logging.Formatter(
        f"[%(levelname)s] {self.name}: %(message)s"
        )
    log_handler.setFormatter(log_format)
    self.logger.addHandler(log_handler)
    self.logger.setLevel(stocklab.log_level)
