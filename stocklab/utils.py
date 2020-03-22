from datetime import datetime, timedelta
import stocklab

def set_last_update_datetime(mod_name):
  last_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  stocklab.set_state(f'{mod_name}__t_last_update', last_update_time, fmt="strftime('%s', ?)")

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
