from datetime import datetime, timedelta
import stocklab
import calendar

def set_last_update_datetime(mod_name):
  last_update_time = datetime.now()
  tstmp = calendar.timegm(last_update_time.timetuple())
  stocklab.set_state(f'{mod_name}__t_last_update', str(tstmp))

def last_update_datetime(mod_name):
  t_last_update = stocklab.get_state(f'{mod_name}__t_last_update')
  if t_last_update:
    return datetime.utcfromtimestamp(int(t_last_update))
  else:
    return None

def is_outdated_since_last_update(mod_name, threshold_minute):
  last_update = last_update_datetime(mod_name)
  if last_update:
    threshold = timedelta(minutes=threshold_minute)
    time_elapsed = datetime.now() - last_update
    return time_elapsed > threshold
  else:
    return True
