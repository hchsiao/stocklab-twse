import time
import stocklab

class SpeedLimiterMixin(object):
  def __init__(self):
    assert isinstance(self, stocklab.Crawler)
    super().__init__()
    self.last_req = None

  def speed(self):
    if self.last_req is None:
      return 0.0
    now = time.time()
    return 1.0 / (now - self.last_req)

  def speed_limited_request(self, request_cb, *args, **kwargs):
    speed = self.speed()
    while self.speed() > self.spec['max_speed']:
      time.sleep(self.spec['tick_period'])
      speed = self.speed()
    retval = request_cb(*args, **kwargs)
    self.logger.debug(f'Request sent, speed={speed}')
    self.last_req = time.time()
    return retval


class RetryMixin(object):
  def __init__(self):
    assert isinstance(self, stocklab.Crawler)
    super().__init__()

  def retry_when_failed(self, do_cb, success_cb, error_cb):
    for nth_try in range(self.spec['retry_limit'] + 1):
      res = do_cb()
      if success_cb(res):
        return res
      self.logger.info('got wrong data, waiting for retry')
      time.sleep(self.spec['retry_period'])
    raise error_cb(res)
